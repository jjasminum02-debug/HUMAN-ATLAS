"""Read exact pinned source metadata, no geometry export/source save or autoexec."""
import bpy,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
source=ROOT/'atlas-data/source-cache/z-anatomy/t97/extracted/Z-Anatomy/Startup.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='9f08a17ea0115fed80b2a73ecdf0a1bc2ab2f6956f37c593ce23d513ea35afcd'
assert not bpy.context.preferences.filepaths.use_scripts_auto_execute
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
rows={'sourceHash':hashlib.sha256(source.read_bytes()).hexdigest(),'collections':[{'name':c.name} for c in bpy.data.collections],
'objects':[{'name':o.name,'parent':o.parent.name if o.parent else None,'collections':[c.name for c in o.users_collection]} for o in bpy.data.objects]}
Path(__file__).with_name('source-metadata.json').write_text(json.dumps(rows,ensure_ascii=False,separators=(',',':'))+'\n')
print('SOURCE_METADATA',len(rows['collections']),len(rows['objects']))
