"""
NERS 515 Lab 5 (proportional counter): every plot, number and table for the report.

Run from anywhere:  python lab_5_plots.py
Reads   data/Lab 5 - 2. Shaping time.csv, data/Lab 5 - 2. Counting Curve - Alpha.csv,
        data/Lab 5 - 2. Counting Curve - Beta.csv, data/Lab 5 - 3. Counting Efficiency.csv,
        data/Lab 5 - 4. Gamma Response, .csv
Writes  figures/*.png + *.pdf, tables/*.tex, results_summary.txt, results_summary.csv

Sources for formulas: Knoll 4th ed., the lecture slides, and the Lab 5 manual only.
Equation numbers are Knoll's (4th ed.). Judgment calls are the named settings below.
Needs numpy, pandas, matplotlib.
"""
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
FIG_DIR = ROOT / "figures"
TAB_DIR = ROOT / "tables"
SHAPING_CSV = DATA_DIR / "Lab 5 - 2. Shaping time.csv"
ALPHA_CSV = DATA_DIR / "Lab 5 - 2. Counting Curve - Alpha.csv"
BETA_CSV = DATA_DIR / "Lab 5 - 2. Counting Curve - Beta.csv"
EFF_CSV = DATA_DIR / "Lab 5 - 3. Counting Efficiency.csv"
GAMMA_CSV = DATA_DIR / "Lab 5 - 4. Gamma Response, .csv"

# ---- measured constants (data files / notebook / manual) ------------------
T_ALPHA = 30.0                   # s per alpha counting-curve point (rate column = counts/30)
T_BETA = 30.0                    # s per beta point (CSV header "30s time intervals")
T_GAMMA = 30.0                   # s per gamma point
LLD_ALPHA, LLD_BETA, LLD_GAMMA = 1738, 307, 229      # channels (CSV headers)
E_AM241_KEV = 5486.0             # keV, main Am-241 alpha group (Knoll Table 1.3, p. 8)
CAL_SHAPING_US = 3.0             # us, shaping-time run used for the one-point calibration
BD_REF_US = 10.0                 # us, reference shaping time for the ballistic deficit
EFF_COUNTS, EFF_TIME = 1428191, 60.0                 # efficiency run (parsed by hand from CSV)
EFF_RATE_UCI_CSV = 0.6433        # CSV "count rate (uC)" = rate / 3.7e4
A0_UCI = 1.032                   # uCi, marked Cl-36 activity ("Original" row)
A0_DATE = date(2026, 8, 1)       # date in the efficiency CSV
UCI_TO_BQ = 3.7e4                # 1 Ci = 3.7e10 s^-1 (Knoll p. 2)
T_HALF_CL36_Y = 3.08e5           # y (Knoll Table 1.1, p. 4)
V_EFF = 1500                     # V, efficiency-run voltage (chosen from the beta plateau)

# ---- judgment calls: named settings (printed at run time; confirm before locking) ----
SHOW_TITLES = False              # captions carry the titles
SIGMA_CENTROID = 1.0             # channels; upper bound on sigma_c = FWHM/2.35/sqrt(A) (Knoll p. 728)
AREA_10US_METHOD = "line through 3 and 6 us"         # extrapolation of the blank 10 us peak area
V_SHAPING_CHOSEN = 3.0           # us, dashed line in F1 (centroid levels off)
PLATEAU_START = 1000             # V, last alpha point before the 1050 V drop
ALPHA_DROP_V = 1050              # V, drawn hollow, excluded from the plateau
AMPLITUDE_POINTS = [900, 1000]   # V, filled points in F3 (peak clearly above the LLD)
AMPLITUDE_LOW = list(range(500, 851))                # V range of the LLD-limited centroids
SHOW_LOW_AMPLITUDE = False       # False: leave 500-850 V out of F3; True: faint hollow (ASK)
GAMMA_SOURCE = "Co-60 gamma"     # legend label
A0_REL_UNC = 0.0                 # relative uncertainty of the marked activity (none stated: ASK)
MEAS_DATE = None                 # date of the efficiency run; None = no decay (not recorded: ASK)
F5_LOG_Y = True                  # beta and gamma together on a log rate axis

# ---- plot style (copied from lab_4_plots.py) ------------------------------
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e3e2de"
BLUE, ORANGE, GRAY = "#2a78d6", "#eb6834", "#8a8984"
GREEN, PURPLE, BLACK = "#009E73", "#CC79A7", "#000000"   # Okabe-Ito additions (colorblind safe)
FONT = 9
W_HALF, W_FULL = 3.5, 7.0       # inches; half-page and full-page figure widths
plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "axes.edgecolor": INK2, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False,
    "font.size": FONT, "axes.titlesize": FONT, "axes.titleweight": "bold",
    "axes.labelsize": FONT, "xtick.labelsize": FONT, "ytick.labelsize": FONT,
    "legend.fontsize": FONT, "lines.linewidth": 1.6, "lines.markersize": 5,
    "savefig.facecolor": SURFACE,
})

