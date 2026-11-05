"""Korean names for Z-Anatomy vessels and heart parts (ROADMAP Q2-1), merged into names_ko.NAMES.

Same rules as names_ko.py: (우리말 koModern, 한자어 in Hangul koTraditional, basis). S = established 대한해부학회 term,
C = composed from KAA component terms. AI-written; verify_names_kmle.py checks every term against the KAA dictionary and
dictionary values replace the draft. ROOTS holds whole vessel names; vessel_name() composes the patterned ZA names
(left/right, '... of left lung', '... branch(es) of <vessel>', MCA segments).
"""
import re

ROOTS = {
    # Aorta and great vessels
    'Ascending aorta': ('오름대동맥', '상행대동맥', 'S'), 'Aortic arch': ('대동맥활', '대동맥궁', 'S'),
    'Thoracic aorta': ('가슴대동맥', '흉대동맥', 'S'), 'Abdominal aorta': ('배대동맥', '복대동맥', 'S'),
    'Brachiocephalic trunk': ('팔머리동맥', '완두동맥', 'S'), 'Common carotid artery': ('온목동맥', '총경동맥', 'S'),
    'Subclavian artery': ('빗장밑동맥', '쇄골하동맥', 'S'), 'Subclavian vein': ('빗장밑정맥', '쇄골하정맥', 'S'),
    'Brachiocephalic vein': ('팔머리정맥', '완두정맥', 'S'), 'Superior vena cava': ('위대정맥', '상대정맥', 'S'),
    'Inferior vena cava (abdominal part)': ('아래대정맥 배부분', '하대정맥 복부', 'C'),
    'Inferior vena cava (thoracic part)': ('아래대정맥 가슴부분', '하대정맥 흉부', 'C'),
    'Pulmonary trunk': ('허파동맥줄기', '폐동맥간', 'S'), 'Bifurcation of pulmonary trunk': ('허파동맥줄기갈림', '폐동맥간분기', 'C'),
    'Pulmonary artery': ('허파동맥', '폐동맥', 'S'), 'Superior pulmonary vein': ('위허파정맥', '상폐정맥', 'S'),
    'Inferior pulmonary vein': ('아래허파정맥', '하폐정맥', 'S'),
    # Heart
    'Atrium': ('심방', '심방', 'S'), 'Ventricle': ('심실', '심실', 'S'),
    'Anterior papillary muscle of right ventricle': ('오른심실 앞꼭지근', '우심실 전유두근', 'C'),
    'Inferior papillary muscle of right ventricle': ('오른심실 아래꼭지근', '우심실 하유두근', 'C'),
    'Septal papillary muscle of right ventricle': ('오른심실 사이막꼭지근', '우심실 중격유두근', 'C'),
    'Inferior papillary muscle of left ventricle': ('왼심실 아래꼭지근', '좌심실 하유두근', 'C'),
    'Anterior semilunar leaflet of pulmonary valve': ('허파동맥판막 앞반달첨판', '폐동맥판 전반월첨', 'C'),
    'Left semilunar leaflet of pulmonary valve': ('허파동맥판막 왼반달첨판', '폐동맥판 좌반월첨', 'C'),
    'Right semilunar leaflet of pulmonary valve': ('허파동맥판막 오른반달첨판', '폐동맥판 우반월첨', 'C'),
    'Inferior leaflet of right atrioventricular valve': ('오른방실판막 아래첨판', '우방실판 하첨', 'C'),
    'Septal leaflet of right atrioventricular valve': ('오른방실판막 사이막첨판', '우방실판 중격첨', 'C'),
    'Posterior leaflet of left atrioventricular valve': ('왼방실판막 뒤첨판', '좌방실판 후첨', 'C'),
    'Left coronary leaflet': ('대동맥판막 왼관상첨판', '대동맥판 좌관상첨', 'C'),
    'Right coronary leaflet': ('대동맥판막 오른관상첨판', '대동맥판 우관상첨', 'C'),
    'Non-coronary leaflet': ('대동맥판막 비관상첨판', '대동맥판 무관상첨', 'C'),
    # Heart vessels
    'Coronary artery': ('관상동맥', '관상동맥', 'S'), 'Anterior interventricular artery': ('앞심실사이동맥', '전심실간동맥', 'S'),
    'Circumflex artery of heart': ('심장휘돌이동맥', '심장회선동맥', 'C'), 'Coronary sinus': ('심장정맥굴', '관상정맥동', 'S'),
    'Great cardiac vein': ('큰심장정맥', '대심정맥', 'S'), 'Middle cardiac vein': ('중간심장정맥', '중심정맥', 'S'),
    'Inferior vein of left ventricle': ('왼심실아래정맥', '좌심실하정맥', 'C'),
    "Inferior vein of left ventricle (//Posterior '')": ('왼심실아래정맥', '좌심실하정맥', 'C'),
    # Lung segments (composed with '... of left/right lung')
    'Superior lobar artery': ('위엽동맥', '상엽동맥', 'C'), 'Middle lobar artery': ('중간엽동맥', '중엽동맥', 'C'),
    'Inferior lobar artery': ('아래엽동맥', '하엽동맥', 'C'),
    'Apical segmental artery': ('꼭대기구역동맥', '첨구동맥', 'C'), 'Anterior segmental artery': ('앞구역동맥', '전구동맥', 'C'),
    'Posterior segmental artery': ('뒤구역동맥', '후구동맥', 'C'), 'Lateral segmental artery': ('가쪽구역동맥', '외측구동맥', 'C'),
    'Medial segmental artery': ('안쪽구역동맥', '내측구동맥', 'C'), 'Superior segmental artery': ('위구역동맥', '상구동맥', 'C'),
    'Anterior basal segmental artery': ('앞바닥구역동맥', '전폐저구동맥', 'C'), 'Lateral basal segmental artery': ('가쪽바닥구역동맥', '외측폐저구동맥', 'C'),
    'Medial basal segmental artery': ('안쪽바닥구역동맥', '내측폐저구동맥', 'C'), 'Posterior basal segmental artery': ('뒤바닥구역동맥', '후폐저구동맥', 'C'),
    'Superior lingular artery': ('위혀구역동맥', '상설구동맥', 'C'), 'Inferior lingular artery': ('아래혀구역동맥', '하설구동맥', 'C'),
    'Apical vein': ('꼭대기구역정맥', '첨구정맥', 'C'), 'Apicoposterior vein': ('꼭대기뒤구역정맥', '첨후구정맥', 'C'),
    'Anterior vein': ('앞구역정맥', '전구정맥', 'C'), 'Posterior vein': ('뒤구역정맥', '후구정맥', 'C'),
    'Lateral vein': ('가쪽구역정맥', '외측구정맥', 'C'), 'Medial vein': ('안쪽구역정맥', '내측구정맥', 'C'),
    'Superior vein': ('위구역정맥', '상구정맥', 'C'), 'Superior basal vein': ('위바닥정맥', '상폐저정맥', 'C'),
    'Inferior basal vein': ('아래바닥정맥', '하폐저정맥', 'C'), 'Lingular vein': ('혀구역정맥', '설구정맥', 'C'),
    'Superior lingular vein': ('위혀구역정맥', '상설구정맥', 'C'), 'Inferior lingular vein': ('아래혀구역정맥', '하설구정맥', 'C'),
    # Head and neck arteries
    'External carotid artery': ('바깥목동맥', '외경동맥', 'S'), 'Internal carotid artery': ('속목동맥', '내경동맥', 'S'),
    'Vertebral artery': ('척추동맥', '추골동맥', 'S'), 'Basilar artery': ('뇌바닥동맥', '뇌저동맥', 'S'),
    'Thyrocervical trunk': ('갑상목동맥줄기', '갑상경동맥간', 'S'), 'Costocervical trunk': ('갈비목동맥줄기', '늑경동맥간', 'S'),
    'Inferior thyroid artery': ('아래갑상동맥', '하갑상선동맥', 'S'), 'Transverse cervical artery': ('가로목동맥', '경횡동맥', 'S'),
    'Deep cervical artery': ('깊은목동맥', '심경동맥', 'S'), 'Supreme intercostal artery': ('맨위갈비사이동맥', '최상늑간동맥', 'S'),
    'Ascending pharyngeal artery': ('오름인두동맥', '상행인두동맥', 'S'), 'Facial artery': ('얼굴동맥', '안면동맥', 'S'),
    'Submental artery': ('턱끝밑동맥', '이하동맥', 'S'), 'Superior labial artery': ('윗입술동맥', '상순동맥', 'S'),
    'Inferior labial artery': ('아랫입술동맥', '하순동맥', 'S'), 'Angular artery': ('눈구석동맥', '안각동맥', 'S'),
    'Occipital artery': ('뒤통수동맥', '후두동맥', 'S'), 'Superficial temporal artery': ('얕은관자동맥', '천측두동맥', 'S'),
    'Transverse facial artery': ('얼굴가로동맥', '안면횡동맥', 'S'), 'Maxillary artery': ('위턱동맥', '상악동맥', 'S'),
    'Middle meningeal artery': ('중간뇌막동맥', '중경막동맥', 'S'), 'Inferior alveolar artery': ('아래이틀동맥', '하치조동맥', 'S'),
    'Anterior deep temporal artery': ('앞깊은관자동맥', '전심측두동맥', 'S'), 'Posterior deep temporal artery': ('뒤깊은관자동맥', '후심측두동맥', 'S'),
    'Buccal artery': ('볼동맥', '협동맥', 'S'), 'Posterior superior alveolar artery': ('뒤위이틀동맥', '후상치조동맥', 'S'),
    'Infra-orbital artery': ('눈확아래동맥', '안와하동맥', 'S'), 'Descending palatine artery': ('내림입천장동맥', '하행구개동맥', 'S'),
    'Greater palatine artery': ('큰입천장동맥', '대구개동맥', 'S'), 'Artery of pterygoid canal': ('날개관동맥', '익돌관동맥', 'S'),
    'Sphenopalatine artery': ('나비입천장동맥', '접형구개동맥', 'S'), 'Ophthalmic artery': ('눈동맥', '안동맥', 'S'),
    'Central retinal artery': ('망막중심동맥', '망막중심동맥', 'S'), 'Lacrimal artery': ('눈물샘동맥', '누선동맥', 'S'),
    'Supra-orbital artery': ('눈확위동맥', '안와상동맥', 'S'), 'Supratrochlear artery': ('도르래위동맥', '활차상동맥', 'S'),
    'Anterior ethmoidal artery': ('앞벌집동맥', '전사골동맥', 'S'), 'Posterior ethmoidal artery': ('뒤벌집동맥', '후사골동맥', 'S'),
    'Long posterior ciliary arteries': ('긴뒤섬모체동맥', '장후모양체동맥', 'S'), 'Short posterior ciliary arteries': ('짧은뒤섬모체동맥', '단후모양체동맥', 'S'),
    # Brain arteries
    'Anterior cerebral artery': ('앞대뇌동맥', '전대뇌동맥', 'S'), 'Middle cerebral artery': ('중간대뇌동맥', '중대뇌동맥', 'S'),
    'Posterior cerebral artery': ('뒤대뇌동맥', '후대뇌동맥', 'S'), 'Anterior communicating artery': ('앞교통동맥', '전교통동맥', 'S'),
    'Posterior communicating artery': ('뒤교통동맥', '후교통동맥', 'S'), 'Superior cerebellar artery': ('위소뇌동맥', '상소뇌동맥', 'S'),
    'Anterior inferior cerebellar artery': ('앞아래소뇌동맥', '전하소뇌동맥', 'S'), 'Posterior inferior cerebellar artery': ('뒤아래소뇌동맥', '후하소뇌동맥', 'S'),
    'Anterior spinal artery': ('앞척수동맥', '전척수동맥', 'S'), 'Callosomarginal artery': ('뇌들보모서리동맥', '뇌량연동맥', 'S'),
    'Pericallosal artery': ('뇌들보주위동맥', '뇌량주위동맥', 'S'), 'Lateral frontobasal artery': ('가쪽이마바닥동맥', '외측전두저동맥', 'C'),
    'Prefrontal artery': ('이마앞동맥', '전전두동맥', 'C'), 'Artery of precentral sulcus': ('중심앞고랑동맥', '중심전구동맥', 'S'),
    'Artery of central sulcus': ('중심고랑동맥', '중심구동맥', 'S'), 'Postcentral arterial branch': ('중심뒤고랑동맥', '중심후구동맥', 'C'),
    'Posterior parietal artery': ('뒤마루동맥', '후두정동맥', 'C'), 'Branch to angular gyrus': ('모이랑가지', '각회지', 'C'),
    'Temporo-occipital branch': ('관자뒤통수가지', '측두후두지', 'C'), 'Anterior temporal branch': ('앞관자가지', '전측두지', 'C'),
    'Posterior temporal branch': ('뒤관자가지', '후측두지', 'C'), 'Parieto-occipital artery': ('마루뒤통수동맥', '두정후두동맥', 'C'),
    'Lateral occipital artery': ('가쪽뒤통수동맥', '외측후두동맥', 'S'), 'Medial occipital artery': ('안쪽뒤통수동맥', '내측후두동맥', 'S'),
    'Distal lateral striate branches': ('먼쪽가쪽줄무늬체가지', '원위외측선조체지', 'C'),
    'Proximal lateral striate branches': ('몸쪽가쪽줄무늬체가지', '근위외측선조체지', 'C'),
    # Head and neck veins and dural sinuses
    'Internal jugular vein': ('속목정맥', '내경정맥', 'S'), 'External jugular vein': ('바깥목정맥', '외경정맥', 'S'),
    'Anterior jugular vein': ('앞목정맥', '전경정맥', 'S'), 'Vertebral vein': ('척추정맥', '추골정맥', 'S'),
    'Facial vein': ('얼굴정맥', '안면정맥', 'S'), 'Common facial vein': ('온얼굴정맥', '총안면정맥', 'S'),
    'Angular vein': ('눈구석정맥', '안각정맥', 'S'), 'Retromandibular vein': ('아래턱뒤정맥', '하악후정맥', 'S'),
    'Superficial temporal veins': ('얕은관자정맥', '천측두정맥', 'S'), 'Maxillary veins': ('위턱정맥', '상악정맥', 'S'),
    'Posterior auricular vein': ('뒤귀정맥', '후이개정맥', 'S'), 'Occipital vein': ('뒤통수정맥', '후두정맥', 'S'),
    'Lingual vein': ('혀정맥', '설정맥', 'S'), 'Submental vein': ('턱끝밑정맥', '이하정맥', 'S'),
    'Superior labial vein': ('윗입술정맥', '상순정맥', 'S'), 'Inferior labial veins': ('아랫입술정맥', '하순정맥', 'S'),
    'Superior thyroid vein': ('위갑상정맥', '상갑상선정맥', 'S'), 'Superior ophthalmic vein': ('위눈정맥', '상안정맥', 'S'),
    'Inferior ophthalmic vein': ('아래눈정맥', '하안정맥', 'S'),
    'Superior sagittal sinus': ('위시상정맥굴', '상시상정맥동', 'S'), 'Inferior sagittal sinus': ('아래시상정맥굴', '하시상정맥동', 'S'),
    'Straight sinus': ('곧은정맥굴', '직정맥동', 'S'), 'Transverse sinus': ('가로정맥굴', '횡정맥동', 'S'),
    'Sigmoid sinus': ('구불정맥굴', 'S상정맥동', 'S'), 'Occipital sinus': ('뒤통수정맥굴', '후두정맥동', 'S'),
    'Cavernous sinus': ('해면정맥굴', '해면정맥동', 'S'), 'Superior petrosal sinus': ('위바위정맥굴', '상추체정맥동', 'S'),
    'Inferior petrosal sinus': ('아래바위정맥굴', '하추체정맥동', 'S'), 'Anterior intercavernous sinus': ('앞해면사이정맥굴', '전해면간정맥동', 'S'),
    'Posterior intercavernous sinus': ('뒤해면사이정맥굴', '후해면간정맥동', 'S'), 'Basilar venous plexus': ('뇌바닥정맥얼기', '뇌저정맥총', 'C'),
    # Upper limb
    'Axillary artery': ('겨드랑동맥', '액와동맥', 'S'), 'Axillary vein': ('겨드랑정맥', '액와정맥', 'S'),
    'Thoraco-acromial artery': ('가슴봉우리동맥', '흉견봉동맥', 'S'), 'Lateral thoracic artery': ('가쪽가슴동맥', '외측흉동맥', 'S'),
    'Lateral thoracic vein': ('가쪽가슴정맥', '외측흉정맥', 'S'), 'Subscapular artery': ('어깨밑동맥', '견갑하동맥', 'S'),
    'Subscapular vein': ('어깨밑정맥', '견갑하정맥', 'S'), 'Circumflex scapular artery': ('어깨휘돌이동맥', '견갑회선동맥', 'S'),
    'Circumflex scapular vein': ('어깨휘돌이정맥', '견갑회선정맥', 'S'), 'Thoracodorsal artery': ('가슴등동맥', '흉배동맥', 'S'),
    'Thoracodorsal vein': ('가슴등정맥', '흉배정맥', 'S'), 'Suprascapular artery': ('어깨위동맥', '견갑상동맥', 'S'),
    'Suprascapular vein': ('어깨위정맥', '견갑상정맥', 'S'),
    'Anterior circumflex humeral artery': ('앞위팔휘돌이동맥', '전상완회선동맥', 'S'), 'Anterior circumflex humeral vein': ('앞위팔휘돌이정맥', '전상완회선정맥', 'S'),
    'Posterior circumflex humeral artery': ('뒤위팔휘돌이동맥', '후상완회선동맥', 'S'), 'Posterior circumflex humeral vein': ('뒤위팔휘돌이정맥', '후상완회선정맥', 'S'),
    'Brachial artery': ('위팔동맥', '상완동맥', 'S'), 'Brachial veins': ('위팔정맥', '상완정맥', 'S'),
    'Deep brachial artery': ('깊은위팔동맥', '상완심동맥', 'S'), 'Middle collateral artery': ('중간곁동맥', '중측부동맥', 'S'),
    'Radial collateral artery': ('노쪽곁동맥', '요측측부동맥', 'S'), 'Superior ulnar collateral artery': ('위자쪽곁동맥', '상척측측부동맥', 'S'),
    'Inferior ulnar collateral artery': ('아래자쪽곁동맥', '하척측측부동맥', 'S'),
    'Radial artery': ('노동맥', '요골동맥', 'S'), 'Radial veins': ('노정맥', '요골정맥', 'S'),
    'Ulnar artery': ('자동맥', '척골동맥', 'S'), 'Ulnar veins': ('자정맥', '척골정맥', 'S'),
    'Ulnar recurrent artery': ('자쪽되돌이동맥', '척측반회동맥', 'S'), 'Common interosseous artery': ('온뼈사이동맥', '총골간동맥', 'S'),
    'Posterior interosseous artery': ('뒤뼈사이동맥', '후골간동맥', 'S'), 'Recurrent interosseous artery': ('되돌이뼈사이동맥', '반회골간동맥', 'S'),
    'Superficial palmar arch': ('얕은손바닥동맥활', '천장동맥궁', 'S'), 'Deep palmar arch': ('깊은손바닥동맥활', '심장동맥궁', 'S'),
    'Superficial venous palmar arch': ('얕은손바닥정맥활', '천장정맥궁', 'S'), 'Deep venous palmar arch': ('깊은손바닥정맥활', '심장정맥궁', 'S'),
    'Common palmar digital arteries': ('온바닥쪽손가락동맥', '총장측지동맥', 'S'), 'Proper palmar digital arteries': ('고유바닥쪽손가락동맥', '고유장측지동맥', 'S'),
    'Palmar metacarpal arteries': ('바닥쪽손허리동맥', '장측중수동맥', 'S'), 'Dorsal metacarpal arteries': ('등쪽손허리동맥', '배측중수동맥', 'S'),
    'Dorsal digital arteries of hand': ('등쪽손가락동맥', '배측수지동맥', 'S'), 'Dorsal carpal anastomosis': ('등쪽손목문합', '배측수근문합', 'C'),
    'Palmar digital veins': ('바닥쪽손가락정맥', '장측지정맥', 'S'), 'Dorsal digital veins of hand': ('등쪽손가락정맥', '배측수지정맥', 'S'),
    'Dorsal venous network of hand': ('손등정맥그물', '수배정맥망', 'S'), 'Cephalic vein': ('노쪽피부정맥', '요측피정맥', 'S'),
    'Basilic vein': ('자쪽피부정맥', '척측피정맥', 'S'), 'Median cubital vein': ('팔오금중간정맥', '주정중피정맥', 'S'),
    'Median antebrachial vein': ('아래팔중간피부정맥', '전완정중피정맥', 'S'),
    # Thorax and abdominal wall
    'Internal thoracic artery': ('속가슴동맥', '내흉동맥', 'S'), 'Internal thoracic veins': ('속가슴정맥', '내흉정맥', 'S'),
    'Musculophrenic artery': ('근육가로막동맥', '근횡격동맥', 'S'), 'Musculophrenic veins': ('근육가로막정맥', '근횡격정맥', 'S'),
    'Superior epigastric artery': ('위배벽동맥', '상복벽동맥', 'S'), 'Superior epigastric veins': ('위배벽정맥', '상복벽정맥', 'S'),
    'Inferior epigastric artery': ('아래배벽동맥', '하복벽동맥', 'S'), 'Inferior epigastric vein': ('아래배벽정맥', '하복벽정맥', 'S'),
    'Superficial epigastric artery': ('얕은배벽동맥', '천복벽동맥', 'S'), 'Superficial epigastric vein': ('얕은배벽정맥', '천복벽정맥', 'S'),
    'Posterior intercostal arteries': ('뒤갈비사이동맥', '후늑간동맥', 'S'),
    'First posterior intercostal artery': ('첫째뒤갈비사이동맥', '제1후늑간동맥', 'C'), 'Second posterior intercostal artery': ('둘째뒤갈비사이동맥', '제2후늑간동맥', 'C'),
    'Superior intercostal vein': ('위갈비사이정맥', '상늑간정맥', 'S'), 'Subcostal artery': ('갈비밑동맥', '늑하동맥', 'S'),
    'Subcostal vein': ('갈비밑정맥', '늑하정맥', 'S'), 'Superior phrenic arteries': ('위가로막동맥', '상횡격동맥', 'S'),
    'Superior phrenic vein': ('위가로막정맥', '상횡격정맥', 'S'), 'Inferior phrenic artery': ('아래가로막동맥', '하횡격동맥', 'S'),
    'Azygos vein': ('홀정맥', '기정맥', 'S'), 'Hemi-azygos vein': ('반홀정맥', '반기정맥', 'S'), 'Accessory hemi-azygos vein': ('덧반홀정맥', '부반기정맥', 'S'),
    'Lumbar arteries': ('허리동맥', '요동맥', 'S'), 'Lumbar veins': ('허리정맥', '요정맥', 'S'), 'Ascending lumbar vein': ('오름허리정맥', '상행요정맥', 'S'),
    # Abdominal viscera
    'Coeliac trunk': ('복강동맥', '복강동맥', 'S'), 'Left gastric artery': ('왼위동맥', '좌위동맥', 'S'),
    'Common hepatic artery': ('온간동맥', '총간동맥', 'S'), 'Proper hepatic artery': ('고유간동맥', '고유간동맥', 'S'),
    'Gastroduodenal artery': ('위샘창자동맥', '위십이지장동맥', 'S'), 'Splenic artery': ('지라동맥', '비장동맥', 'S'),
    'Splenic vein': ('지라정맥', '비장정맥', 'S'), 'Gastro-omental vein': ('위그물막정맥', '위대망정맥', 'S'),
    'Superior mesenteric artery': ('위창자간막동맥', '상장간막동맥', 'S'), 'Superior mesenteric vein': ('위창자간막정맥', '상장간막정맥', 'S'),
    'Inferior mesenteric artery': ('아래창자간막동맥', '하장간막동맥', 'S'), 'Inferior mesenteric vein': ('아래창자간막정맥', '하장간막정맥', 'S'),
    'Inferior pancreaticoduodenal artery': ('아래이자샘창자동맥', '하췌십이지장동맥', 'S'),
    'Anterior inferior pancreaticoduodenal artery': ('앞아래이자샘창자동맥', '전하췌십이지장동맥', 'S'),
    'Ileocolic artery': ('돌주름창자동맥', '회결장동맥', 'S'), 'Appendicular artery': ('막창자꼬리동맥', '충수동맥', 'S'),
    'Colic artery': ('잘록창자동맥', '결장동맥', 'S'), 'Colic vein': ('잘록창자정맥', '결장정맥', 'S'),
    'Middle colic artery': ('중간잘록창자동맥', '중결장동맥', 'S'), 'Middle colic vein': ('중간잘록창자정맥', '중결장정맥', 'S'),
    'Marginal artery': ('모서리동맥', '변연동맥', 'S'), 'Sigmoid arteries': ('구불창자동맥', 'S상결장동맥', 'S'),
    'Sigmoid veins': ('구불창자정맥', 'S상결장정맥', 'S'), 'Superior anorectal artery': ('위곧창자동맥', '상직장동맥', 'S'),
    'Hepatic portal vein': ('간문맥', '간문맥', 'S'), 'Hepatic veins': ('간정맥', '간정맥', 'S'),
    'Renal artery': ('콩팥동맥', '신동맥', 'S'), 'Renal vein': ('콩팥정맥', '신정맥', 'S'),
    'Intrarenal arteries': ('속동맥', '내동맥', 'C'), 'Intrarenal veins': ('속정맥', '내정맥', 'C'),  # '왼콩팥 속동맥'
    'Inferior suprarenal artery': ('아래부신동맥', '하부신동맥', 'S'), 'Testicular artery': ('고환동맥', '고환동맥', 'S'),
    'Testicular vein': ('고환정맥', '고환정맥', 'S'),
    # Pelvis
    'Common iliac artery': ('온엉덩동맥', '총장골동맥', 'S'), 'Common iliac vein': ('온엉덩정맥', '총장골정맥', 'S'),
    'Internal iliac artery': ('속엉덩동맥', '내장골동맥', 'S'), 'Internal iliac vein': ('속엉덩정맥', '내장골정맥', 'S'),
    'External iliac artery': ('바깥엉덩동맥', '외장골동맥', 'S'), 'External iliac vein': ('바깥엉덩정맥', '외장골정맥', 'S'),
    'Iliolumbar artery': ('엉덩허리동맥', '장요동맥', 'S'), 'Iliolumbar vein': ('엉덩허리정맥', '장요정맥', 'S'),
    'Median sacral artery': ('정중엉치동맥', '정중천골동맥', 'S'), 'Lateral sacral veins': ('가쪽엉치정맥', '외측천골정맥', 'S'),
    'Superior gluteal artery': ('위볼기동맥', '상둔동맥', 'S'), 'Superior gluteal veins': ('위볼기정맥', '상둔정맥', 'S'),
    'Inferior gluteal artery': ('아래볼기동맥', '하둔동맥', 'S'), 'Inferior gluteal veins': ('아래볼기정맥', '하둔정맥', 'S'),
    'Obturator artery': ('폐쇄동맥', '폐쇄동맥', 'S'), 'Internal pudendal artery': ('속음부동맥', '내음부동맥', 'S'),
    'Internal pudendal vein': ('속음부정맥', '내음부정맥', 'S'), 'Deep artery of penis': ('음경깊은동맥', '음경심동맥', 'S'),
    'Dorsal artery of penis': ('음경등동맥', '음경배동맥', 'S'), 'Deep dorsal vein of penis': ('깊은음경등정맥', '심음경배정맥', 'S'),
    'Superficial dorsal veins of penis': ('얕은음경등정맥', '천음경배정맥', 'S'),
    'Superficial external pudendal artery': ('얕은바깥음부동맥', '천외음부동맥', 'S'), 'Deep external pudendal artery': ('깊은바깥음부동맥', '심외음부동맥', 'S'),
    'External pudendal veins': ('바깥음부정맥', '외음부정맥', 'S'),
    # Lower limb
    'Femoral artery': ('넙다리동맥', '대퇴동맥', 'S'), 'Femoral vein': ('넙다리정맥', '대퇴정맥', 'S'),
    'Deep femoral artery': ('깊은넙다리동맥', '대퇴심동맥', 'S'), 'Deep femoral vein': ('깊은넙다리정맥', '대퇴심정맥', 'S'),
    'Perforating femoral arteries': ('관통동맥', '관통동맥', 'S'), 'Perforating veins': ('관통정맥', '관통정맥', 'S'),
    'Lateral circumflex femoral artery': ('가쪽넙다리휘돌이동맥', '외측대퇴회선동맥', 'S'),
    'Lateral circumflex femoral veins': ('가쪽넙다리휘돌이정맥', '외측대퇴회선정맥', 'S'),
    'Medial circumflex femoral artery': ('안쪽넙다리휘돌이동맥', '내측대퇴회선동맥', 'S'),
    'Medial circumflex femoral veins': ('안쪽넙다리휘돌이정맥', '내측대퇴회선정맥', 'S'),
    'Great saphenous vein': ('큰두렁정맥', '대복재정맥', 'S'), 'Small saphenous vein': ('작은두렁정맥', '소복재정맥', 'S'),
    'Popliteal artery': ('오금동맥', '슬와동맥', 'S'), 'Popliteal vein': ('오금정맥', '슬와정맥', 'S'),
    'Superior lateral genicular artery': ('가쪽위무릎동맥', '외측상슬동맥', 'S'), 'Superior medial genicular artery': ('안쪽위무릎동맥', '내측상슬동맥', 'S'),
    'Inferior lateral genicular artery': ('가쪽아래무릎동맥', '외측하슬동맥', 'S'), 'Inferior medial genicular artery': ('안쪽아래무릎동맥', '내측하슬동맥', 'S'),
    'Middle genicular artery': ('중간무릎동맥', '중슬동맥', 'S'), 'Genicular veins': ('무릎정맥', '슬정맥', 'S'),
    'Patellar anastomosis': ('무릎뼈문합', '슬개문합', 'C'),
    'Anterior tibial artery': ('앞정강동맥', '전경골동맥', 'S'), 'Anterior tibial veins': ('앞정강정맥', '전경골정맥', 'S'),
    'Posterior tibial artery': ('뒤정강동맥', '후경골동맥', 'S'), 'Posterior tibial veins': ('뒤정강정맥', '후경골정맥', 'S'),
    'Fibular artery': ('종아리동맥', '비골동맥', 'S'), 'Fibular veins': ('종아리정맥', '비골정맥', 'S'),
    'Dorsalis pedis artery': ('발등동맥', '족배동맥', 'S'), 'Lateral tarsal artery': ('가쪽발목동맥', '외측족근동맥', 'S'),
    'Arcuate artery': ('활꼴동맥', '궁상동맥', 'S'), 'Deep plantar artery': ('깊은발바닥동맥', '심족저동맥', 'S'),
    'Dorsal metatarsal arteries': ('등쪽발허리동맥', '배측중족동맥', 'S'), 'Dorsal metatarsal veins': ('등쪽발허리정맥', '배측중족정맥', 'S'),
    'Dorsal digital arteries of foot': ('등쪽발가락동맥', '배측족지동맥', 'S'), 'Dorsal digital veins of foot': ('등쪽발가락정맥', '배측족지정맥', 'S'),
    'Dorsal venous arch of foot': ('발등정맥활', '족배정맥궁', 'S'),
    'Medial plantar artery': ('안쪽발바닥동맥', '내측족저동맥', 'S'), 'Medial plantar veins': ('안쪽발바닥정맥', '내측족저정맥', 'S'),
    'Lateral plantar artery': ('가쪽발바닥동맥', '외측족저동맥', 'S'), 'Lateral plantar veins': ('가쪽발바닥정맥', '외측족저정맥', 'S'),
    'Plantar arch': ('발바닥동맥활', '족저동맥궁', 'S'), 'Plantar venous arch': ('발바닥정맥활', '족저정맥궁', 'S'),
    'Plantar metatarsal arteries': ('바닥쪽발허리동맥', '족저중족동맥', 'S'), 'Plantar metatarsal veins': ('바닥쪽발허리정맥', '족저중족정맥', 'S'),
    'Common plantar digital arteries': ('온바닥쪽발가락동맥', '총족저지동맥', 'S'), 'Proper plantar digital arteries': ('고유바닥쪽발가락동맥', '고유족저지동맥', 'S'),
    'Plantar digital veins': ('바닥쪽발가락정맥', '족저지정맥', 'S'), 'Intercapitular veins of foot': ('발머리사이정맥', '족두간정맥', 'C'),
}

