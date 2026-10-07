def finite(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def percentiles(values_by_name):
    """Return 0-100 average-rank percentiles. Ties receive the same percentile."""
    rows = sorted((v, n) for n, v in values_by_name.items() if finite(v))
    if not rows:
        return {}
    if len(rows) == 1:
        return {rows[0][1]: 50.0}
    out = {}
    i = 0
    total = len(rows)
    while i < total:
        j = i + 1
        value = rows[i][0]
        while j < total and rows[j][0] == value:
            j += 1
        avg_index = (i + (j - 1)) / 2.0
        pct = 100.0 * avg_index / (total - 1)
        for _, name in rows[i:j]:
            out[name] = pct
        i = j
    return out


def compute_score_rows(heroes, previous_heroes=None):
    heroes = [h for h in heroes if h.get('name')]
    previous_heroes = previous_heroes or []
    prev_by = {h.get('name'): h for h in previous_heroes if h.get('name')}

    wr = {h['name']: h.get('wr') for h in heroes}
    ban = {h['name']: h.get('ban') for h in heroes}
    pick = {h['name']: h.get('pick') for h in heroes}
    momentum = {}
    for h in heroes:
        p = prev_by.get(h['name'], {})
        dwr = h.get('wr') - p.get('wr') if finite(h.get('wr')) and finite(p.get('wr')) else 0.0
        dp = h.get('pick') - p.get('pick') if finite(h.get('pick')) and finite(p.get('pick')) else 0.0
        db = h.get('ban') - p.get('ban') if finite(h.get('ban')) and finite(p.get('ban')) else 0.0
        momentum[h['name']] = 0.60 * dwr + 0.25 * dp + 0.15 * db

    pwr = percentiles(wr)
    pban = percentiles(ban)
    ppick = percentiles(pick)
    pmom = percentiles(momentum)

    rows = []
    for h in heroes:
        n = h['name']
        score = (
            0.45 * pwr.get(n, 50.0)
            + 0.20 * ppick.get(n, 50.0)
            + 0.20 * pban.get(n, 50.0)
            + 0.15 * pmom.get(n, 50.0)
        )
        score = round(score, 1)
        label = 'Señal muy alta' if score >= 80 else 'Señal alta' if score >= 65 else 'Señal media' if score >= 45 else 'Señal baja'
        rows.append({
            'name': n,
            'score': score,
            'label': label,
            'wr_pct': round(pwr.get(n, 50.0), 1),
            'pick_pct': round(ppick.get(n, 50.0), 1),
            'ban_pct': round(pban.get(n, 50.0), 1),
            'momentum_pct': round(pmom.get(n, 50.0), 1),
            'momentum_raw': round(momentum.get(n, 0.0), 3),
        })
    rows.sort(key=lambda x: (-x['score'], x['name']))
    for i, row in enumerate(rows, 1):
        row['rank'] = i
    return rows


FORMULA = '45% WR percentile + 20% pick percentile + 20% ban percentile + 15% momentum percentile'
MOMENTUM_FORMULA = '60% delta WR + 25% delta pick + 15% delta ban'