RESULTS = []   # (name, value, uncertainty, unit, source)


def R(name, value, unc=None, unit="", src=""):
    """Register a number for the printed summary and results_summary.{txt,csv}."""
    RESULTS.append((name, value, unc, unit, src))


def title(ax, text):
    if SHOW_TITLES:
        ax.set_title(text)


def leg(ax, loc):
    """Short in-plot legend; details go in the figure caption."""
    ax.legend(loc=loc, frameon=True, framealpha=0.9, edgecolor="none", handlelength=1.6,
              borderpad=0.3, labelspacing=0.25, borderaxespad=0.3)


def save(fig, name):
    FIG_DIR.mkdir(exist_ok=True)
    fig.savefig(FIG_DIR / f"{name}.png", dpi=200)
    fig.savefig(FIG_DIR / f"{name}.pdf")


# MCA channel -> pulse amplitude, Lab 2 calibration: channel = 765.8 V + 27.6 (our Lab 2 report)
CAL_SLOPE, CAL_INT = 765.8, 27.6


def volt_axis(ax, log=False):
    """Right-hand axis: MCA channel converted to amplitude (V) with the Lab 2 calibration."""
    sec = ax.secondary_yaxis("right", functions=(lambda c: (np.asarray(c) - CAL_INT) / CAL_SLOPE,
                                                 lambda v: CAL_SLOPE * np.asarray(v) + CAL_INT))
    sec.set_ylabel("amplitude (V)")
    if log:
        sec.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:g}"))
        sec.yaxis.set_minor_formatter(plt.FuncFormatter(lambda v, _: f"{v:.1f}"))
    return sec


def rates(counts, t):
    """r = N/t, sigma_r = sqrt(N)/t (Knoll Eq. 3.40, p. 88; sigma_N = sqrt(N))."""
    counts = np.asarray(counts, float)
    return counts / t, np.sqrt(counts) / t


# =========================================================================
# Fitting (kept from Lab 4; not used for any drawn line in Lab 5)
# =========================================================================
def weighted_line_fit(x, y, sy, sx, n_iter=50):
    """Fit y = a + b x with effective variance sy^2 + (b*sx)^2 (Eq. 3.37).

    Returns a, b, covariance matrix, chi2, ndf.
    """
    b = 0.0
    for _ in range(n_iter):
        w = 1.0 / (sy**2 + (b * sx) ** 2)
        A = np.vstack([np.ones_like(x), x]).T
        cov = np.linalg.inv(A.T @ (A * w[:, None]))
        a, b_new = cov @ (A.T @ (w * y))
        if abs(b_new - b) < 1e-12:
            b = b_new
            break
        b = b_new
    w = 1.0 / (sy**2 + (b * sx) ** 2)
    chi2 = float(np.sum(w * (y - (a + b * x)) ** 2))
    return a, b, cov, chi2, len(x) - 2


# =========================================================================
# Loading
# =========================================================================
def load_shaping():
    d = pd.read_csv(SHAPING_CSV)
    d.columns = ["tau", "c", "area"]
    d["area_est"] = False
    # 10 us area is blank: straight line through the 3 and 6 us areas, evaluated at 10 us
    p3, p6 = d.set_index("tau").loc[3.0, "area"], d.set_index("tau").loc[6.0, "area"]
    a10 = p6 + (p6 - p3) / (6.0 - 3.0) * (10.0 - 6.0)
    blank = d["area"].isna()
    d.loc[blank, "area"] = a10
    d.loc[blank, "area_est"] = True
    d["sc"] = SIGMA_CENTROID
    return d, a10


def load_alpha():
    d = pd.read_csv(ALPHA_CSV)
    d.columns = ["hv", "counts", "c", "rate_csv"]
    d["rate"], d["srate"] = rates(d["counts"], T_ALPHA)
    return d


def load_beta():
    d = pd.read_csv(BETA_CSV)
    d.columns = ["hv", "counts", "c", "rate_csv"]
    d["rate"], d["srate"] = rates(d["counts"], T_BETA)
    return d


def load_gamma():
    d = pd.read_csv(GAMMA_CSV)
    d = d.iloc[:, :2]
    d.columns = ["hv", "counts"]
    d["rate"], d["srate"] = rates(d["counts"], T_GAMMA)
    return d


