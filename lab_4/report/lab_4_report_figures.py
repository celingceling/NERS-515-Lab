#!/usr/bin/env python3
"""NERS 515 Lab 4 report: all numbers, figures and LaTeX table snippets.

Decisions used (from Celing):
  * Calibration from Lab 2 (channel = 765.8 V + 27.6) written as V = -36.0 mV + 1.31 mV * n; sigma_V = 25.4 mV (Lab 2).
  * Scope: dead time 360 us, interval after dead time 480 us, from initial pulse 840 us.
  * No line fitting. Slopes from two-point/group means, errors by Knoll Eq. 3.37.
  * Pb absorbers and the source-rate comparison are not used.
Run from this folder:  python3 lab_4_report_figures.py
"""
import csv, json, math, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
D = lambda *p: os.path.join(HERE, *p)
os.makedirs(D("figures"), exist_ok=True)
os.makedirs(D("tables"), exist_ok=True)

# ----------------------------------------------------------------- constants
CAL_SLOPE = 765.8      # channels per volt (Lab 2)
CAL_OFFSET_MV, CAL_SLOPE_MV = -36.0, 1.31   # V(n) = -36.0 mV + 1.31 mV * n (inverted Lab 2 fit, slope rounded)
CAL_OFFSET = 27.6      # channel at 0 V (Lab 2)
SIG_V = 0.0254         # V, scope amplitude uncertainty from Lab 2
T_MCA = 30.0           # s real time
TAU_SCOPE = 360e-6     # s
T_RECOV_INT = 480e-6   # s
T_RECOV_INIT = 840e-6  # s
CURSOR_SIG = 2e-6      # s, one cursor step
N_EXP = 105.0          # cm2/g read from Knoll Fig. 2.16 (Co-60)
SIG_N_EXP = 10.0
E_CO60 = 0.32          # MeV read from Fig. 2.16 marker
# our power-law reading of the Fig. 2.16 line: E = E10 * (n/10)^(-P)
E10, P_E = 1.47, 0.668
OP_V = 840

C1, C2, C3, GR = "#1f4e79", "#c0504d", "#5b8c3a", "#7f7f7f"
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": 0.25, "figure.dpi": 150,
                     "savefig.bbox": "tight"})


def prop(f, vals, sigs, h=1e-6):
    """Knoll Eq. 3.37 with numerical partial derivatives (independent errors)."""
    vals = np.asarray(vals, float)
    f0 = f(*vals)
    var = 0.0
    for i, s in enumerate(sigs):
        if s == 0:
            continue
        d = np.array(vals)
        step = h * max(abs(vals[i]), 1.0)
        d[i] += step
        var += ((f(*d) - f0) / step * s) ** 2
    return f0, math.sqrt(var)


def read(name):
    with open(D("data", name)) as fh:
        return list(csv.DictReader(fh))


def tex(name, s):
    with open(D("tables", name), "w") as fh:
        fh.write(s)


def fmt(x, s, nd=2):
    """value $\\pm$ error with the same number of decimals"""
    return f"{x:.{nd}f} $\\pm$ {s:.{nd}f}"


R = {}  # everything we quote

# ================================================================ counting curve
cc = read("counting_curve.csv")
HV = np.array([float(r["HV"]) for r in cc])
N = np.array([float(r["Counts"]) for r in cc])
PH = np.array([float(r["PH"]) for r in cc])
dPH = np.array([float(r["dPH"]) for r in cc])
TC = 3.0
rate = N / TC
srate = np.sqrt(N) / TC

# plateau slope: group sums (Knoll Eq. 3.42) at both ends of 730-890 V
g1 = (HV >= 730) & (HV <= 770)
g2 = (HV >= 850) & (HV <= 890)
N1, N2 = N[g1].sum(), N[g2].sum()
T1, T2 = TC * g1.sum(), TC * g2.sum()
r1, s1 = N1 / T1, math.sqrt(N1) / T1
r2, s2 = N2 / T2, math.sqrt(N2) / T2
V1, V2 = HV[g1].mean(), HV[g2].mean()
slope = (r2 - r1) / (V2 - V1)
sslope = math.hypot(s1, s2) / (V2 - V1)
pct = 100 * slope * 100 / r1
spct = 100 * sslope * 100 / r1
R["plateau"] = dict(r1=r1, s1=s1, r2=r2, s2=s2, V1=V1, V2=V2, slope=slope, sslope=sslope,
                    pct=pct, spct=spct, N1=int(N1), N2=int(N2), T1=T1, T2=T2)
