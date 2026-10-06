from pathlib import Path
import json
import re

INDEX = Path('index.html')
CORE = Path('data/editorial-core.json')

html = INDEX.read_text(encoding='utf-8')
core = json.loads(CORE.read_text(encoding='utf-8'))
profiles = core.get('profiles') or {}
matchups = core.get('matchups') or {}

if len(profiles) < 30:
    raise RuntimeError(f'Editorial core too small: {len(profiles)} profiles')

# Remove a previous build-time core if this script is ever run twice.
html = re.sub(
    r'<script id="mfEditorialCore">.*?</script>',
    '',
    html,
    flags=re.S,
)

payload = json.dumps(core, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
core_tag = f'<script id="mfEditorialCore">window.MF_EDITORIAL={payload};</script>'
if '</head>' not in html:
    raise RuntimeError('Missing </head> in generated index')
html = html.replace('</head>', core_tag + '</head>', 1)

# Draft Coach and Post-Draft Analysis previously carried independent PROFILE objects.
profile_pattern = re.compile(r'const PROFILE=\{.*?\}\s*\n(?=const ally=|function picksFrom)', re.S)
html, profile_count = profile_pattern.subn(
    "const PROFILE=window.MF_EDITORIAL?.profiles||{};\n",
    html,
)

# Draft Coach interaction layer previously carried an independent MATCH object.
match_pattern = re.compile(r'const MATCH=\{.*?\};\s*\n\s*function values', re.S)
html, match_count = match_pattern.subn(
    "const MATCH=window.MF_EDITORIAL?.matchups||{};\n\nfunction values",
    html,
)

if profile_count != 2:
    raise RuntimeError(f'Expected to normalize 2 PROFILE blocks, normalized {profile_count}')
if match_count != 1:
    raise RuntimeError(f'Expected to normalize 1 MATCH block, normalized {match_count}')

# Runtime consistency guard: all matchup names must exist in the shared profile pool.
unknown = set()
for hero, rule in matchups.items():
    if hero not in profiles:
        unknown.add(hero)
    for key in ('warn', 'good'):
        for name in rule.get(key, []):
            if name not in profiles:
                unknown.add(name)
if unknown:
    raise RuntimeError('Unknown heroes in editorial matchups: ' + ', '.join(sorted(unknown)))

INDEX.write_text(html, encoding='utf-8')
print(f'Normalized editorial runtime: {len(profiles)} profiles, {len(matchups)} matchup rules')