# =========================================================================
# F1. Centroid vs shaping time
# =========================================================================
def plot_shaping(d, a10):
    """F1. Peak centroid vs shaping time, +/- SIGMA_CENTROID error bars (sigma_c = sigma/sqrt(A),
    sigma = FWHM/2.35, Knoll p. 728), dashed line at the chosen 3 us. Prints the ballistic deficit
    BD = (C10 - C)/C10 x 100 % (Knoll p. 649, Fig. 17.22) with Eq. 3.37 propagation."""
    print("\n--- F1. Centroid vs shaping time ---")
    if d["area_est"].any():
        print(f"10 us peak area blank: estimated by {AREA_10US_METHOD} = {a10:.4g} (ESTIMATED)")
        R("10 us peak area (estimated)", a10, None, "counts", AREA_10US_METHOD)
    # sigma_c = FWHM / (2.35 sqrt(A)) < 1 channel for any FWHM below 2.35 sqrt(A)
    d["fwhm_max"] = 2.35 * np.sqrt(d["area"])
    print(f"sigma_c = FWHM/(2.35 sqrt(A)) (Knoll p. 728); sigma_c < 1 ch whenever FWHM < 2.35 sqrt(A):")
    for r in d.itertuples():
        tag = " (area estimated)" if r.area_est else ""
        print(f"  {r.tau:4g} us: A = {r.area:.4g}{tag}, FWHM limit for sigma_c < 1 ch = {r.fwhm_max:.0f} ch")
    print(f"error bars drawn at SIGMA_CENTROID = {SIGMA_CENTROID:g} ch (upper bound; smaller than the markers)")

    ref = d[d["tau"] == BD_REF_US].iloc[0]
    C10, s10 = ref.c, ref.sc
    d["bd"] = 100 * (C10 - d["c"]) / C10
    # BD = 1 - C/C10: dBD/dC = -1/C10, dBD/dC10 = C/C10^2 (Eq. 3.37)
    d["sbd"] = 100 * np.sqrt((d["sc"] / C10) ** 2 + (d["c"] * s10 / C10**2) ** 2)
    print(f"ballistic deficit relative to {BD_REF_US:g} us (C10 = {C10:.2f}):")
    for r in d.itertuples():
        if r.tau == BD_REF_US:
            continue
        print(f"  {r.tau:4g} us: C = {r.c:.2f}, BD = {r.bd:.2f} +/- {r.sbd:.2f} %")
        R(f"ballistic deficit at {r.tau:g} us", r.bd, r.sbd, "%", "(C10-C)/C10, Knoll p. 649; Eq. 3.37, sigma_c=1 ch")

    fig, ax = plt.subplots(figsize=(W_HALF, 2.8))
    ax.errorbar(d["tau"], d["c"], yerr=d["sc"], fmt="o", color=BLUE, capsize=2, mec=SURFACE,
                label="peak centroid")
    ax.axvline(V_SHAPING_CHOSEN, color=PURPLE, ls="--", label=f"chosen, {V_SHAPING_CHOSEN:g} $\\mu$s")
    ax.set_xscale("log")
    ax.set_xticks(d["tau"])
    ax.set_xticklabels([f"{t:g}" for t in d["tau"]])
    ax.minorticks_off()
    ax.set_xlabel("shaping time ($\\mu$s)")
    ax.set_ylabel("peak centroid (channel)")
    volt_axis(ax)
    title(ax, "Centroid vs shaping time")
    leg(ax, "lower right")
    fig.tight_layout()
    save(fig, "F1_centroid_vs_shaping_time")
    return d


# =========================================================================
# F2. Alpha counting curve
# =========================================================================
def plot_alpha_counting(d):
    """F2. Am-241 count rate vs voltage, r = N/30 s, sigma_r = sqrt(N)/30 s (Eq. 3.40).
    All points share one marker (1050 V is still excluded from the plateau); dashed line at PLATEAU_START.
    Written in linear and log y versions."""
    print(f"\n--- F2. Alpha counting curve (LLD {LLD_ALPHA}, {T_ALPHA:g} s/point) ---")
    print(f"settings: PLATEAU_START = {PLATEAU_START} V, ALPHA_DROP_V = {ALPHA_DROP_V} V (hollow, excluded)")
    ok = np.allclose(d["rate"], d["rate_csv"], rtol=1e-6)
    print(f"rate column = counts/{T_ALPHA:g} s: {'reproduced' if ok else 'MISMATCH'}")
    print(d[["hv", "counts", "rate", "srate"]].round(2).to_string(index=False))
    drop = d[d["hv"] == ALPHA_DROP_V].iloc[0]
    top = d[d["hv"] == PLATEAU_START].iloc[0]
    print(f"FLAG: rate falls from {top.rate:.0f} /s at {PLATEAU_START} V to {drop.rate:.0f} /s at {ALPHA_DROP_V} V "
          f"(centroid {top.c:.0f} -> {drop.c:.0f} ch)")
    for v in (850, 900, 1000, ALPHA_DROP_V):
        r = d[d["hv"] == v].iloc[0]
        R(f"alpha rate at {v} V", r.rate, r.srate, "counts/s", "N/30 s, sqrt(N)/30 s (Eq. 3.40)")
    print("300 V has N = 0 (rate 0, no error bar); it cannot be drawn on the log axis.")

    for logy in (False, True):
        fig, ax = plt.subplots(figsize=(W_HALF, 2.8))
        m = d[d["counts"] > 0] if logy else d
        ax.errorbar(m["hv"], m["rate"], yerr=m["srate"], fmt="o", color=BLUE, capsize=2, mec=SURFACE,
                    label="count rate")
        ax.axvline(PLATEAU_START, color=PURPLE, ls="--", label=f"{PLATEAU_START} V")
        if logy:
            ax.set_yscale("log")
            ax.set_ylim(0.3, 2e6)          # headroom so the legend sits above the data
        else:
            ax.set_ylim(-500, d["rate"].max() * 1.08)
        ax.set_xlabel("applied voltage (V)")
        ax.set_ylabel("count rate (s$^{-1}$)")
        title(ax, "Alpha counting curve")
        leg(ax, "upper left")
        fig.tight_layout()
        save(fig, f"F2_alpha_counting_curve_{'log' if logy else 'lin'}")
    return d