# '<adjective> branch(es) of <vessel>' -> '<vessel> <adjective>가지' / '<vessel> <adjective>지'.
BRANCH = {
    'Accessory': ('덧', '부'), 'Anterior': ('앞', '전'), 'Posterior': ('뒤', '후'), 'Ascending': ('오름', '상행'), 'Descending': ('내림', '하행'),
    'Deep': ('깊은', '심'), 'Superficial': ('얕은', '천'), 'Colic': ('잘록창자', '결장'), 'Ileal': ('돌창자', '회장'), 'Iliacus': ('엉덩근', '장골근'),
    'Lumbar': ('허리', '요'), 'Spinal': ('척수', '척수'), 'Mental': ('턱끝', '이'), 'Mylohyoid': ('턱목뿔근', '악설골근'), 'Frontal': ('이마', '전두'),
    'Calcaneal': ('발꿈치', '종골'), 'Dorsal carpal': ('등쪽손목', '배측수근'), 'Palmar carpal': ('바닥쪽손목', '장측수근'), 'Pectoral': ('가슴근', '흉근'),
    'Perforating': ('관통', '관통'), 'Insular': ('섬', '도'), 'Parietal': ('마루', '두정'), 'Temporal': ('관자', '측두'),
    'Orbitofrontal': ('눈확이마', '안와전두'), 'Septal': ('사이막', '중격'), 'Anterior septal': ('앞사이막', '전중격'), 'Posterior septal': ('뒤사이막', '후중격'),
    'Posterior lateral nasal': ('뒤가쪽코', '후외측비'), 'Lateral pontine': ('가쪽다리뇌', '외측교뇌'), 'Medial pontine': ('안쪽다리뇌', '내측교뇌'),
    'Right inferolateral': ('오른아래가쪽', '우하외측'),
}


