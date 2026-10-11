from pathlib import Path
import json,re,sys

CONFIG=Path('data/monetization-config.json')
PRIVACY=Path('privacy.html')
errors=[]
def need(cond,msg):
    if not cond: errors.append(msg)

need(CONFIG.exists(),'Monetization config missing')
need(PRIVACY.exists(),'Privacy page missing')
if not CONFIG.exists():
    print('MONETIZATION READINESS VALIDATION FAILED')
    print('- Monetization config missing')
    sys.exit(1)

cfg=json.loads(CONFIG.read_text(encoding='utf-8'))
need(cfg.get('schema_version')==1,'Unsupported monetization config schema')
enabled=cfg.get('enabled') is True
provider=cfg.get('provider') or 'none'
publisher_id=(cfg.get('publisher_id') or '').strip()
personalized=cfg.get('personalized_ads') is True
serves_europe=cfg.get('serves_eea_uk_ch') is True
ads=cfg.get('ads_txt') or {}
consent=cfg.get('consent') or {}
analytics=cfg.get('analytics') or {}

need(provider in {'none','google_adsense'},f'Unsupported monetization provider: {provider}')
need(not personalized or enabled,'Personalized ads cannot be enabled while monetization is disabled')

# ads.txt may be staged before ad serving, but only with a real publisher ID.
ads_path=Path('ads.txt')
if ads.get('enabled') is True:
    ads_pub=(ads.get('publisher_id') or '').strip()
    need(bool(re.fullmatch(r'pub-\d{16}',ads_pub)),'ads.txt publisher ID must be a real-looking pub- + 16 digit ID')
    need(ads_path.exists(),'ads.txt is enabled in config but ads.txt file is missing')
    if ads_path.exists() and ads_pub:
        content=ads_path.read_text(encoding='utf-8')
        expected=f'google.com, {ads_pub}, DIRECT, f08c47fec0942fa0'
        need(expected in content,'ads.txt does not contain the configured Google seller declaration')
else:
    need(not ads_path.exists(),'ads.txt exists but ads_txt.enabled is false; do not publish placeholder seller IDs')

html='\n'.join(p.read_text(encoding='utf-8',errors='ignore') for p in Path('.').rglob('*.html') if '.git' not in p.parts and '_site' not in p.parts)
ad_runtime_tokens=('pagead2.googlesyndication.com','adsbygoogle')
analytics_tokens=('googletagmanager.com','google-analytics.com','gtag(')

if not enabled:
    need(not any(t in html for t in ad_runtime_tokens),'AdSense runtime detected while monetization is disabled')
    need(not personalized,'personalized_ads must remain false while monetization is disabled')
else:
    need(provider=='google_adsense','Enabled monetization currently requires provider=google_adsense')
    need(bool(re.fullmatch(r'ca-pub-\d{16}',publisher_id)),'Enabled AdSense requires a real-looking ca-pub- + 16 digit publisher ID')
    need(ads.get('enabled') is True,'Enabled AdSense requires ads.txt readiness')
    if ads.get('publisher_id'):
        need(publisher_id.replace('ca-','')==ads.get('publisher_id'),'AdSense client ID and ads.txt publisher ID do not match')
    if serves_europe:
        need(consent.get('enabled') is True,'Serving ads in EEA/UK/Switzerland requires consent handling to be enabled')
        need(consent.get('google_certified') is True,'EEA/UK/Switzerland ad serving requires a Google-certified CMP in this project guardrail')
        need(consent.get('iab_tcf') is True,'EEA/UK/Switzerland CMP must be configured for IAB TCF in this project guardrail')
        need(bool((consent.get('provider') or '').strip()),'Configured CMP provider name missing')

if analytics.get('enabled') is True:
    need((analytics.get('provider') or 'none')!='none','Analytics enabled without a provider')
else:
    need(not any(t in html for t in analytics_tokens),'Analytics runtime detected while analytics is disabled')

privacy=PRIVACY.read_text(encoding='utf-8') if PRIVACY.exists() else ''
if not enabled and analytics.get('enabled') is not True:
    need('Actualmente no instalamos cookies publicitarias ni de analítica.' in privacy,'Privacy page no longer matches the disabled ads/analytics state')
else:
    need('Actualmente no instalamos cookies publicitarias ni de analítica.' not in privacy,'Privacy disclosure still claims ads/analytics are disabled')
    need('anunci' in privacy.lower(),'Privacy page must disclose advertising when monetization is enabled')

if errors:
    print('MONETIZATION READINESS VALIDATION FAILED')
    for e in errors: print('- '+e)
    sys.exit(1)
state='enabled' if enabled else 'disabled-safe'
print(f'Monetization readiness passed: state={state}; provider={provider}; ads_txt={bool(ads.get("enabled"))}; european_consent_guard={serves_europe}; analytics={bool(analytics.get("enabled"))}; no placeholder IDs accepted.')