# =========================================================================
# F3. Alpha pulse amplitude vs voltage (log-linear)
# =========================================================================
def two_point_slope(r1, r2):
    """s = ln(c2/c1)/(V2-V1); sigma_s = sqrt((sc1/c1)^2 + (sc2/c2)^2)/(V2-V1) (Eq. 3.37)."""
    dv = r2.hv - r1.hv
    s = np.log(r2.c / r1.c) / dv
    ss = np.sqrt((SIGMA_CENTROID / r1.c) ** 2 + (SIGMA_CENTROID / r2.c) ** 2) / dv
    return s, ss


def plot_alpha_amplitude(d, show_low=SHOW_LOW_AMPLITUDE, name="F3_alpha_amplitude_vs_voltage"):
    """F3. Alpha peak centroid vs voltage on a log y axis (compare Knoll Fig. 6.11 / Eq. 6.10,
    ln M ~ linear in V). Filled: AMPLITUDE_POINTS and the 1050 V drop; hollow: LLD-limited
    500-850 V if show_low. Error bars +/- SIGMA_CENTROID. No fit line."""
    good = d[d["hv"].isin(AMPLITUDE_POINTS)]
    dr = d[d["hv"] == ALPHA_DROP_V]
    low = d[d["hv"].isin(AMPLITUDE_LOW) & (d["c"] > 0)]
    print("\n--- F3. Alpha pulse amplitude vs voltage ---")
    print(f"settings: AMPLITUDE_POINTS = {AMPLITUDE_POINTS}, SHOW_LOW_AMPLITUDE = {SHOW_LOW_AMPLITUDE}")
    print(f"FLAG: centroids at 500-850 V are {low['c'].min():.0f}-{low['c'].max():.0f} ch, at or just above "
          f"the LLD ({LLD_ALPHA}); probably the LLD edge, not the alpha peak.")
    r900, r1000, r1050 = (d[d["hv"] == v].iloc[0] for v in (900, 1000, ALPHA_DROP_V))
    for a, b in ((r900, r1000), (r1000, r1050)):
        s, ss = two_point_slope(a, b)
        print(f"  d ln(centroid)/dV, {a.hv:.0f}-{b.hv:.0f} V: {s:.5f} +/- {ss:.1e} /V "
              f"(centroid x{np.exp(s*100):.3f} per 100 V)")
        R(f"d ln(centroid)/dV {a.hv:.0f}-{b.hv:.0f} V", s, ss, "1/V", "two-point slope; Eq. 3.37, sigma_c=1 ch; Knoll Eq. 6.10")

    fig, ax = plt.subplots(figsize=(W_HALF, 2.8))
    if show_low:
        ax.errorbar(low["hv"], low["c"], yerr=SIGMA_CENTROID, fmt="o", color=BLUE, mfc=SURFACE, capsize=2,
                    label="at LLD (500-850 V)")
    pts = pd.concat([good, dr])
    ax.errorbar(pts["hv"], pts["c"], yerr=SIGMA_CENTROID, fmt="o", color=BLUE, capsize=2, mec=SURFACE,
                label="peak centroid")
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}"))
    ax.yaxis.set_minor_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0f}"))
    ax.set_xlabel("applied voltage (V)")
    ax.set_ylabel("peak centroid (channel)")
    volt_axis(ax, log=True)
    if not show_low:
        ax.set_xlim(870, 1080)
    title(ax, "Alpha pulse amplitude vs voltage")
    leg(ax, "upper left")
    fig.tight_layout()
    save(fig, name)