i830, i850 = list(HV).index(830), list(HV).index(850)
R["rate830"], R["rate850"] = (rate[i830], srate[i830]), (rate[i850], srate[i850])
R["rate910"] = (rate[-1], srate[-1])
R["rate710"] = (rate[3], srate[3])
R["rate670"] = (rate[1], srate[1])

# pulse height in volts for table; local ratio PH(910)/PH(690)
R["ph_ratio_890_690"] = PH[HV == 890][0] / PH[HV == 690][0]

# Table: HV, counts, rate, PH (raw columns go to Data)
rows = []
for h, n, r, s, p, dp in zip(HV, N, rate, srate, PH, dPH):
    rows.append(f"{h:.0f} & {r:.1f} $\\pm$ {s:.1f} \\\\")
tex("t_rate.tex", "\n".join(rows) + "\n")
half = (len(HV) + 1) // 2
rows2 = []
for i in range(half):
    j = i + half
    left = f"{HV[i]:.0f} & {rate[i]:.1f} $\\pm$ {srate[i]:.1f}"
    right = f"{HV[j]:.0f} & {rate[j]:.1f} $\\pm$ {srate[j]:.1f}" if j < len(HV) else " & "
    rows2.append(left + " & " + right + " \\\\")
tex("t_rate2.tex", "\n".join(rows2) + "\n")
rows = []
for h, p, dp in zip(HV, PH, dPH):
    rows.append(f"{h:.0f} & {p:.2f} & {dp:.2f} \\\\")
_h = (len(HV) + 1) // 2
_rows = []
for i in range(_h):
    j = i + _h
    l = f"{HV[i]:.0f} & {N[i]:.0f} & {PH[i]:g} $\\pm$ {dPH[i]:g}"
    r = f"{HV[j]:.0f} & {N[j]:.0f} & {PH[j]:g} $\\pm$ {dPH[j]:g}" if j < len(HV) else " & & "
    _rows.append(l + " & " + r + " \\\\")
tex("t_raw_cc.tex", "\n".join(_rows) + "\n")

# Figure A: pulse height vs HV
fig, ax = plt.subplots(figsize=(3.3, 2.7))
ax.errorbar(HV, PH, yerr=dPH, fmt="o", ms=4, color=C1, ecolor=C1, capsize=2, lw=1)
ax.set_xlabel("High voltage (V)")
ax.set_ylabel("Pre-amp pulse height (mV)")
fig.savefig(D("figures", "A_pulse_height_vs_hv.pdf"))
plt.close(fig)

# Figure B: counting curve
fig, ax = plt.subplots(figsize=(3.3, 2.7))
m0 = N > 0
ax.errorbar(HV[m0], rate[m0], yerr=srate[m0], fmt="o", ms=4, color=C1, capsize=2, lw=1, label="counts")
ax.errorbar(HV[~m0], rate[~m0], yerr=0, fmt="o", ms=4, mfc="white", color=C1, label="")
# 670 V: hollow (noise, no pulse on scope)
ax.errorbar([670], [rate[1]], yerr=[srate[1]], fmt="o", ms=4, mfc="white", color=C1, capsize=2, lw=1)
ax.axvspan(730, 890, color=GR, alpha=0.12, lw=0)
ax.axvline(OP_V, color=C2, lw=1, ls="--")
ax.text(OP_V + 4, 12, "840 V", color="#222", fontsize=8, rotation=90, va="bottom")
ax.set_xlabel("High voltage (V)")
ax.set_ylabel("Count rate (s$^{-1}$)")
ax.set_ylim(0, 105)
fig.savefig(D("figures", "B_counting_curve.pdf"))
plt.close(fig)

# ================================================================ consistency
pc = read("pulse_height_consistency.csv")
cons = []
for r in pc:
    n = float(r["centroid_channel"])
    g = float(r["gross_counts"])
    v = (CAL_OFFSET_MV + CAL_SLOPE_MV * n) / 1000.0   # same formula as the user's figure script
    rt, srt = g / T_MCA, math.sqrt(g) / T_MCA
    cons.append(dict(src=r["source"], ch=n, V=v, sV=SIG_V, G=g, rate=rt, srate=srt))
R["cons"] = cons
rows = []
for c in cons:
    rows.append(f"{c['src']} & {c['ch']:.0f} & {c['G']:.0f} & {T_MCA:.0f} \\\\")
