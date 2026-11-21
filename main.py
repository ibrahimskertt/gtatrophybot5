import json, os, glob
from model import forecast, hours

def main():
    indir = os.environ.get('MAKEFUN_INPUT_DIR', '/input')
    outdir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(outdir, exist_ok=True)
    for path in sorted(glob.glob(os.path.join(indir, '*.in'))):
        with open(path) as f:
            case = json.load(f)
        x_t = hours(case['target'])
        hd = case['horizon_minutes'] / 1440.0
        rows = []
        for idx, tr in enumerate(case['trophies']):
            points = [(hours(rd['at']), rd['rates'][idx]) for rd in case['history'] if rd['rates'][idx] is not None]
            if not points:
                points = [(0.0, 0.01)]
            rows.append({'id': tr['id'], 'q': forecast(points, tr['tier'], x_t, hd)})
        out_path = os.path.join(outdir, case['id'] + '.out')
        with open(out_path, 'w') as f:
            f.write(json.dumps({'trophies': rows}, separators=(',', ':')))
if __name__ == '__main__':
    main()