# =========================================================================
# F4. One-point energy calibration (no spectrum saved)
# =========================================================================
def calibration(ds):
    """F4 skipped (no .SPE). k = 5.486 MeV / centroid at 3 us (Knoll Table 1.3), through the origin;
    sigma_k = k sigma_c / c (Eq. 3.37)."""
    c = ds[ds["tau"] == CAL_SHAPING_US].iloc[0].c
    k = E_AM241_KEV / c
    sk = k * SIGMA_CENTROID / c
    print("\n--- F4. Calibrated alpha spectrum: SKIPPED (no .SPE saved) ---")
    print(f"k = {E_AM241_KEV:g} keV / {c:.2f} ch = {k:.4f} +/- {sk:.4f} keV/ch (through origin; "
          f"800 V, gain 50, {CAL_SHAPING_US:g} us shaping only)")
    R("energy calibration factor k", k, sk, "keV/channel", "5486 keV / C(3 us); Knoll Table 1.3; Eq. 3.37, sigma_c<=1 ch")
    return k, sk


# =========================================================================
# F5. Beta and gamma counting curves
# =========================================================================
def plot_beta_gamma(db, dg, logy=F5_LOG_Y):
    """F5. Cl-36 beta (LLD 307) and gamma (LLD 229) count rate vs voltage, r = N/30 s,
    sigma_r = sqrt(N)/30 s (Eq. 3.40). Two series, nothing else."""
    print(f"\n--- F5. Beta (LLD {LLD_BETA}) and gamma (LLD {LLD_GAMMA}) counting curves, 30 s/point ---")
    ok = np.allclose(db["rate"], db["rate_csv"], rtol=1e-6)
    print(f"beta rate column = counts/{T_BETA:g} s: {'reproduced' if ok else 'MISMATCH'}")
    print("beta:\n" + db[["hv", "counts", "c", "rate", "srate"]].round(2).to_string(index=False))
    print("gamma:\n" + dg[["hv", "counts", "rate", "srate"]].round(2).to_string(index=False))
    dup = dg[dg.duplicated("counts", keep=False) & (dg["counts"] > 0)]
    if len(dup):
        print(f"FLAG: gamma counts repeat exactly: {', '.join(f'{v:.0f} V' for v in dup['hv'])} "
              f"all = {dup['counts'].iloc[0]:.0f}; possible copy error, check the notebook.")
    print(f"FLAG: beta centroids at 1100-1450 V are {db[(db.hv>=1100)&(db.hv<=1450)]['c'].min():.0f}-"
          f"{db[(db.hv>=1100)&(db.hv<=1450)]['c'].max():.0f} ch, at the LLD ({LLD_BETA}), like the alpha case.")
    print(f"gamma source label (GAMMA_SOURCE) = '{GAMMA_SOURCE}': Co-60 or Cs-137? ASK")
    for v in (1500, 1550):
        r = db[db["hv"] == v].iloc[0]
        R(f"beta rate at {v} V", r.rate, r.srate, "counts/s", "N/30 s, sqrt(N)/30 s (Eq. 3.40)")
    gm = dg.loc[dg["rate"].idxmax()]
    R("gamma maximum rate", gm.rate, gm.srate, "counts/s", f"at {gm.hv:.0f} V; Eq. 3.40")

    fig, ax = plt.subplots(figsize=(W_HALF, 2.8))
    b = db[db["counts"] > 0] if logy else db
    g = dg[dg["counts"] > 0] if logy else dg
    ax.errorbar(b["hv"], b["rate"], yerr=b["srate"], fmt="o", color=BLUE, capsize=2, mec=SURFACE,
                label="Cl-36 beta")
    ax.errorbar(g["hv"], g["rate"], yerr=g["srate"], fmt="s", color=ORANGE, capsize=2, mec=SURFACE,
                label=GAMMA_SOURCE)
    if logy:
        ax.set_yscale("log")
    ax.set_xlabel("applied voltage (V)")
    ax.set_ylabel("count rate (s$^{-1}$)")
    title(ax, "Beta and gamma counting curves")
    leg(ax, "center right")
    fig.tight_layout()
    save(fig, "F5_beta_gamma_counting_curves")