tex("t_raw_cons.tex", "\n".join(rows) + "\n")
rows = []
for c in cons:
    rows.append(f"{c['src']} & {c['V']:.2f} $\\pm$ {c['sV']:.2f} & {c['rate']:.0f} $\\pm$ {c['srate']:.0f} \\\\")
tex("t_cons.tex", "\n".join(rows) + "\n")

fig, ax = plt.subplots(figsize=(3.3, 2.7))
mk = {"Co-60": "o", "C-14": "s", "Cl-36": "^"}
for c in cons:
    ax.errorbar(c["rate"], c["V"], xerr=c["srate"], yerr=c["sV"], fmt=mk[c["src"]], ms=6,
                color=C1, capsize=2, lw=1)
    ax.annotate(c["src"], (c["rate"], c["V"]), textcoords="offset points", xytext=(6, 5), fontsize=8)
ax.set_xlabel("Count rate (s$^{-1}$)")
ax.set_ylabel("Pulse amplitude (V)")
ax.set_xlim(0, 540)
ax.set_ylim(2.0, 5.0)
fig.savefig(D("figures", "C_pulse_height_consistency.pdf"))
plt.close(fig)

# ================================================================ beta attenuation
ba = read("beta_attenuation.csv")
t_mg = np.array([float(r["t_mgcm2"]) for r in ba])
Nb = np.array([float(r["Counts"]) for r in ba])
Tb = np.array([float(r["Time"]) for r in ba])
Bn, Bt = Nb[0], Tb[0]
Brate, sBrate = Bn / Bt, math.sqrt(Bn) / Bt
R["bkg"] = (Brate, sBrate)
# rows 1..8
t = t_mg[1:] / 1000.0           # g/cm2
Ng, Tg = Nb[1:], Tb[1:]
gross = Ng / Tg
sgross = np.sqrt(Ng) / Tg
rnet = gross - Brate
srnet = np.sqrt(sgross ** 2 + sBrate ** 2)     # Knoll Eqs. 3.52-3.53
lnr = np.log(rnet)
slnr = srnet / rnet
st = 0.10 * t                                    # manual: 10 % of thickness
R["beta"] = dict(t=t.tolist(), rnet=rnet.tolist(), srnet=srnet.tolist())

rows_raw, rows_net = [], []
for i, (tm, n, ti) in enumerate(zip(t_mg[1:], Ng, Tg)):
    rows_raw.append(f"Al & {tm:.2f} & {n:.0f} & {ti:.0f} \\\\")
tex("t_raw_beta.tex", "\n".join(rows_raw) + "\n")

# n from consecutive pairs (Eq. 2.14 two points, Eq. 3.37 errors)
def n_pair(ra, rb, ta, tb_, sra, srb, sta, stb):
    f = lambda ra, rb, ta, tb_: math.log(ra / rb) / (tb_ - ta)
    return prop(f, [ra, rb, ta, tb_], [sra, srb, sta, stb])

pairs = []
for i in range(len(t) - 1):
    v, s = n_pair(rnet[i], rnet[i + 1], t[i], t[i + 1], srnet[i], srnet[i + 1], st[i], st[i + 1])
    pairs.append((t_mg[1 + i], t_mg[2 + i], v, s))
R["pairs"] = pairs
for i in range(len(t)):
    ncol = f"{pairs[i][2]:.1f} $\\pm$ {pairs[i][3]:.1f}" if i < len(pairs) else "-"
    rows_net.append(f"{t_mg[1+i]:.1f} & {gross[i]:.2f} $\\pm$ {sgross[i]:.2f} & {rnet[i]:.1f} $\\pm$ {srnet[i]:.1f} "
                    f"& {lnr[i]:.2f} $\\pm$ {slnr[i]:.2f} \\\\")
tex("t_net_beta.tex", "\n".join(rows_net) + "\n")
tex("t_pairs.tex", "\n".join(
    f"{a:.1f}$\\to${b:.1f} & {v:.1f} $\\pm$ {s:.1f} \\\\" for a, b, v, s in pairs) + "\n")
n12, sn12 = pairs[0][2], pairs[0][3]
R["n12"] = (n12, sn12)
# endpoint energy from our reading of Fig 2.16
fE = lambda n: E10 * (n / 10.0) ** (-P_E)
E12, sE12 = prop(fE, [n12], [sn12])
Eexp, sEexp = prop(fE, [N_EXP], [SIG_N_EXP])
R["E12"], R["Eexp"] = (E12, sE12), (Eexp, sEexp)
R["n_ratio"] = N_EXP / n12

