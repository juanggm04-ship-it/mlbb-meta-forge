from pathlib import Path
from urllib.parse import urlparse
import json, os, re

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'data'/'site-config.json'


def normalize_base(value):
    value=(value or '').strip()
    if not value:
        raise RuntimeError('Public base URL is empty')
    parsed=urlparse(value)
    if parsed.scheme!='https' or not parsed.netloc or parsed.query or parsed.fragment:
        raise RuntimeError(f'Public base URL must be a clean HTTPS origin/path: {value}')
    return value.rstrip('/')+'/'


def normalize_domain(value):
    value=(value or '').strip().lower().rstrip('.')
    if not value:
        return None
    if '://' in value or '/' in value or ':' in value or not re.fullmatch(r'[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?',value):
        raise RuntimeError(f'Custom domain must be a bare hostname: {value}')
    if '.' not in value:
        raise RuntimeError(f'Custom domain must contain a public suffix: {value}')
    return value


def load_site_config():
    if not CONFIG.exists():
        raise RuntimeError('Missing data/site-config.json')
    cfg=json.loads(CONFIG.read_text(encoding='utf-8'))
    if cfg.get('schema_version')!=1:
        raise RuntimeError(f'Unsupported site config schema: {cfg.get("schema_version")}')
    override=os.getenv('MF_PUBLIC_BASE_URL')
    cfg['base_url']=normalize_base(override or cfg.get('base_url'))
    cfg['site_name']=(cfg.get('site_name') or 'MLBB Meta Forge').strip()
    cfg['locale']=(cfg.get('locale') or 'es').strip()
    cfg['deployment_target']=(cfg.get('deployment_target') or 'github-pages').strip()
    cfg['custom_domain']=normalize_domain(cfg.get('custom_domain'))
    cfg['noindex_paths']=sorted({str(x).strip('/') for x in cfg.get('noindex_paths',[]) if str(x).strip()})
    legacy=[]
    for value in cfg.get('legacy_base_urls',[]):
        try: base=normalize_base(value)
        except Exception: continue
        if base not in legacy: legacy.append(base)
    cfg['legacy_base_urls']=legacy
    if cfg['custom_domain']:
        parsed=urlparse(cfg['base_url'])
        if parsed.hostname!=cfg['custom_domain']:
            raise RuntimeError(f'Custom domain {cfg["custom_domain"]} must match public base host {parsed.hostname}')
        if parsed.path not in ('','/'):
            raise RuntimeError('Custom-domain base URL must be served from the domain root, not a subpath')
    return cfg


def canonical_for(path, base_url=None):
    cfg=load_site_config() if base_url is None else None
    base=cfg['base_url'] if cfg else normalize_base(base_url)
    rel=Path(path).as_posix().lstrip('./')
    if rel=='index.html': return base
    if rel.endswith('/index.html'): return base+rel[:-10]
    return base+rel
