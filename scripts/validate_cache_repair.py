from pathlib import Path
import re,sys
PAGE=Path('repair/index.html')
STATUS=Path('status/index.html')
errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)
need(PAGE.exists(),'repair/index.html missing')
need(STATUS.exists(),'status/index.html missing')
if PAGE.exists():
    text=PAGE.read_text(encoding='utf-8')
    for token,msg in [
        ('name="robots" content="noindex,nofollow"','Repair page must be noindex'),
        ('id="mf-cache-repair-runtime"','Repair runtime missing'),
        ("APP_SCOPE='/mlbb-meta-forge/'",'Repair scope guard missing'),
        ('navigator.serviceWorker.getRegistrations()','Service-worker inspection missing'),
        ('.startsWith(APP_SCOPE)','Service-worker scope filter missing'),
        ("k.startsWith('mf-shell-')",'Cache-name guard missing'),
        ('r.unregister()','Service-worker unregister missing'),
        ('caches.delete(k)','Cache deletion missing'),
        ("cache:'no-store'",'Network diagnostic must bypass browser HTTP cache'),
        ('localStorage','Repair page must disclose localStorage preservation'),
        ('Watchlist','Repair preservation disclosure missing'),
    ]: need(token in text,msg)
    runtime=re.search(r'<script id="mf-cache-repair-runtime">(.*?)</script>',text,re.S)
    need(bool(runtime),'Repair runtime could not be isolated')
    if runtime:
        js=runtime.group(1)
        for forbidden,msg in [
            ('localStorage.clear','Repair must not clear localStorage'),
            ('localStorage.removeItem','Repair must not remove localStorage items'),
            ('localStorage.setItem','Repair must not write localStorage'),
            ('sessionStorage.clear','Repair must not clear sessionStorage'),
            ('indexedDB.deleteDatabase','Repair must not delete IndexedDB'),
            ('serviceWorker.register','Repair page must not register a service worker'),
        ]: need(forbidden not in js,msg)
    need('id="mf-pwa-runtime"' not in text,'Repair page must remain outside the normal PWA runtime')
if STATUS.exists():
    status=STATUS.read_text(encoding='utf-8')
    need('id="cacheRepairPanel"' in status,'Status recovery panel missing')
    need('../repair/' in status,'Status repair link missing')
    need('No borra Watchlist, drafts, perfil ni preferencias.' in status,'Status preservation disclosure missing')
if errors:
    print('CACHE REPAIR VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
print('Cache repair validation passed: scoped service-worker/cache cleanup, no PWA self-registration, and local user data preserved.')