# weighted averages (Knoll Eqs. 3.45-3.51) for the flat parts
def wavg(idx):
    w = 1 / srnet[idx] ** 2
    m = (w * rnet[idx]).sum() / w.sum()
    s = 1 / math.sqrt(w.sum())
    return m, s
R["tail_a"] = wavg(slice(2, 6))     # 177-843 mg/cm2
R["tail_b"] = wavg(slice(6, 8))     # 1279-1541 mg/cm2

fig, ax = plt.subplots(figsize=(5.2, 3.3))
ax.errorbar(t_mg[1:], lnr, xerr=0.10 * t_mg[1:], yerr=slnr, fmt="o", ms=4, color=C1, capsize=2, lw=1,
            label="net rate (Al)")
tt = np.linspace(0, 1.6, 200)
l12 = math.log(rnet[0]) - n12 * (tt - t[0])
ax.plot(tt * 1000, l12, color=C2, lw=1.2, label=f"through first two points, n = {n12:.0f} cm$^2$/g")
lexp = math.log(rnet[0]) - N_EXP * (tt - t[0])
ax.plot(tt * 1000, lexp, color=GR, lw=1.2, ls="--", label=f"expected n = {N_EXP:.0f} cm$^2$/g (Fig. 2.16), same start")
ax.set_ylim(0.8, 4.6)
ax.set_xlim(0, 1650)
ax.set_xlabel("Al mass thickness (mg/cm$^2$)")
ax.set_ylabel("ln(net rate / s$^{-1}$)")
ax.legend(fontsize=7, frameon=False, loc="upper right")
fig.savefig(D("figures", "D_beta_attenuation_ln.pdf"))
plt.close(fig)

# ================================================================ dead time
ts = read("two_source_dead_time.csv")
T = 10.0
runs = []

def tau_f(b, a, c, ab):
    """counts -> tau (Knoll Eqs. 4.30-4.32); a = Th-232, c = Cl-36, ab = both."""
    mb, m1, m2, m12 = b / T, a / T, c / T, ab / T
    X = m1 * m2 - mb * m12
    Y = m1 * m2 * (m12 + mb) - mb * m12 * (m1 + m2)
    Z = Y * (m1 + m2 - m12 - mb) / X ** 2
    return X * (1 - math.sqrt(1 - Z)) / Y

def Z_f(b, a, c, ab):
    mb, m1, m2, m12 = b / T, a / T, c / T, ab / T
    X = m1 * m2 - mb * m12
    Y = m1 * m2 * (m12 + mb) - mb * m12 * (m1 + m2)
    return Y * (m1 + m2 - m12 - mb) / X ** 2

for r in ts:
    b, a, c, ab = (float(r["Background"]), float(r["Th-232"]), float(r["Cl-36"]), float(r["Both"]))
    tau, stau = prop(tau_f, [b, a, c, ab], [math.sqrt(max(b, 1)), math.sqrt(a), math.sqrt(c), math.sqrt(ab)])
    Z = Z_f(b, a, c, ab)
    # predicted m12 at the scope tau
    tau0 = TAU_SCOPE
    def pred_np(b, a, c, ab):
        mb, m1, m2 = b / T, a / T, c / T
        n1, n2, nb = m1 / (1 - m1 * tau0), m2 / (1 - m2 * tau0), mb / (1 - mb * tau0)
        n12 = n1 + n2 - nb
        return n12 / (1 + n12 * tau0)
    def pred_p(b, a, c, ab):
        mb, m1, m2 = b / T, a / T, c / T
        from scipy.optimize import brentq
        inv = lambda m: brentq(lambda n: n * math.exp(-n * tau0) - m, m, 1.0 / tau0)
        n12 = inv(m1) + inv(m2) - inv(mb) if mb > 0 else inv(m1) + inv(m2)
        return n12 * math.exp(-n12 * tau0)
    pnp, spnp = prop(pred_np, [b, a, c, ab], [math.sqrt(max(b, 1)), math.sqrt(a), math.sqrt(c), 0])
    pp, spp = prop(pred_p, [b, a, c, ab], [math.sqrt(max(b, 1)), math.sqrt(a), math.sqrt(c), 0], h=1e-4)
    runs.append(dict(b=b, a=a, c=c, ab=ab, tau=tau, stau=stau, Z=Z, m12=ab / T, sm12=math.sqrt(ab) / T,
                     m12tau=ab / T * tau, pnp=pnp, spnp=spnp, pp=pp, spp=spp,
                     csv_tau=float(list(r.values())[4])))