# =========================================================================
# Efficiency (table only)
# =========================================================================
def efficiency(db):
    """Absolute and intrinsic efficiency. r = N/t +/- sqrt(N)/t (Eq. 3.40); A = A0 exp(-lambda t),
    lambda = ln2/T_half (Knoll Eq. 1.1, Table 1.1); eps_abs = r/A; eps_int = eps_abs 4 pi/Omega,
    Omega = 2 pi (Knoll pp. 118-119, p. 166); Eq. 3.37 propagation."""
    r, sr = rates(EFF_COUNTS, EFF_TIME)
    r, sr = float(r), float(sr)
    A0 = A0_UCI * UCI_TO_BQ
    lam = np.log(2) / T_HALF_CL36_Y                         # 1/y
    dt_y = 0.0 if MEAS_DATE is None else (MEAS_DATE - A0_DATE).days / 365.25
    A = A0 * np.exp(-lam * dt_y)
    sA = A * A0_REL_UNC
    eps = r / A
    seps = eps * np.sqrt((sr / r) ** 2 + (sA / A) ** 2)     # Eq. 3.37 for a quotient
    omega = 2 * np.pi
    eps_int = eps * 4 * np.pi / omega
    seps_int = seps * 4 * np.pi / omega
    print("\n--- Efficiency (Cl-36, 1500 V, LLD 307, 60 s) ---")
    print(f"settings: MEAS_DATE = {MEAS_DATE} (decay elapsed {dt_y:.3f} y), A0_REL_UNC = {A0_REL_UNC}")
    print(f"r = {EFF_COUNTS} / {EFF_TIME:g} s = {r:.2f} +/- {sr:.2f} /s; CSV 'uC' column check: "
          f"r/3.7e4 = {r/UCI_TO_BQ:.4f} (CSV {EFF_RATE_UCI_CSV})")
    print(f"A0 = {A0_UCI} uCi = {A0:.4g} Bq; lambda = {lam:.4g} /y; decay over 1 y would be "
          f"{100*(1-np.exp(-lam)):.2e} % (negligible)")
    print(f"eps_abs = {eps:.4f} +/- {seps:.4f} (counting only); eps_int (Omega = 2 pi) = {eps_int:.4f} +/- {seps_int:.4f}")
    print("FLAG: eps_abs > 0.5, the 2 pi geometric maximum; eps_int > 1 is unphysical.")
    rb = {v: db[db["hv"] == v].iloc[0] for v in (1500, 1550)}
    for v, rr in rb.items():
        print(f"  beta curve at {v} V: {rr.rate:.1f} +/- {rr.srate:.1f} /s; efficiency run / curve = "
              f"{r/rr.rate:.4f}")
    diff = 100 * (r / rb[1500].rate - 1)
    sdiff = 100 * (r / rb[1500].rate) * np.sqrt((sr / r) ** 2 + (rb[1500].srate / rb[1500].rate) ** 2)
    print(f"FLAG: efficiency-run rate is {diff:.1f} +/- {sdiff:.1f} % above the beta-curve rate at 1500 V")
    R("efficiency-run rate", r, sr, "counts/s", "1428191/60 s; Eq. 3.40")
    R("marked activity A0", A0, sA, "Bq", "1.032 uCi x 3.7e4 Bq/uCi (Knoll p. 2); no stated uncertainty")
    R("activity at measurement", A, sA, "Bq", "A0 exp(-lambda t), Knoll Eq. 1.1; T1/2 = 3.08e5 y")
    R("absolute efficiency", eps, seps, "", "r/A; Eq. 3.37 (counting only); > 0.5 2pi limit")
    R("intrinsic efficiency (Omega=2pi)", eps_int, seps_int, "", "eps_abs 4pi/Omega, Knoll pp. 118-119")
    R("eff-run vs beta curve at 1500 V", diff, sdiff, "%", "r_eff/r_curve - 1; Eq. 3.37")
    return dict(r=r, sr=sr, A0=A0, A=A, sA=sA, eps=eps, seps=seps, eps_int=eps_int, seps_int=seps_int,
                dt_y=dt_y, rb=rb)


# =========================================================================
# Tables (LaTeX, booktabs)
# =========================================================================
def tex_table(name, caption, label, header, rows, spec=None):
    TAB_DIR.mkdir(exist_ok=True)
    spec = spec or "l" + "r" * (len(header) - 1)
    lines = ["\\begin{table}[htbp]", "\\centering", f"\\caption{{{caption}}}", f"\\label{{{label}}}",
             f"\\begin{{tabular}}{{{spec}}}", "\\toprule", " & ".join(header) + " \\\\", "\\midrule"]
    lines += [" & ".join(str(c) for c in r) + " \\\\" for r in rows]
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
    (TAB_DIR / f"{name}.tex").write_text("\n".join(lines) + "\n")


def cnt(n):
    """Counts with +/- sqrt(N) (Eq. 3.29)."""
    return f"{n:.0f} $\\pm$ {np.sqrt(n):.0f}"


