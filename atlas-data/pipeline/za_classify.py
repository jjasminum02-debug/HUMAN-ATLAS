"""Z-Anatomy object classification. Pure Python: no Blender, so it can be tested directly.

Input per mesh object: source name, numbered top collection, Bonus collection paths, parent name.
Output: system/kind/side/region, or an exclusion reason. Rules use ZA's own collections first and
name keywords only as a fallback inside a collection.
"""
import re

# ZA name suffixes. Label leader lines (.j/.i/.t/.s) and whole-system aggregates (.g) are not anatomy.
SIDED = {'l': 'left', 'r': 'right'}
ATTACHMENT_SUFFIX = re.compile(r'^([oe])(\d*)([lr]?)$')  # .ol/.er, numbered patches .o5r/.e25l, unsided .o1
NON_ANATOMY = {'j', 'i', 't', 's', 'g'}

SENSE_WORDS = (r'eye|retina|sclera|lens|iris|cornea|vitreous|zonular|choroid|ciliary|pupil|auditory|cochlea|tympan|'
               r'labyrinth|semicircular|utricle|saccule|vestibul|lacrimal|conjunctiva|eyelid|tarsus|ear\b|auricle|nasal|olfactory|tongue|taste')

TOP = {'1': 'skeletal', '2': 'attachment', '3': 'joint', '4': 'muscular', '5': 'cardiovascular', '7': 'nervous'}
EXTRACTED_TOPS = {'1', '2', '3', '4', '7'}

REGIONS = {'Head': 'head', 'Neck': 'neck', 'Trunk': 'trunk', 'upper limb': 'upper_limb', 'hand': 'hand',
           'lower limb': 'lower_limb', 'foot': 'foot'}


def split_name(name):
    match = re.search(r'\.([oe]\d*[lr]?|[a-z]{1,2})$', name)
    suffix = match.group(1) if match else ''
    base = name[:match.start()] if match else name
    parenthesized = base.startswith('(') and base.endswith(')')
    return (base[1:-1] if parenthesized else base), suffix, parenthesized


def slug(text):
    # Keep the prime mark: ZA has distinct objects such as "Central canal" and "Central canal'".
    return re.sub(r'[^a-z0-9]+', '-', text.lower().replace("'", ' prime')).strip('-')


def _has(paths, label):
    return any(label in part for path in paths for part in path)


def _joint_kind(n):
    if 'labrum' in n: return 'labrum'
    if 'menisc' in n and 'ligament' not in n: return 'meniscus'
    if 'nucleus pulposus' in n or 'anulus fibrosus' in n or 'annulus fibrosus' in n or re.search(r'\bdiscs?\b', n): return 'disc'
    if 'capsul' in n: return 'capsule'
    if 'fat pad' in n or 'fat body' in n: return 'fat_pad'
    if 'symphysis' in n or 'synchondrosis' in n: return 'cartilaginous_joint'
    if 'membrane' in n: return 'membrane'
    if 'cartilage' in n: return 'cartilage'
    if 'bursa' in n: return 'bursa'
    if re.search(r'ligament|\bcord\b|\bband\b|\bligamenta\b|zona orbicularis', n): return 'ligament'
    if 'suture' in n or 'syndesmosis' in n or 'gomphosis' in n: return 'fibrous_joint'
    if 'joint' in n: return 'joint'
    return None


def _muscular_kind(n, paths):
    if _has(paths, 'Fascia'): return 'fascia'
    if _has(paths, 'Bursae'): return 'bursa'
    if _has(paths, 'Tendon sheaths'): return 'sheath'
    if 'retinacul' in n: return 'retinaculum'
    if 'septum' in n: return 'septum'
    if 'aponeuros' in n: return 'aponeurosis'
    if 'sheath' in n: return 'sheath'
    if 'bursa' in n: return 'bursa'
    if 'fascia' in n and 'tensor fasciae' not in n: return 'fascia'
    if 'linea alba' in n or 'raphe' in n: return 'raphe'
    if re.search(r'\btendons?\b|tendinous (arch|ring)', n): return 'tendon'
    if re.search(r'\btract\b', n): return 'fascia'  # iliotibial tract: thickened fascia lata
    if 'ligament' in n: return 'ligament'
    if re.search(r'\btarsus\b|trochlea of', n): return 'connective'  # eyelid tarsal plates, oblique-muscle pulley
    return 'muscle'


def _nervous_kind(n, paths):
    if _has(paths, 'Peripheral nervous system'): return 'nerve'
    if _has(paths, 'Sense organs'): return 'sense_organ'
    if _has(paths, 'Central nervous system'): return 'cns'
    if re.search(r'nerve|plexus|ganglion|ramus|branch|trunk', n): return 'nerve'
    if re.search(SENSE_WORDS, n): return 'sense_organ'
    if re.search(r'nucleus|tract|fasciculus|medulla|spinal cord|horn of|central canal|substance|reticular|brain|cerebr|cortex', n): return 'cns'
    return None


def classify(name, top, bonus_paths, parent=None):
    """Return a dict with either `exclude` (reason) or the structure classification."""
    base, suffix, parenthesized = split_name(name)
    top_key = top.split(':')[0]
    if suffix in NON_ANATOMY:
        return {'exclude': 'label_or_aggregate_suffix_.' + suffix}
    if top_key not in EXTRACTED_TOPS:
        return {'exclude': 'collection_out_of_scope_' + TOP.get(top_key, top_key)}
    n = base.lower()
    out = {'name': base, 'parenthesized': parenthesized, 'system': TOP[top_key]}
    attachment = ATTACHMENT_SUFFIX.match(suffix) if top_key == '2' else None
    if attachment:
        out['kind'] = 'origin' if attachment.group(1) == 'o' else 'insertion'
        out['side'] = SIDED.get(attachment.group(3), 'unpaired')
        out['patch'] = int(attachment.group(2)) if attachment.group(2) else None
        out['muscle'] = base
        out['bone'] = parent
    else:
        out['side'] = SIDED.get(suffix, 'unpaired')
        if top_key == '1':
            if _has(bonus_paths, 'Teeth') or re.search(r'incisor|canine|premolar|molar', n): out['kind'] = 'tooth'
            elif _has(bonus_paths, 'Cartilages') or _has(bonus_paths, 'Costal cartilages') or 'cartilage' in n: out['kind'] = 'cartilage'
            elif re.search(r'\bcells of\b|\bsinus\b', n): out['kind'] = 'cavity'  # air cells, paranasal sinuses
            else: out['kind'] = 'bone'
        elif top_key == '2':
            out['kind'] = None  # attachment collection without an attachment suffix
        elif top_key == '3':
            out['kind'] = _joint_kind(n)
        elif top_key == '4':
            out['kind'] = _muscular_kind(n, bonus_paths)
        elif top_key == '7':
            out['kind'] = _nervous_kind(n, bonus_paths)
    regions = []
    for path in bonus_paths:
        if 'Main divisions' in path:
            division = path[path.index('Main divisions') + 1] if path.index('Main divisions') + 1 < len(path) else ''
            for label, region in REGIONS.items():
                if label in division and region not in regions: regions.append(region)
    out['regions'] = regions
    out['id'] = 'za:' + slug(name)
    return out