def vessel_name(name):
    """(koModern, koTraditional, basis) for a ZA vessel or heart name, or None."""
    found = _compose(name)
    if not found: return None
    modern, traditional, basis = found
    # KAA forms seen in the dictionary-checked vessel names: 정맥동굴 (dural sinuses), 주름창자 (colic), 위오른허파정맥.
    modern = modern.replace('정맥굴', '정맥동굴').replace('잘록창자', '주름창자')
    modern = re.sub(r'^(왼|오른)(위|아래)허파정맥$', r'\2\1허파정맥', modern)
    return modern, traditional, basis


def _compose(name):
    name = name.rstrip('.')
    name = name[0].upper() + name[1:]  # inner vessel of '... branch of left colic artery'
    if name in ROOTS: return ROOTS[name]
    m = re.fullmatch(r'(.+) \((M\d)(?:[- ]segment)?\)', name)  # middle cerebral artery segments M1-M3
    if m and (base := _compose(m[1])): return (f'{base[0]} ({m[2]})', f'{base[1]} ({m[2]})', 'C')
    m = re.fullmatch(r'(.+) branch(?:es)? of (.+)', name)
    if m and m[1] in BRANCH and (base := _compose(m[2])):
        return (f'{base[0]} {BRANCH[m[1]][0]}가지', f'{base[1]} {BRANCH[m[1]][1]}지', 'C')
    m = re.fullmatch(r'(Anterior|Posterior) division of (.+)', name)
    if m and (base := _compose(m[2])):
        return (f"{base[0]} {'앞' if m[1] == 'Anterior' else '뒤'}갈래", f"{base[1]} {'전' if m[1] == 'Anterior' else '후'}분지", 'C')
    m = re.fullmatch(r'(.+) of (left|right) (lung|kidney)', name)
    if m and (base := ROOTS.get(m[1])):
        organ = {('left', 'lung'): ('왼허파', '좌폐'), ('right', 'lung'): ('오른허파', '우폐'),
                 ('left', 'kidney'): ('왼콩팥', '좌신'), ('right', 'kidney'): ('오른콩팥', '우신')}[(m[2], m[3])]
        return (f'{organ[0]} {base[0]}', f'{organ[1]} {base[1]}', 'C')
    m = re.fullmatch(r'(Left|Right) (.+)', name)
    if m and (base := ROOTS.get(m[2][0].upper() + m[2][1:])) and not base[0].startswith(('왼', '오른')):
        left = m[1] == 'Left'
        return (('왼' if left else '오른') + base[0], ('좌' if left else '우') + base[1], 'C')
    return None
