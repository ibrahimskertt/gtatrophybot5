import math
from datetime import datetime, timezone

RELEASE = datetime(2026, 11, 19, tzinfo=timezone.utc)
Z = [-1.644854, -0.674490, 0.0, 0.674490, 1.644854]
PRIOR = {'platinum': 0.55, 'gold': 0.75, 'silver': 0.90, 'bronze': 1.00}

def clamp(v, lo, hi):
    return max(lo, min(v, hi))

def logit(rate):
    r = clamp(rate, 0.01, 99.99)
    p = r / 100.0
    return math.log(p / (1 - p))

def inv_logit(l):
    return 100.0 / (1.0 + math.exp(-l))

def hours(ts):
    iso = ts.rstrip('Z')
    if ts.endswith('Z'):
        iso += '+00:00'
    dt = datetime.fromisoformat(iso)
    return (dt - RELEASE).total_seconds() / 3600.0

def wls(u, y, w):
    swuu = sum(wi * ui * ui for wi, ui in zip(w, u))
    if swuu == 0:
        return 0.0, 0.0
    swuy = sum(wi * ui * yi for wi, ui, yi in zip(w, u, y))
    slope = swuy / swuu
    resid = [yi - slope * ui for ui, yi in zip(u, y)]
    sw = sum(w)
    rms = math.sqrt(sum(wi * ri * ri for wi, ri in zip(w, resid)) / sw) if sw else 0.0
    return slope, rms

def forecast(points, tier, x_t, horizon_days):
    xs, rates = zip(*points)
    x_last, r_last = xs[-1], rates[-1]
    if len(points) < 3 or all(r == rates[0] for r in rates):
        b = PRIOR[tier]
        b = clamp(b, -0.5, 2.5)
        s_fit = 0.30
    else:
        u = [math.log(1 + x) for x in xs]
        y = [logit(r) for r in rates]
        w = [1 + (x / x_last if x_last > 0 else 0) for x in xs]
        slope, rms = wls(u, y, w)
        s_fit = max(rms, 0.30)
        b = 0.65 * slope + 0.35 * PRIOR[tier]
        b = clamp(b, -0.5, 2.5)
    g = b * (math.log(1 + x_t) - math.log(1 + x_last))
    damp = 1.0 / (1.0 + math.exp((r_last - 50.0) / 12.0))
    med = logit(r_last) + g * (0.35 + 0.65 * damp)
    rate = inv_logit(med)
    if r_last < 20.0:
        bound = min(99.5, max(r_last * 8.0, r_last + 12.0))
        rate = min(rate, bound)
    lo = max(0.01, r_last * 0.25)
    rate = clamp(rate, lo, 99.99)
    med = logit(rate)
    s = math.sqrt((0.5 * math.sqrt(horizon_days)) ** 2 + (0.6 * s_fit) ** 2 + 0.22 ** 2)
    qs = [round(clamp(inv_logit(med + z * s), 0.01, 99.99), 4) for z in Z]
    for i in range(1, len(qs)):
        if qs[i] < qs[i - 1]:
            qs[i] = qs[i - 1]
    return qs