R["runs"] = runs
taus = np.array([r["tau"] for r in runs])
mean = taus.mean()
sd = taus.std(ddof=1)
sem = sd / math.sqrt(len(taus))
R["tau_mean"], R["tau_sd"], R["tau_sem"] = mean, sd, sem
# pooled counts
pb, pa, pcc, pab = (sum(r[k] for r in runs) for k in ("b", "a", "c", "ab"))
ptau, pstau = prop(tau_f, [pb / 3, pa / 3, pcc / 3, pab / 3],
                   [math.sqrt(pb) / 3, math.sqrt(pa) / 3, math.sqrt(pcc) / 3, math.sqrt(pab) / 3])
R["tau_pooled"] = (ptau, pstau)
# scope vs two-source
R["scope_vs_mean_sigma"] = (mean - TAU_SCOPE) / sem
R["limit_rate"] = (1 / TAU_SCOPE, 1 / (math.e * TAU_SCOPE))

# scope readings
R["scope"] = dict(dead=TAU_SCOPE * 1e6, dead_s=math.hypot(CURSOR_SIG, CURSOR_SIG) * 1e6,
                  interval=T_RECOV_INT * 1e6, init=T_RECOV_INIT * 1e6)

rows = []
for i, r in enumerate(runs, 1):
    rows.append(f"{i} & {r['b']:.0f} & {r['a']:.0f} & {r['c']:.0f} & {r['ab']:.0f} \\\\")
tex("t_raw_two.tex", "\n".join(rows) + "\n")
rows = []
for i, r in enumerate(runs, 1):
    rows.append(f"{i} & {r['tau']*1e6:.0f} $\\pm$ {r['stau']*1e6:.0f} \\\\")
rows.append(f"Mean $\\pm$ SEM & {mean*1e6:.0f} $\\pm$ {sem*1e6:.0f} \\\\")
tex("t_tau.tex", "\n".join(rows) + "\n")
rows = []
for i, r in enumerate(runs, 1):
    rows.append(f"{i} & {r['m12']:.1f} $\\pm$ {r['sm12']:.1f} & {r['pnp']:.1f} $\\pm$ {r['spnp']:.1f} & {r['pp']:.1f} $\\pm$ {r['spp']:.1f} \\\\")
tex("t_pred.tex", "\n".join(rows) + "\n")

# Figure E: tau per run with scope band
fig, ax = plt.subplots(figsize=(3.3, 2.7))
x = np.arange(1, 4)
ax.errorbar(x, taus * 1e6, yerr=[r["stau"] * 1e6 for r in runs], fmt="o", ms=5, color=C1, capsize=3, lw=1,
            label="two-source, each run")
ax.axhspan(mean * 1e6 - sem * 1e6, mean * 1e6 + sem * 1e6, color=C1, alpha=0.12, lw=0)
ax.axhline(mean * 1e6, color=C1, lw=1, ls=":", label="two-source mean $\\pm$ SEM")
ax.axhline(360, color=C2, lw=1.2, label="scope dead time (360 $\\mu$s)")
ax.set_xticks(x)
ax.set_xlim(0.5, 3.5)
ax.set_ylim(-500, 2300)
ax.set_xlabel("Run")
ax.set_ylabel("Dead time $\\tau$ ($\\mu$s)")
ax.legend(fontsize=7, frameon=False, loc="upper left", ncol=1)
fig.savefig(D("figures", "E_tau_per_run.pdf"))
plt.close(fig)

# ------------------------------------------------------------ macros for the .tex
M = {}
def mac(k, v):
    M[k] = v
