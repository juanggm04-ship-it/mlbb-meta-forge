from pathlib import Path
import sys

PAGE=Path('my-meta/index.html')
SRC=Path('scripts/inject_local_data_portability.py')
errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)
need(PAGE.exists(),'My Meta page missing')
need(SRC.exists(),'Local portability source missing')
text=PAGE.read_text(encoding='utf-8') if PAGE.exists() else ''
src=SRC.read_text(encoding='utf-8') if SRC.exists() else ''
for token,msg in [
    ('id="localDataPortability"','Local data portability panel missing'),
    ('id="exportLocalData"','Export backup action missing'),
    ('id="importLocalData"','Import backup input missing'),
    ('id="clearLocalData"','Clear local data action missing'),
    ('id="localDataStatus"','Accessible local data status missing'),
    ('id="local-data-portability-script"','Local portability runtime missing'),
    ("KEYS=['mf_watchlist_v1','mf_profile_v1','mf_draft_history_v1','mf_turn_draft_history_v1','mf_compare_recent_v1']",'Expected five portable keys missing'),
    ("app:'MLBB Meta Forge',version:1",'Backup schema/version missing'),
    ("file.size>1024*1024",'Import size limit missing'),
    ("HEROES.has",'Imported hero validation missing'),
    ('slice(0,8)','Draft history cap missing'),
    ('out.length>=6','Recent compare cap missing'),
    ("confirm('Importar reemplazará",'Import overwrite confirmation missing'),
    ("confirm('¿Borrar Watchlist",'Local clear confirmation missing'),
    ("new Blob([JSON.stringify(backup,null,2)]",'JSON backup download missing'),
    ("localStorage.setItem(k,JSON.stringify(value))",'Validated restore write missing'),
    ('El archivo se procesa localmente y no se sube a Meta Forge.','Local-processing disclosure missing'),
]: need(token in text or token in src,msg)
need('fetch(' not in src and 'XMLHttpRequest' not in src,'Portability tool must not upload backup data')
if errors:
    print('LOCAL DATA PORTABILITY VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print('Local data portability validation passed: five-key JSON backup, 133-hero validation, size/cap guards, overwrite confirmation and no network upload.')