def make_tables(ds, da, db, dg, eff):
    pm = "$\\pm$"
    cen = lambda c: "--" if (pd.isna(c) or c == 0) else f"{c:.2f}"
    # raw data
    tex_table("t1_shaping_raw", "Shaping-time data, Am-241 at 800 V.", "tab:shaping-raw",
              ["Shaping time ($\\mu$s)", "Centroid (channel)", "Gross peak area"],
              [[f"{r.tau:g}", f"{r.c:.2f}", "not recorded" if r.area_est else cnt(r.area)] for r in ds.itertuples()])
    tex_table("t2_alpha_raw", f"Alpha counting-curve data, Am-241, LLD channel {LLD_ALPHA}, {T_ALPHA:g} s per point.",
              "tab:alpha-raw", ["Voltage (V)", "Gross counts", "Centroid (channel)"],
              [[f"{r.hv:.0f}", cnt(r.counts), cen(r.c)] for r in da.itertuples()])
    tex_table("t3_beta_raw", f"Beta counting-curve data, Cl-36, LLD channel {LLD_BETA}, {T_BETA:g} s per point.",
              "tab:beta-raw", ["Voltage (V)", "Gross counts", "Centroid (channel)"],
              [[f"{r.hv:.0f}", cnt(r.counts), cen(r.c)] for r in db.itertuples()])
    tex_table("t4_efficiency_raw", "Efficiency-run data, Cl-36.", "tab:eff-raw",
              ["Source", "Voltage (V)", "Counts", "Time (s)", "Marked activity"],
              [["Cl-36", f"{V_EFF}", cnt(EFF_COUNTS), f"{EFF_TIME:g}", f"{A0_UCI} $\\mu$Ci ({A0_DATE:%b %-d %Y})"]],
              spec="lrrrr")
    tex_table("t5_gamma_raw", f"Gamma counting-curve data, LLD channel {LLD_GAMMA}, {T_GAMMA:g} s per point.",
              "tab:gamma-raw", ["Voltage (V)", "Gross counts"],
              [[f"{r.hv:.0f}", cnt(r.counts)] for r in dg.itertuples()])
    # derived
    tex_table("t6_ballistic_deficit", f"Ballistic deficit relative to {BD_REF_US:g} $\\mu$s, "
              f"$\\sigma_c \\le {SIGMA_CENTROID:g}$ channel. $^*$10 $\\mu$s area estimated ({AREA_10US_METHOD}).",
              "tab:bd", ["Shaping time ($\\mu$s)", "Centroid", "Peak area", "BD (\\%)"],
              [[f"{r.tau:g}", f"{r.c:.2f} {pm} {r.sc:g}", f"{r.area:.3g}" + ("$^*$" if r.area_est else ""),
                "--" if r.tau == BD_REF_US else f"{r.bd:.2f} {pm} {r.sbd:.2f}"] for r in ds.itertuples()])
    tex_table("t7_alpha_rates", "Alpha count rates, $r=N/t$, $\\sigma_r=\\sqrt{N}/t$.", "tab:alpha-rates",
              ["Voltage (V)", "Rate (s$^{-1}$)", "$\\ln c$"],
              [[f"{r.hv:.0f}", f"{r.rate:.2f} {pm} {r.srate:.2f}",
                "--" if (pd.isna(r.c) or r.c == 0) else f"{np.log(r.c):.4f} {pm} {SIGMA_CENTROID/r.c:.4f}"]
               for r in da.itertuples()])
    rows = []
    for (rb, rg) in [(db[db.hv == v], dg[dg.hv == v]) for v in sorted(set(db.hv) | set(dg.hv))]:
        v = (rb if len(rb) else rg).iloc[0].hv
        bs = f"{rb.iloc[0].rate:.1f} {pm} {rb.iloc[0].srate:.1f}" if len(rb) else "--"
        gs = f"{rg.iloc[0].rate:.2f} {pm} {rg.iloc[0].srate:.2f}" if len(rg) else "--"
        rows.append([f"{v:.0f}", bs, gs])
    tex_table("t8_beta_gamma_rates", "Beta and gamma count rates, $\\sigma_r=\\sqrt{N}/t$.", "tab:bg-rates",
              ["Voltage (V)", "Cl-36 beta (s$^{-1}$)", f"{GAMMA_SOURCE} (s$^{{-1}}$)"], rows)
    e = eff
    tex_table("t9_efficiency", "Counting efficiency, Cl-36 at 1500 V (counting uncertainty only).", "tab:eff",
              ["Quantity", "Value"],
              [["Count rate $r$ (s$^{-1}$)", f"{e['r']:.1f} {pm} {e['sr']:.1f}"],
               ["Activity $A$ (Bq)", f"{e['A']:.4g}"],
               ["$\\varepsilon_{\\mathrm{abs}} = r/A$", f"{e['eps']:.4f} {pm} {e['seps']:.4f}"],
               ["$\\varepsilon_{\\mathrm{int}}$ ($\\Omega = 2\\pi$)", f"{e['eps_int']:.4f} {pm} {e['seps_int']:.4f}"],
               ["Beta-curve rate at 1500 V (s$^{-1}$)", f"{e['rb'][1500].rate:.1f} {pm} {e['rb'][1500].srate:.1f}"],
               ["Beta-curve rate at 1550 V (s$^{-1}$)", f"{e['rb'][1550].rate:.1f} {pm} {e['rb'][1550].srate:.1f}"]])
    print(f"\nwrote 9 LaTeX tables to {TAB_DIR}")