P = R["plateau"]
mac("rOneA", f"{P['r1']:.1f}"); mac("srOneA", f"{P['s1']:.1f}")
mac("rTwoA", f"{P['r2']:.1f}"); mac("srTwoA", f"{P['s2']:.1f}")
mac("NoneA", f"{P['N1']}"); mac("NtwoA", f"{P['N2']}")
mac("pSlope", f"{P['slope']:.3f}"); mac("spSlope", f"{P['sslope']:.3f}")
mac("pPct", f"{P['pct']:.1f}"); mac("spPct", f"{P['spct']:.1f}")
mac("rEightThirty", f"{R['rate830'][0]:.1f}"); mac("srEightThirty", f"{R['rate830'][1]:.1f}")
mac("rEightFifty", f"{R['rate850'][0]:.1f}"); mac("srEightFifty", f"{R['rate850'][1]:.1f}")
mac("rNineTen", f"{R['rate910'][0]:.1f}"); mac("srNineTen", f"{R['rate910'][1]:.1f}")
mac("rSevenTen", f"{R['rate710'][0]:.1f}"); mac("srSevenTen", f"{R['rate710'][1]:.1f}")
mac("rSixSeventy", f"{R['rate670'][0]:.1f}"); mac("srSixSeventy", f"{R['rate670'][1]:.1f}")
i690 = list(HV).index(690)
mac("rSixNinety", f"{rate[i690]:.1f}"); mac("srSixNinety", f"{srate[i690]:.1f}")
mac("phRatio", f"{R['ph_ratio_890_690']:.0f}")
c0 = cons[0]
mac("coV", f"{c0['V']:.2f}"); mac("coRate", f"{c0['rate']:.1f}"); mac("scoRate", f"{c0['srate']:.1f}")
mac("coCh", f"{c0['ch']:.0f}"); mac("coG", f"{c0['G']:.0f}")
mac("bkgR", f"{Brate:.1f}"); mac("sbkgR", f"{sBrate:.2f}")
mac("grossA", f"{gross[0]:.1f}"); mac("sgrossA", f"{sgross[0]:.1f}")
mac("netA", f"{rnet[0]:.1f}"); mac("snetA", f"{srnet[0]:.1f}")
mac("lnA", f"{lnr[0]:.2f}"); mac("slnA", f"{slnr[0]:.3f}")
mac("netB", f"{rnet[1]:.1f}"); mac("snetB", f"{srnet[1]:.1f}")
mac("lnRatio", f"{math.log(rnet[0]/rnet[1]):.3f}")
mac("dtAB", f"{t[1]-t[0]:.5f}")
mac("nTwo", f"{n12:.1f}"); mac("snTwo", f"{sn12:.1f}")
mac("nExp", f"{N_EXP:.0f}"); mac("snExp", f"{SIG_N_EXP:.0f}")
mac("nRatio", f"{R['n_ratio']:.1f}")
mac("EMeas", f"{E12:.2f}"); mac("sEMeas", f"{sE12:.2f}")
mac("EExpFit", f"{Eexp:.2f}"); mac("EFig", f"{E_CO60:.2f}")
mac("tailA", f"{R['tail_a'][0]:.1f}"); mac("stailA", f"{R['tail_a'][1]:.1f}")
mac("tailB", f"{R['tail_b'][0]:.1f}"); mac("stailB", f"{R['tail_b'][1]:.1f}")
r0 = runs[0]
mb_, m1_, m2_, m12_ = r0["b"]/T, r0["a"]/T, r0["c"]/T, r0["ab"]/T
X_ = m1_*m2_ - mb_*m12_
Y_ = m1_*m2_*(m12_+mb_) - mb_*m12_*(m1_+m2_)
mac("sMb", f"{mb_:.1f}"); mac("sMone", f"{m1_:.1f}"); mac("sMtwo", f"{m2_:.1f}"); mac("sMonetwo", f"{m12_:.1f}")
mac("sX", f"{X_:.0f}"); mac("sY", f"{Y_/1e5:.2f}\\times10^{{5}}"); mac("sZ", f"{r0['Z']:.3f}")
mac("sTau", f"{r0['tau']*1e6:.0f}"); mac("ssTau", f"{r0['stau']*1e6:.0f}")
mac("tauMean", f"{mean*1e6:.0f}"); mac("tauSD", f"{sd*1e6:.0f}"); mac("tauSEM", f"{sem*1e6:.0f}")
mac("tauPool", f"{ptau*1e6:.0f}"); mac("stauPool", f"{pstau*1e6:.0f}")
mac("nSigScope", f"{R['scope_vs_mean_sigma']:.1f}")
mac("limA", f"{R['limit_rate'][0]:.0f}"); mac("limB", f"{R['limit_rate'][1]:.0f}")
mac("sDead", "360"); mac("ssDead", "3"); mac("sInt", "480"); mac("sInit", "840")
with open(D("tables", "macros.tex"), "w") as fh:
    for k, v in M.items():
        fh.write("\\newcommand{\\" + k + "}{" + str(v) + "}\n")

with open(D("results.json"), "w") as fh:
    json.dump(R, fh, indent=1, default=float)
print(json.dumps(R, indent=1, default=float))
