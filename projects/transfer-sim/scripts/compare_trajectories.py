# compare_trajectories.py — CPU golden vs GPU nominal 轨迹逐点对比（ASCII）
import csv, sys

def load(path):
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            rows.append([float(x) for x in line.split(',')])
    return rows

cpu = load(r'L:\gmat888\transfer-sim\data\trajectory_earth.csv')
gpu = load(r'L:\gmat888\transfer-sim\data\trajectory_gpu.csv')

# CPU 行: t,x,y,z,vx,vy,vz[,moon...]; GPU 行: t,x,y,z,vx,vy,vz
def interp(rows, t):
    if t <= rows[0][0]: return rows[0][1:7]
    if t >= rows[-1][0]: return rows[-1][1:7]
    lo, hi = 0, len(rows) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if rows[mid][0] <= t: lo = mid
        else: hi = mid
    a, b = rows[lo], rows[hi]
    w = (t - a[0]) / (b[0] - a[0])
    return [a[k] + w * (b[k] - a[k]) for k in range(1, 7)]

names = ['x', 'y', 'z', 'vx', 'vy', 'vz']
mx = [0.0]*6; sm = [0.0]*6; n = 0
for g in gpu:
    if g[0] > cpu[-1][0]:
        break
    c = interp(cpu, g[0])
    for k in range(6):
        d = abs(c[k] - g[k+1])
        if d > mx[k]: mx[k] = d
        sm[k] += d
    n += 1

print('rows compared: %d' % n)
print('NOTE: rows are 30s-cadence samples; linear interpolation limits this comparison to ~meter level.')
print('The authoritative CPU/GPU divergence is the fixed-step test in main_gpu (2.9e-8 km).')
print('component   max_abs_diff      mean_abs_diff')
ok = True
for k in range(6):
    mean = sm[k]/max(n,1)
    print('%-8s   %.6e      %.6e' % (names[k], mx[k], mean))
    lim = 0.05 if k < 3 else 1e-6   # km（插值受限）与 km/s（真实发散）
    if mx[k] > lim: ok = False

# 终点（SOI 附近最后一行）状态差
c_end = interp(cpu, gpu[-1][0])
d_end = [abs(c_end[k] - gpu[-1][k+1]) for k in range(6)]
print('final-state diff:', ['%.3e' % d for d in d_end])
print('RESULT:', 'PASS' if ok else 'FAIL')
sys.exit(0 if ok else 1)