# =========================================================================
def write_summary():
    lines, rows = [], []
    for name, v, u, unit, src in RESULTS:
        us = "" if u is None else f" +/- {u:.4g}"
        lines.append(f"{name}: {v:.5g}{us} {unit}   [{src}]")
        rows.append(dict(name=name, value=v, uncertainty=u, unit=unit, source=src))
    (ROOT / "results_summary.txt").write_text("\n".join(lines) + "\n")
    pd.DataFrame(rows).to_csv(ROOT / "results_summary.csv", index=False)
    print("\n=== RESULTS SUMMARY ===")
    print("\n".join(lines))


# =========================================================================
# F6. Differential counting curves (slope of the counting curve)
# =========================================================================
def differential(d, exclude=()):
    """dr/dV between neighbouring points: (r2 - r1)/(V2 - V1) at the midpoint voltage.
    The counting curve mirrors the integral pulse height distribution, so its slope maps the
    differential distribution (Knoll pp. 113-115, Fig. 4.3). sigma from Eq. 3.37:
    sqrt(s1^2 + s2^2)/(V2 - V1)."""
    d = d[~d["hv"].isin(exclude)].sort_values("hv").reset_index(drop=True)
    v1, v2 = d["hv"].values[:-1], d["hv"].values[1:]
    r1, r2 = d["rate"].values[:-1], d["rate"].values[1:]
    s1, s2 = d["srate"].values[:-1], d["srate"].values[1:]
    dv = v2 - v1
    return pd.DataFrame({"vmid": (v1 + v2) / 2, "v1": v1, "v2": v2,
                         "drdv": (r2 - r1) / dv, "sdrdv": np.sqrt(s1**2 + s2**2) / dv})


def plot_differential(d, name, label, color, marker, exclude=()):
    """F6. Differential counting curve dr/dV vs midpoint voltage, error bars from Eq. 3.37."""
    dd = differential(d, exclude)
    print(f"\n--- {name}: differential counting curve ({label}) ---")
    print(dd.round(3).to_string(index=False))
    fig, ax = plt.subplots(figsize=(W_HALF, 2.8))
    ax.errorbar(dd["vmid"], dd["drdv"], yerr=dd["sdrdv"], fmt=marker + "-", color=color, capsize=2,
                mec=SURFACE, lw=1.0, label=label)
    ax.axhline(0, color=GRAY, lw=0.8)
    ax.set_xlabel("applied voltage (V)")
    ax.set_ylabel("d$r$/d$V$ (s$^{-1}$ V$^{-1}$)")
    leg(ax, "upper left")
    fig.tight_layout()
    save(fig, name)
    return dd


if __name__ == "__main__":
    print("settings:", dict(SIGMA_CENTROID=SIGMA_CENTROID, AREA_10US_METHOD=AREA_10US_METHOD,
                            PLATEAU_START=PLATEAU_START, ALPHA_DROP_V=ALPHA_DROP_V,
                            AMPLITUDE_POINTS=AMPLITUDE_POINTS, SHOW_LOW_AMPLITUDE=SHOW_LOW_AMPLITUDE,
                            GAMMA_SOURCE=GAMMA_SOURCE, A0_REL_UNC=A0_REL_UNC, MEAS_DATE=MEAS_DATE,
                            F5_LOG_Y=F5_LOG_Y, T_ALPHA=T_ALPHA, T_BETA=T_BETA, T_GAMMA=T_GAMMA))
    ds, a10 = load_shaping()
    plot_shaping(ds, a10)
    da = load_alpha()
    plot_alpha_counting(da)
    plot_alpha_amplitude(da, show_low=True, name="F3_alpha_amplitude_vs_voltage_with_low")
    calibration(ds)
    db, dg = load_beta(), load_gamma()
    plot_beta_gamma(db, dg)
    plot_differential(da, "F6a_alpha_differential", "Am-241 alpha", BLUE, "o", exclude=(ALPHA_DROP_V,))
    plot_differential(db, "F6b_beta_differential", "Cl-36 beta", BLUE, "o")
    eff = efficiency(db)
    make_tables(ds, da, db, dg, eff)
    write_summary()
    plt.close("all")
