"""Extract location-method cells from a two-column portfolio into private authoring input.

Never imports needling depths, reflections, photos or patient metadata into learner data.
This is an extraction/triage tool, not an anatomical validator or location compiler.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

HEADER = re.compile(r"^[\s‘’'\"“”]*(LU|LI|ST|SP|HT|SI|BL|KI|PC|TE|GB|LR|CV|GV)\s*(\d+)\s+(.+)")
COUNTS = dict(LU=11, LI=20, ST=45, SP=21, HT=9, SI=19, BL=67, KI=27, PC=9, TE=23, GB=44, LR=14, CV=24, GV=28)
# These identify sentences for author review, not final pose IDs, angles or model support.
CUES = {
    'arm_raise': r'(어깨|위팔|팔).{0,18}(들어|들라|벌리|외전)|거비',
    'elbow_flex': r'(팔꿉|팔꿈치|팔굽).{0,15}굽|손을.{0,12}가슴',
    'hand_close': r'주먹|손가락.{0,20}굽|깍지',
    'mouth_open': r'입을.{0,12}(벌|열)',
    'mouth_close': r'입을.{0,12}다물|입술.{0,12}다물|이를.{0,12}(악|깨물)',
    'neck_turn': r'고개.{0,15}돌|목.{0,12}돌',
    'neck_flex': r'고개.{0,15}숙',
    'knee_flex': r'무릎.{0,15}굽|다리를.{0,15}ㄱ',
    'hip_open': r'아빠다리|넙다리.{0,15}벌|양반다리',
    'ankle_or_toe': r'(발가락|발목|발을).{0,18}(굽|펴|안쪽|바깥)',
}

def methods(cells):
    return [row[1] for row in cells if len(row) > 1 and row[0] and row[1]
            and re.sub(r'\s+', '', row[0]) in {'탐혈과정', '취혈과정'}]

def consume(events, previous, page):
    """Carry the heading across a column/page boundary; never infer it from numbering."""
    result = []
    for _, kind, payload in sorted(events, key=lambda x: x[0]):
        if kind == 'heading':
            code, number, name = payload
            previous = {'code': code + number, 'nameRaw': name, 'headingPage': page}
        elif previous:
            bounds, text = payload
            compact = re.sub(r'\s+', ' ', text).strip()
            result.append({**previous, 'page': page, 'tableBounds': list(bounds),
                           'locationMethod': compact,
                           'postureCueCandidates': [key for key, rx in CUES.items() if re.search(rx, compact)],
                           'contentReview': 'pending', 'modelBinding': None})
        else:
            raise ValueError(f'Method table without a preceding heading on page {page}')
    return result, previous

def extract(pdf):
    import pdfplumber
    rows, previous = [], None
    with pdfplumber.open(pdf) as doc:
        for page_number, page in enumerate(doc.pages, 1):
            tables = page.find_tables()
            # Read down the left column, then down the right column, then next page.
            for x0, x1 in [(0, page.width / 2), (page.width / 2, page.width)]:
                events = []
                for line in page.crop((x0, 0, x1, page.height)).extract_text_lines():
                    match = HEADER.match(line['text'])
                    if match:
                        events.append((line['top'], 'heading', match.groups()))
                for table in tables:
                    if x0 <= table.bbox[0] < x1:
                        text = methods(table.extract())
                        if text:
                            events.append((table.bbox[1], 'table', (table.bbox, '\n'.join(text))))
                batch, previous = consume(events, previous, page_number)
                rows.extend(batch)
        page_count = len(doc.pages)
    expected = {f'{channel}{number}' for channel, count in COUNTS.items() for number in range(1, count + 1)}
    counts = Counter(row['code'] for row in rows)
    check = {'missingCodes': sorted(expected - counts.keys()), 'unexpectedCodes': sorted(counts.keys() - expected),
             'duplicates': {code: count for code, count in counts.items() if count != 1}}
    if any(check.values()):
        raise ValueError(json.dumps(check, ensure_ascii=False))
    summary = {'schemaVersion': 1, 'sourceSha256': hashlib.sha256(Path(pdf).read_bytes()).hexdigest(),
               'pageCount': page_count, 'recordCount': len(rows), 'uniqueCodes': len(counts),
               'channelCounts': COUNTS, 'codeCoverage': check,
               'excludedSections': ['규격/자침깊이', '느낀점', '사진', '개인정보'],
               'postureCueRecordCount': sum(bool(row['postureCueCandidates']) for row in rows),
               'clinicalAccuracyValidated': False, 'learnerImported': 0, 'poseAssetsBound': 0}
    return summary, rows

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf', type=Path, required=True)
    parser.add_argument('--private-output', type=Path, required=True)
    parser.add_argument('--summary', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    if not args.private_output.resolve().is_relative_to(root / 'private-sources'):
        parser.error('Extracted portfolio text must stay under the ignored private-sources directory.')
    summary, rows = extract(args.pdf)
    args.private_output.mkdir(parents=True, exist_ok=True)
    (args.private_output / 'location-methods.json').write_text(json.dumps({'source': summary, 'rows': rows}, ensure_ascii=False, indent=2) + '\n')
    lines = ['# 취혈 위치·방법 대조용 원고', '', '추출본. 사실 검증·학습 화면 반영·자세 구현이 완료된 자료가 아님.', '']
    for row in rows:
        lines += [f"## {row['code']} — PDF {row['page']}쪽", '', row['locationMethod'], '',
                  f"자세 검토 후보: {', '.join(row['postureCueCandidates']) or '자동 검출 없음; 원문 검토 필요'}", '']
    (args.private_output / 'LOCATION-METHODS.md').write_text('\n'.join(lines))
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(summary, ensure_ascii=False))

if __name__ == '__main__':
    main()
