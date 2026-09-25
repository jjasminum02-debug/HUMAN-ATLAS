#!/usr/bin/env python3
"""Idempotently add the T05 source-bounded calf pilot structure records."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA_PATH = ROOT / "atlas-data/catalog/canonical-catalog.json"
REGISTRY_PATH = ROOT / "atlas-data/sources/registry.json"
STATUS_PATH = ROOT / "atlas-data/catalog/catalog-status.json"

GRAY_SOURCE_ID = "GRAY_ANATOMY_20E_1918"
GRAY_EDITION = "Anatomy of the Human Body, 20th US edition, thoroughly revised and re-edited by Warren H. Lewis; Lea & Febiger, 1918"
GRAY_CHAPTER_URL = "https://www.bartleby.com/lit-hub/anatomy-of-the-human-body/8c-the-muscles-and-fasci-of-the-leg/"
GRAY_TA_URL = "https://www.bartleby.com/lit-hub/anatomy-of-the-human-body/pages-480/"

EVIDENCE = {
    "EV-GRAY1918-GASTRO": "Gray 20th US ed. (1918), section 8c, ‘The Superficial Group’, subsection ‘The Gastrocnemius’: medial and lateral head attachments, shared knee-capsule attachment, and head aponeuroses. Chapter subsection locator; printed page not independently verified. " + GRAY_CHAPTER_URL,
    "EV-GRAY1918-CALCANEAL-TENDON": "Gray 20th US ed. (1918), section 8c, subsection ‘Tendo Calcaneus (tendo Achillis)’: common gastrocnemius/soleus tendon and its attachment at the middle posterior calcaneus. " + GRAY_CHAPTER_URL,
    "EV-GRAY1918-SOLEUS": "Gray 20th US ed. (1918), section 8c, ‘The Superficial Group’, subsection ‘The Soleus’: tibial and fibular attachments, tendinous arch, and union with the gastrocnemius tendon. Chapter subsection locator; printed page not independently verified. " + GRAY_CHAPTER_URL,
    "EV-GRAY1918-TIBIALIS-ANTERIOR": "Gray 20th US ed. (1918), section 8c, subsection ‘The Tibialis anterior (Tibialis anticus)’, printed page 480: origins, tendon passage, and insertions. " + GRAY_TA_URL,
    "EV-GRAY1918-TIBIALIS-POSTERIOR": "Gray 20th US ed. (1918), section 8c, ‘The Deep Group’, subsection ‘The Tibialis posterior (Tibialis posticus)’: origins, tendon course, navicular insertion and fibrous expansions. Chapter subsection locator; printed page not independently verified. " + GRAY_CHAPTER_URL,
    "EV-GRAY1918-FIBULARIS-LONGUS": "Gray 20th US ed. (1918), section 8c, ‘The Lateral Crural Muscles’, subsection ‘The Peronæus longus’: origins, tendon course, insertions and stated occasional slips. Chapter subsection locator; printed page not independently verified. " + GRAY_CHAPTER_URL,
    "EV-GRAY1918-FIBULARIS-BREVIS": "Gray 20th US ed. (1918), section 8c, ‘The Lateral Crural Muscles’, subsection ‘The Peronæus brevis’: origins, tendon course and insertion. Chapter subsection locator; printed page not independently verified. " + GRAY_CHAPTER_URL,
    "EV-GRAY1918-TA-COURSE": "Gray 20th US ed. (1918), section 8c, subsection ‘The Tibialis anterior (Tibialis anticus)’, printed page 480: tendon course through the crural ligaments. " + GRAY_TA_URL,
    "EV-GRAY1918-TP-COURSE": "Gray 20th US ed. (1918), section 8c, ‘The Deep Group’, subsection ‘The Tibialis posterior (Tibialis posticus)’: tendon course behind the medial malleolus and across named foot ligaments. " + GRAY_CHAPTER_URL,
    "EV-GRAY1918-FL-COURSE": "Gray 20th US ed. (1918), section 8c, ‘The Lateral Crural Muscles’, subsection ‘The Peronæus longus’: tendon course behind the lateral malleolus, across the calcaneus and cuboid, and under the long plantar ligament. " + GRAY_CHAPTER_URL,
    "EV-GRAY1918-FB-COURSE": "Gray 20th US ed. (1918), section 8c, ‘The Lateral Crural Muscles’, subsection ‘The Peronæus brevis’: tendon course behind the lateral malleolus and along the calcaneus. " + GRAY_CHAPTER_URL,
}

# Stable Structure IDs. Surface/landmark labels retain the source's granularity.
STRUCTURES = [
    ("HA-S-FEMUR", "bone", "Femur", "EV-GRAY1918-GASTRO", None),
    ("HA-S-FEMORAL-CONDYLE-MEDIAL", "landmark", "Medial condyle of femur", "EV-GRAY1918-GASTRO", "HA-S-FEMUR"),
    ("HA-S-FEMUR-ADJACENT-MEDIAL-CONDYLE", "landmark", "Femur adjacent to the upper posterior part of the medial condyle", "EV-GRAY1918-GASTRO", "HA-S-FEMUR"),
    ("HA-S-FEMORAL-CONDYLE-LATERAL", "landmark", "Lateral condyle of femur", "EV-GRAY1918-GASTRO", "HA-S-FEMUR"),
    ("HA-S-FEMUR-POSTERIOR-ABOVE-LATERAL-CONDYLE", "landmark", "Posterior surface of femur immediately above lateral condyle", "EV-GRAY1918-GASTRO", "HA-S-FEMUR"),
    ("HA-S-KNEE-CAPSULE", "other", "Capsule of the knee", "EV-GRAY1918-GASTRO", None),
    ("HA-S-TIBIA", "bone", "Tibia", "EV-GRAY1918-TIBIALIS-ANTERIOR", None),
    ("HA-S-TIBIA-LATERAL-CONDYLE", "landmark", "Lateral condyle of tibia", "EV-GRAY1918-TIBIALIS-ANTERIOR", "HA-S-TIBIA"),
    ("HA-S-TIBIA-UPPER-LATERAL-SURFACE", "landmark", "Upper half or two-thirds of lateral surface of tibia", "EV-GRAY1918-TIBIALIS-ANTERIOR", "HA-S-TIBIA"),
    ("HA-S-TIBIA-POPLITEAL-LINE", "landmark", "Popliteal line of tibia", "EV-GRAY1918-SOLEUS", "HA-S-TIBIA"),
    ("HA-S-TIBIA-MEDIAL-BORDER-MIDDLE-THIRD", "landmark", "Middle third of medial border of tibia", "EV-GRAY1918-SOLEUS", "HA-S-TIBIA"),
    ("HA-S-TIBIA-POSTERIOR-LATERAL-TP-REGION", "landmark", "Lateral part of posterior tibial surface from the popliteal-line region to the junction of the middle and lower thirds", "EV-GRAY1918-TIBIALIS-POSTERIOR", "HA-S-TIBIA"),
    ("HA-S-FIBULA", "bone", "Fibula", "EV-GRAY1918-SOLEUS", None),
    ("HA-S-FIBULA-HEAD", "landmark", "Head of fibula", "EV-GRAY1918-SOLEUS", "HA-S-FIBULA"),
    ("HA-S-FIBULA-POSTERIOR-UPPER-THIRD", "landmark", "Upper third of posterior surface of fibular body", "EV-GRAY1918-SOLEUS", "HA-S-FIBULA"),
    ("HA-S-FIBULA-MEDIAL-UPPER-TWO-THIRDS", "landmark", "Upper two-thirds of medial surface of fibula", "EV-GRAY1918-TIBIALIS-POSTERIOR", "HA-S-FIBULA"),
    ("HA-S-FIBULA-LATERAL-SURFACE", "landmark", "Lateral surface of fibular body", "EV-GRAY1918-FIBULARIS-LONGUS", "HA-S-FIBULA"),
    ("HA-S-FIBULA-LATERAL-UPPER-TWO-THIRDS", "landmark", "Upper two-thirds of lateral surface of fibular body", "EV-GRAY1918-FIBULARIS-LONGUS", "HA-S-FIBULA"),
    ("HA-S-FIBULA-LATERAL-LOWER-TWO-THIRDS", "landmark", "Lower two-thirds of lateral surface of fibular body", "EV-GRAY1918-FIBULARIS-BREVIS", "HA-S-FIBULA"),
    ("HA-S-INTEROSSEOUS-MEMBRANE-LEG", "other", "Interosseous membrane of the leg", "EV-GRAY1918-TIBIALIS-ANTERIOR", None),
    ("HA-S-CRURAL-FASCIA", "fascia", "Deep fascia of the leg (fascia cruris)", "EV-GRAY1918-TIBIALIS-ANTERIOR", None),
    ("HA-S-TA-EDL-SEPTUM", "fascia", "Intermuscular septum between tibialis anterior and extensor digitorum longus", "EV-GRAY1918-TIBIALIS-ANTERIOR", None),
    ("HA-S-LATERAL-LEG-SEPTA", "fascia", "Intermuscular septa separating the lateral muscles from adjacent anterior and posterior muscles", "EV-GRAY1918-FIBULARIS-LONGUS", None),
    ("HA-S-TP-ADJACENT-INTERMUSCULAR-SEPTA", "fascia", "Intermuscular septa separating tibialis posterior from adjacent muscles", "EV-GRAY1918-TIBIALIS-POSTERIOR", None),
    ("HA-S-DEEP-TRANSVERSE-FASCIA-LEG", "fascia", "Deep transverse fascia of the leg", "EV-GRAY1918-TIBIALIS-POSTERIOR", None),
    ("HA-S-TENDINOUS-ARCH-SOLEUS", "other", "Tendinous arch between tibial and fibular origins of soleus", "EV-GRAY1918-SOLEUS", None),
    ("HA-S-CALCANEAL-TENDON", "tendon", "Calcaneal tendon (tendo calcaneus; tendo Achillis)", "EV-GRAY1918-CALCANEAL-TENDON", None),
    ("HA-S-CALCANEUS", "bone", "Calcaneus", "EV-GRAY1918-CALCANEAL-TENDON", None),
    ("HA-S-CALCANEUS-POSTERIOR-MIDDLE", "landmark", "Middle part of posterior surface of calcaneus", "EV-GRAY1918-CALCANEAL-TENDON", "HA-S-CALCANEUS"),
    ("HA-S-MEDIAL-CUNEIFORM", "bone", "First cuneiform (medial cuneiform)", "EV-GRAY1918-TIBIALIS-ANTERIOR", None),
    ("HA-S-MEDIAL-CUNEIFORM-INFEROMEDIAL-SURFACE", "landmark", "Medial and under surface of first cuneiform", "EV-GRAY1918-TIBIALIS-ANTERIOR", "HA-S-MEDIAL-CUNEIFORM"),
    ("HA-S-METATARSAL-1", "bone", "First metatarsal bone", "EV-GRAY1918-TIBIALIS-ANTERIOR", None),
    ("HA-S-BASE-METATARSAL-1", "landmark", "Base of first metatarsal bone", "EV-GRAY1918-TIBIALIS-ANTERIOR", "HA-S-METATARSAL-1"),
    ("HA-S-NAVICULAR", "bone", "Navicular bone", "EV-GRAY1918-TIBIALIS-POSTERIOR", None),
    ("HA-S-NAVICULAR-TUBEROSITY", "landmark", "Tuberosity of navicular bone", "EV-GRAY1918-TIBIALIS-POSTERIOR", "HA-S-NAVICULAR"),
    ("HA-S-SUSTENTACULUM-TALI", "landmark", "Sustentaculum tali of calcaneus", "EV-GRAY1918-TIBIALIS-POSTERIOR", "HA-S-CALCANEUS"),
    ("HA-S-CUNEIFORM-BONES", "bone", "Three cuneiform bones", "EV-GRAY1918-TIBIALIS-POSTERIOR", None),
    ("HA-S-CUBOID", "bone", "Cuboid bone", "EV-GRAY1918-TIBIALIS-POSTERIOR", None),
    ("HA-S-BASE-METATARSAL-2", "landmark", "Base of second metatarsal bone", "EV-GRAY1918-TIBIALIS-POSTERIOR", None),
    ("HA-S-BASE-METATARSAL-3", "landmark", "Base of third metatarsal bone", "EV-GRAY1918-TIBIALIS-POSTERIOR", None),
    ("HA-S-BASE-METATARSAL-4", "landmark", "Base of fourth metatarsal bone", "EV-GRAY1918-TIBIALIS-POSTERIOR", None),
    ("HA-S-METATARSAL-5", "bone", "Fifth metatarsal bone", "EV-GRAY1918-FIBULARIS-BREVIS", None),
    ("HA-S-TUBEROSITY-BASE-METATARSAL-5", "landmark", "Tuberosity at base of fifth metatarsal", "EV-GRAY1918-FIBULARIS-BREVIS", "HA-S-METATARSAL-5"),
    ("HA-S-MEDIAL-MALLEOLUS", "landmark", "Medial malleolus", "EV-GRAY1918-TP-COURSE", "HA-S-TIBIA"),
    ("HA-S-LACINIATE-LIGAMENT", "other", "Laciniate ligament", "EV-GRAY1918-TP-COURSE", None),
    ("HA-S-DELTOID-LIGAMENT", "other", "Deltoid ligament", "EV-GRAY1918-TP-COURSE", None),
    ("HA-S-PLANTAR-CALCANEONAVICULAR-LIGAMENT", "other", "Plantar calcaneonavicular ligament", "EV-GRAY1918-TP-COURSE", None),
    ("HA-S-LATERAL-MALLEOLUS", "landmark", "Lateral malleolus", "EV-GRAY1918-FL-COURSE", "HA-S-FIBULA"),
    ("HA-S-CALCANEUS-LATERAL-SURFACE", "landmark", "Lateral surface of calcaneus", "EV-GRAY1918-FL-COURSE", "HA-S-CALCANEUS"),
    ("HA-S-CALCANEAL-TROCHLEAR-PROCESS", "landmark", "Trochlear process of calcaneus", "EV-GRAY1918-FB-COURSE", "HA-S-CALCANEUS"),
    ("HA-S-CUBOID-GROOVE", "landmark", "Groove on plantar surface of cuboid", "EV-GRAY1918-FL-COURSE", "HA-S-CUBOID"),
    ("HA-S-LONG-PLANTAR-LIGAMENT", "other", "Long plantar ligament", "EV-GRAY1918-FL-COURSE", None),
    ("HA-S-TRANSVERSE-CRURAL-LIGAMENT", "fascia", "Transverse crural ligament", "EV-GRAY1918-TA-COURSE", None),
    ("HA-S-CRUCIATE-CRURAL-LIGAMENT", "fascia", "Cruciate crural ligament", "EV-GRAY1918-TA-COURSE", None),
]

# key, muscle/part, role, target, source-bounded summary, evidence IDs, variantContext
ATTACHMENTS = [
    ("GASTRO-LAT-FEMUR-ORIGIN", "HA-P-000001", "origin", "HA-S-FEMORAL-CONDYLE-LATERAL", "The lateral head arises at an impression on the side of the lateral femoral condyle.", ["EV-GRAY1918-GASTRO"], None),
    ("GASTRO-LAT-FEMUR-POSTERIOR-ORIGIN", "HA-P-000001", "origin", "HA-S-FEMUR-POSTERIOR-ABOVE-LATERAL-CONDYLE", "The lateral head also arises from the posterior femoral surface immediately above the lateral part of the condyle.", ["EV-GRAY1918-GASTRO"], None),
    ("GASTRO-LAT-KNEE-CAPSULE-ORIGIN", "HA-P-000001", "origin", "HA-S-KNEE-CAPSULE", "The source states that both gastrocnemius heads also arise from the subjacent knee-joint capsule.", ["EV-GRAY1918-GASTRO"], None),
    ("GASTRO-MED-FEMUR-ORIGIN", "HA-P-000002", "origin", "HA-S-FEMORAL-CONDYLE-MEDIAL", "The medial, larger head arises from a depression at the upper posterior part of the medial femoral condyle.", ["EV-GRAY1918-GASTRO"], None),
    ("GASTRO-MED-FEMUR-ADJACENT-ORIGIN", "HA-P-000002", "origin", "HA-S-FEMUR-ADJACENT-MEDIAL-CONDYLE", "The medial head also arises from the femur adjacent to the upper posterior part of the medial condyle.", ["EV-GRAY1918-GASTRO"], None),
    ("GASTRO-MED-KNEE-CAPSULE-ORIGIN", "HA-P-000002", "origin", "HA-S-KNEE-CAPSULE", "The source states that both gastrocnemius heads also arise from the subjacent knee-joint capsule.", ["EV-GRAY1918-GASTRO"], None),
    ("GASTRO-CALCANEUS-INSERTION", "HA-M-000001", "insertion", "HA-S-CALCANEUS-POSTERIOR-MIDDLE", "The head aponeuroses converge into the gastrocnemius aponeurosis, which joins the soleus tendon as the calcaneal tendon; the shared tendon attaches to the middle posterior calcaneus.", ["EV-GRAY1918-GASTRO", "EV-GRAY1918-CALCANEAL-TENDON"], None),
    ("SOLEUS-FIBULA-HEAD-ORIGIN", "HA-M-000002", "origin", "HA-S-FIBULA-HEAD", "Tendinous fibers arise from the back of the head of the fibula.", ["EV-GRAY1918-SOLEUS"], None),
    ("SOLEUS-FIBULA-POSTERIOR-UPPER-THIRD-ORIGIN", "HA-M-000002", "origin", "HA-S-FIBULA-POSTERIOR-UPPER-THIRD", "Tendinous fibers arise from the upper third of the posterior surface of the fibular body.", ["EV-GRAY1918-SOLEUS"], None),
    ("SOLEUS-TIBIA-POPLITEAL-LINE-ORIGIN", "HA-M-000002", "origin", "HA-S-TIBIA-POPLITEAL-LINE", "The source identifies the popliteal line as part of the tibial origin.", ["EV-GRAY1918-SOLEUS"], None),
    ("SOLEUS-TIBIA-MEDIAL-BORDER-ORIGIN", "HA-M-000002", "origin", "HA-S-TIBIA-MEDIAL-BORDER-MIDDLE-THIRD", "The source identifies the middle third of the medial tibial border as part of the tibial origin.", ["EV-GRAY1918-SOLEUS"], None),
    ("SOLEUS-ARCH-ORIGIN", "HA-M-000002", "origin", "HA-S-TENDINOUS-ARCH-SOLEUS", "Some fibers arise from a tendinous arch placed between the tibial and fibular origins.", ["EV-GRAY1918-SOLEUS"], None),
    ("SOLEUS-CALCANEUS-INSERTION", "HA-M-000002", "insertion", "HA-S-CALCANEUS-POSTERIOR-MIDDLE", "The soleus aponeurosis joins the gastrocnemius tendon to form the calcaneal tendon, whose insertion is at the middle posterior calcaneus.", ["EV-GRAY1918-SOLEUS", "EV-GRAY1918-CALCANEAL-TENDON"], None),
    ("TA-TIBIA-CONDYLE-ORIGIN", "HA-M-000003", "origin", "HA-S-TIBIA-LATERAL-CONDYLE", "The source places an origin on the lateral condyle of the tibia.", ["EV-GRAY1918-TIBIALIS-ANTERIOR"], None),
    ("TA-TIBIA-SURFACE-ORIGIN", "HA-M-000003", "origin", "HA-S-TIBIA-UPPER-LATERAL-SURFACE", "The source places an origin on the upper half or two-thirds of the lateral surface of the tibial body.", ["EV-GRAY1918-TIBIALIS-ANTERIOR"], None),
    ("TA-IOM-ORIGIN", "HA-M-000003", "origin", "HA-S-INTEROSSEOUS-MEMBRANE-LEG", "The source also describes an origin from the adjoining part of the leg interosseous membrane.", ["EV-GRAY1918-TIBIALIS-ANTERIOR"], None),
    ("TA-FASCIA-ORIGIN", "HA-M-000003", "origin", "HA-S-CRURAL-FASCIA", "The source describes fibers arising from the deep surface of the leg fascia.", ["EV-GRAY1918-TIBIALIS-ANTERIOR"], None),
    ("TA-SEPTUM-ORIGIN", "HA-M-000003", "origin", "HA-S-TA-EDL-SEPTUM", "The source describes an origin from the intermuscular septum between tibialis anterior and extensor digitorum longus.", ["EV-GRAY1918-TIBIALIS-ANTERIOR"], None),
    ("TA-CUNEIFORM-INSERTION", "HA-M-000003", "insertion", "HA-S-MEDIAL-CUNEIFORM-INFEROMEDIAL-SURFACE", "The tendon is inserted into the medial and under surface of the first cuneiform.", ["EV-GRAY1918-TIBIALIS-ANTERIOR"], None),
    ("TA-MT1-INSERTION", "HA-M-000003", "insertion", "HA-S-BASE-METATARSAL-1", "The tendon is inserted into the base of the first metatarsal bone.", ["EV-GRAY1918-TIBIALIS-ANTERIOR"], None),
    ("TP-IOM-ORIGIN", "HA-M-000004", "origin", "HA-S-INTEROSSEOUS-MEMBRANE-LEG", "The source describes an origin from nearly all of the posterior leg interosseous membrane, except its lowest part.", ["EV-GRAY1918-TIBIALIS-POSTERIOR"], None),
    ("TP-TIBIA-ORIGIN", "HA-M-000004", "origin", "HA-S-TIBIA-POSTERIOR-LATERAL-TP-REGION", "The source places fibers on the lateral portion of the posterior tibial surface, from the popliteal-line region to the junction of the middle and lower thirds.", ["EV-GRAY1918-TIBIALIS-POSTERIOR"], None),
    ("TP-FIBULA-ORIGIN", "HA-M-000004", "origin", "HA-S-FIBULA-MEDIAL-UPPER-TWO-THIRDS", "The source places fibers on the upper two-thirds of the medial fibular surface.", ["EV-GRAY1918-TIBIALIS-POSTERIOR"], None),
    ("TP-TRANSVERSE-FASCIA-ORIGIN", "HA-M-000004", "origin", "HA-S-DEEP-TRANSVERSE-FASCIA-LEG", "The source notes some fibers from the deep transverse fascia of the leg.", ["EV-GRAY1918-TIBIALIS-POSTERIOR"], None),
    ("TP-SEPTA-ORIGIN", "HA-M-000004", "origin", "HA-S-TP-ADJACENT-INTERMUSCULAR-SEPTA", "The source notes some fibers from intermuscular septa separating the muscle from adjacent muscles.", ["EV-GRAY1918-TIBIALIS-POSTERIOR"], None),
    ("TP-NAVICULAR-INSERTION", "HA-M-000004", "insertion", "HA-S-NAVICULAR-TUBEROSITY", "The tendon inserts into the tuberosity of the navicular bone.", ["EV-GRAY1918-TIBIALIS-POSTERIOR"], None),
    ("TP-SUSTENTACULUM-EXPANSION", "HA-M-000004", "other_attachment", "HA-S-SUSTENTACULUM-TALI", "A fibrous expansion passes backward to the sustentaculum tali of the calcaneus.", ["EV-GRAY1918-TIBIALIS-POSTERIOR"], None),
    ("TP-CUNEIFORM-EXPANSION", "HA-M-000004", "other_attachment", "HA-S-CUNEIFORM-BONES", "The source describes a forward and lateral fibrous expansion to the three cuneiform bones.", ["EV-GRAY1918-TIBIALIS-POSTERIOR"], None),
    ("TP-CUBOID-EXPANSION", "HA-M-000004", "other_attachment", "HA-S-CUBOID", "The source describes a forward and lateral fibrous expansion to the cuboid.", ["EV-GRAY1918-TIBIALIS-POSTERIOR"], None),
    ("TP-MT2-EXPANSION", "HA-M-000004", "other_attachment", "HA-S-BASE-METATARSAL-2", "The source describes a forward and lateral fibrous expansion to the base of the second metatarsal.", ["EV-GRAY1918-TIBIALIS-POSTERIOR"], None),
    ("TP-MT3-EXPANSION", "HA-M-000004", "other_attachment", "HA-S-BASE-METATARSAL-3", "The source describes a forward and lateral fibrous expansion to the base of the third metatarsal.", ["EV-GRAY1918-TIBIALIS-POSTERIOR"], None),
    ("TP-MT4-EXPANSION", "HA-M-000004", "other_attachment", "HA-S-BASE-METATARSAL-4", "The source describes a forward and lateral fibrous expansion to the base of the fourth metatarsal.", ["EV-GRAY1918-TIBIALIS-POSTERIOR"], None),
    ("FL-FIBULA-HEAD-ORIGIN", "HA-M-000005", "origin", "HA-S-FIBULA-HEAD", "The source describes an origin from the head of the fibula.", ["EV-GRAY1918-FIBULARIS-LONGUS"], None),
    ("FL-FIBULA-LATERAL-UPPER-TWO-THIRDS-ORIGIN", "HA-M-000005", "origin", "HA-S-FIBULA-LATERAL-UPPER-TWO-THIRDS", "The source describes an origin from the upper two-thirds of the lateral surface of the fibular body.", ["EV-GRAY1918-FIBULARIS-LONGUS"], None),
    ("FL-FASCIA-ORIGIN", "HA-M-000005", "origin", "HA-S-CRURAL-FASCIA", "The source also describes an origin from the deep surface of the leg fascia.", ["EV-GRAY1918-FIBULARIS-LONGUS"], None),
    ("FL-SEPTA-ORIGIN", "HA-M-000005", "origin", "HA-S-LATERAL-LEG-SEPTA", "The source also describes origins from the septa separating the lateral muscle from adjacent anterior and posterior muscles.", ["EV-GRAY1918-FIBULARIS-LONGUS"], None),
    ("FL-MT1-INSERTION", "HA-M-000005", "insertion", "HA-S-BASE-METATARSAL-1", "The tendon inserts on the lateral side of the base of the first metatarsal.", ["EV-GRAY1918-FIBULARIS-LONGUS"], None),
    ("FL-CUNEIFORM-INSERTION", "HA-M-000005", "insertion", "HA-S-MEDIAL-CUNEIFORM", "The tendon inserts on the lateral side of the first cuneiform.", ["EV-GRAY1918-FIBULARIS-LONGUS"], None),
    ("FB-FIBULA-LATERAL-LOWER-TWO-THIRDS-ORIGIN", "HA-M-000006", "origin", "HA-S-FIBULA-LATERAL-LOWER-TWO-THIRDS", "The source describes an origin from the lower two-thirds of the lateral surface of the fibular body.", ["EV-GRAY1918-FIBULARIS-BREVIS"], None),
    ("FB-SEPTA-ORIGIN", "HA-M-000006", "origin", "HA-S-LATERAL-LEG-SEPTA", "The source also describes origins from septa separating the muscle from adjacent anterior and posterior muscles.", ["EV-GRAY1918-FIBULARIS-BREVIS"], None),
    ("FB-MT5-INSERTION", "HA-M-000006", "insertion", "HA-S-TUBEROSITY-BASE-METATARSAL-5", "The tendon inserts on the lateral side of the tuberosity at the base of the fifth metatarsal.", ["EV-GRAY1918-FIBULARIS-BREVIS"], None),
]

COURSES = [
    ("TA", "HA-M-000003", "The tendon passes through the medial compartments of the transverse and cruciate crural ligaments before reaching its foot insertions.", ["HA-S-TRANSVERSE-CRURAL-LIGAMENT", "HA-S-CRUCIATE-CRURAL-LIGAMENT"], ["EV-GRAY1918-TA-COURSE"]),
    ("TP", "HA-M-000004", "The tendon runs behind the medial malleolus in a groove, then beneath the laciniate ligament, over the deltoid ligament, and beneath the plantar calcaneonavicular ligament.", ["HA-S-MEDIAL-MALLEOLUS", "HA-S-LACINIATE-LIGAMENT", "HA-S-DELTOID-LIGAMENT", "HA-S-PLANTAR-CALCANEONAVICULAR-LIGAMENT"], ["EV-GRAY1918-TP-COURSE"]),
    ("FL", "HA-M-000005", "The tendon passes behind the lateral malleolus, across the lateral calcaneus and cuboid groove, and beneath the long plantar ligament.", ["HA-S-LATERAL-MALLEOLUS", "HA-S-CALCANEUS-LATERAL-SURFACE", "HA-S-CUBOID-GROOVE", "HA-S-LONG-PLANTAR-LIGAMENT"], ["EV-GRAY1918-FL-COURSE"]),
    ("FB", "HA-M-000006", "The tendon passes behind the lateral malleolus and forward on the lateral calcaneus above the trochlear process.", ["HA-S-LATERAL-MALLEOLUS", "HA-S-CALCANEUS-LATERAL-SURFACE", "HA-S-CALCANEAL-TROCHLEAR-PROCESS"], ["EV-GRAY1918-FB-COURSE"]),
]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def source_record():
    return {
        "id": GRAY_SOURCE_ID,
        "title": "Anatomy of the Human Body",
        "authors": ["Henry Gray", "Warren H. Lewis (editor)"],
        "edition": GRAY_EDITION,
        "year": 1918,
        "urlOrLocalRef": GRAY_CHAPTER_URL,
        "accessDate": "2026-09-25",
        "license": {
            "id": "LIC-GRAY1918-US-PD-INTERNAL",
            "name": "Public domain in the United States for the 1918 original; global redistribution status not assessed",
            "spdxId": None,
            "allowedUses": ["internal", "research"],
            "attributionRequired": True,
            "attributionText": "Gray, Henry; Lewis, Warren H., ed. Anatomy of the Human Body, 20th US ed. (Lea & Febiger, 1918), section 8c. https://www.bartleby.com/lit-hub/anatomy-of-the-human-body/8c-the-muscles-and-fasci-of-the-leg/",
            "derivativesAllowed": False,
            "redistributionAllowed": False,
        },
    }


def registry_record():
    return {
        "id": GRAY_SOURCE_ID,
        "category": "historical_anatomy_reference",
        "title": "Anatomy of the Human Body",
        "organization": "Henry Gray; Warren H. Lewis (editor); Lea & Febiger",
        "edition": GRAY_EDITION,
        "edition_status": "20th edition and 1918 imprint verified by the title page and library catalog; section 8c and the Tibialis anterior printed page 480 inspected as online text; not treated as a current anatomy standard",
        "primary_locator": GRAY_CHAPTER_URL,
        "edition_locator": "https://www.biodiversitylibrary.org/bibliography/20311",
        "verified_content_locators": [
            GRAY_TA_URL,
            GRAY_CHAPTER_URL,
        ],
        "verified_locator_detail": "T05 uses paraphrased attachment summaries with the exact source edition and subsection/page locator recorded per evidence item. No full text or image is copied into project data. The online chapter is used as a historical source transcription; source claims remain needs_review.",
        "license": {
            "name": "Public domain in the United States (1918 original); global status not assessed",
            "status": "1918 original identified as not in copyright by Biodiversity Heritage Library; Wikisource source record states US public-domain basis; no public redistribution is authorized by this task",
            "url": "https://www.biodiversitylibrary.org/bibliography/20311",
            "required_credit_verbatim": None,
            "note": "The task stores internal paraphrases and citations only. Check territorial status and the exact source copy before any external distribution.",
        },
        "access_state": "bibliographic record and scan-backed text section accessed online; no source file downloaded",
        "artifact_state": "no local source copy; no source hash; claim-level locators retained in atlas-data/catalog/canonical-catalog.json",
        "intended_use_candidate": "Historical structural cross-check for pilot origin/insertion and tendon-course claims; not a current nomenclature authority, complete variation catalog, or clinical source.",
        "limitations": [
            "The 1918 edition predates current nomenclature and contemporary anatomy references; every T05 claim remains needs_review.",
            "The source transcription describes selected anatomy and does not establish the completeness of each attachment region or all variants.",
            "U.S. public-domain status does not establish worldwide distribution status for this project's future release context.",
        ],
    }


def main():
    dataset = read_json(DATA_PATH)
    entities = dataset["entities"]
    # Replace only records owned by this idempotent T05 builder.
    entities["sources"] = [x for x in entities["sources"] if x["id"] != GRAY_SOURCE_ID]
    entities["evidence"] = [x for x in entities["evidence"] if not x["id"].startswith("EV-GRAY1918-")]
    entities["structures"] = [x for x in entities["structures"] if not x["id"].startswith("HA-S-T05-") and x["id"] not in {s[0] for s in STRUCTURES}]
    entities["terms"] = [x for x in entities["terms"] if not x["id"].startswith("HA-T-T05-S-")]
    entities["attachments"] = [x for x in entities["attachments"] if not x["id"].startswith("HA-A-T05-")]
    entities["claims"] = [x for x in entities["claims"] if not x["id"].startswith("HA-C-T05-")]

    entities["sources"].append(source_record())
    source_registry = read_json(REGISTRY_PATH)
    source_registry["sources"] = [x for x in source_registry["sources"] if x["id"] != GRAY_SOURCE_ID]
    gray_registry = registry_record()
    source_registry["sources"].append(gray_registry)
    for source in source_registry["sources"]:
        if source["id"] == "OPENSTAX_AP2E":
            limitation = "The official section page includes an express restriction against ingesting book content into generative AI offerings without prior written permission. No OpenStax body text was added to T05 claims; AI-assisted extraction remains unused pending permission or a different source workflow."
            if limitation not in source.setdefault("limitations", []):
                source["limitations"].append(limitation)
            source["t05_ai_extraction_status"] = "not_used_due_to_publisher_ingestion_restriction"

    evidence_claims = {evidence_id: [] for evidence_id in EVIDENCE}
    structures = []
    terms = []
    term_counter = 1
    term_ids_by_structure = {}
    for ident, kind, label, evidence_id, parent_id in STRUCTURES:
        term_id = f"HA-T-T05-S-{ident.removeprefix('HA-S-')}"
        term = {
            "id": term_id,
            "conceptId": ident,
            "language": "en",
            "script": "Latn",
            "text": label,
            "termRole": "historical",
            "edition": GRAY_EDITION,
            "evidenceIds": [evidence_id],
            "reviewState": "needs_review",
        }
        terms.append(term)
        term_ids_by_structure[ident] = term_id
        row = {"id": ident, "kind": kind, "termIds": [term_id]}
        if parent_id is not None:
            row["parentId"] = parent_id
        structures.append(row)

    attachment_records = []
    claim_records = []
    for key, owner, role, target, summary, evidence_ids, variant_context in ATTACHMENTS:
        attachment_id = f"HA-A-T05-{key}"
        claim_id = f"HA-C-T05-{key}"
        attachment = {
            "id": attachment_id,
            "muscleOrPartId": owner,
            "role": role,
            "targetStructureId": target,
            "landmarkId": target if next(s for s in STRUCTURES if s[0] == target)[1] == "landmark" else None,
            "descriptionClaimId": claim_id,
            "variantContext": variant_context,
        }
        claim = {
            "id": claim_id,
            "subjectId": attachment_id,
            "field": "attachment_description",
            "value": {"targetStructureId": target, "summary": summary, "edition": GRAY_EDITION},
            "evidenceIds": evidence_ids,
            "attribution": "source_summary",
            "reviewState": "needs_review",
        }
        attachment_records.append(attachment)
        claim_records.append(claim)
        for evidence_id in evidence_ids:
            evidence_claims[evidence_id].append(claim_id)

    for key, owner, summary, related_ids, evidence_ids in COURSES:
        claim_id = f"HA-C-T05-COURSE-{key}"
        claim_records.append({
            "id": claim_id,
            "subjectId": owner,
            "field": "tendon_course_related_structures",
            "value": {"summary": summary, "relatedStructureIds": related_ids, "edition": GRAY_EDITION},
            "evidenceIds": evidence_ids,
            "attribution": "source_summary",
            "reviewState": "needs_review",
        })
        for evidence_id in evidence_ids:
            evidence_claims[evidence_id].append(claim_id)

    evidence_records = []
    for evidence_id, locator in EVIDENCE.items():
        evidence_records.append({
            "id": evidence_id,
            "sourceId": GRAY_SOURCE_ID,
            "locator": locator,
            "supportedClaimIds": sorted(evidence_claims[evidence_id]),
            "evidenceKind": "primary",
        })

    entities["structures"].extend(structures)
    entities["terms"].extend(terms)
    entities["attachments"].extend(attachment_records)
    entities["claims"].extend(claim_records)
    entities["evidence"].extend(evidence_records)
    dataset["revision"] = "T05-pilot-structure-text-v1"
    write_json(DATA_PATH, dataset)
    write_json(REGISTRY_PATH, source_registry)

    catalog_status = read_json(STATUS_PATH)
    catalog_status["pilotStructureText"] = {
        "revision": "T05-pilot-structure-text-v1",
        "taskStatus": "complete_with_unreviewed_claims_and_language_gaps",
        "pilotMuscleConcepts": ["HA-M-000001", "HA-M-000002", "HA-M-000003", "HA-M-000004", "HA-M-000005", "HA-M-000006"],
        "gastrocnemiusHeadParts": ["HA-P-000001", "HA-P-000002"],
        "sourceBackedAttachmentRecords": len(attachment_records),
        "sourceBackedCourseClaims": len(COURSES),
        "structureTerms": len(terms),
        "allClaimsNeedsReview": all(x["reviewState"] == "needs_review" for x in claim_records),
        "koreanAndHanjaTerms": "missing; no primary item locators",
        "ta2EnglishLatinTermRoles": "needs_review; official/equivalent/synonym cells not visually verified",
        "humanReview": "not performed",
        "publicRelease": "not authorized",
    }
    catalog_status["nextAllowedWork"] = "T06 web app and text exploration may proceed from T03/T05; all T05 claims remain unreviewed and the whole-body catalog gate stays blocked."
    write_json(STATUS_PATH, catalog_status)
    print(json.dumps({
        "revision": dataset["revision"],
        "structures": len(structures),
        "structureTerms": len(terms),
        "attachments": len(attachment_records),
        "claims": len(claim_records),
        "evidence": len(evidence_records),
        "sources": [GRAY_SOURCE_ID],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
