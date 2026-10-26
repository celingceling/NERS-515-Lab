"""
NERS 515 Lab 4 (GM counting): every plot, number and table for the report.

Run from anywhere:  python lab_4_plots.py
Reads   data/counting_curve.csv, data/beta_attenuation.csv, data/two_source_dead_time.csv
        data/pulse_height_consistency.csv (written from the notebook values if missing)
Writes  figures/*.png + *.pdf, tables/*.tex, results_summary.txt, results_summary.csv

Sources for formulas: Knoll 4th ed., the lecture slides, and the Lab 4 manual only.
Equation numbers are Knoll's (4th ed.). Judgment calls are the named settings below.
Needs numpy, pandas, matplotlib.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
FIG_DIR = ROOT / "figures"
TAB_DIR = ROOT / "tables"
ATTEN_CSV = DATA_DIR / "beta_attenuation.csv"
COUNT_CSV = DATA_DIR / "counting_curve.csv"
TWOSRC_CSV = DATA_DIR / "two_source_dead_time.csv"
PH_CSV = DATA_DIR / "pulse_height_consistency.csv"
SCOPE_DIR = ROOT.parents[1] / "Lab 4"            # NERS 515/Lab 4 (dead_time.JPG, recovery_time.JPG)
SCOPE_DEAD_IMG = SCOPE_DIR / "dead_time.JPG"      # notebook calls these print_008 / print_009
SCOPE_REC_IMG = SCOPE_DIR / "recovery_time.JPG"

# ---- measured constants (notebook / manual) -------------------------------
COUNT_TIME = 3.0                 # s per counting-curve point (notebook)
T_TWO_SRC = 10.0                 # s per two-source measurement (CSV header "T=10s")
T_PH = 30.0                      # s real time per MCA spectrum
V_OP = 840.0                     # V operating voltage (notebook)
V_START = 670.0                  # V first counts (Knoll p. 215 "starting voltage")
V_RUNAWAY = 910.0                # V continuous discharge onset; run stopped here
TAU_DEAD_SCOPE = 360e-6          # s, scope dead time (Sec. 5.1)
TAU_RECOVERY_SCOPE = 482e-6      # s, scope recovery time (Sec. 5.1)
X_REL_ERR = 0.10                 # manual: assume 10% uncertainty in thickness
CAL_OFFSET_MV, CAL_SLOPE_MV = -36.0, 1.31    # V(n) = -36.0 mV + 1.31 mV * n
CAL_SLOPE_NOTEBOOK_MV = 1.305    # slope that reproduces the notebook's 3.83 / 4.44 V
PH_NOTEBOOK_V = {"Co-60": 3.83, "C-14": 4.44}

# ---- judgment calls: named settings (printed at run time; confirm before locking) ----
SHOW_TITLES = False              # short titles on figures (set True if no LaTeX caption)
KNEE_HV = 710.0                  # V, where the rise ends and the plateau begins (read from data)
PLATEAU = (730, 890)             # V, main plateau-fit window
PLATEAU_ALTS = [(710, 890), (770, 890)]   # alternates, printed for sensitivity
AMP_FIT_RANGE = (730, 890)       # V, pulse-height-vs-HV line fit; only the line is drawn over this range
FIT_MAX_THICKNESS = None         # mg/cm^2; None = use every Al point for the "all points" fit
SUBFITS = {                      # name: (first, last) Al point, 1-indexed inclusive
    "all points": (1, 8),
    "without first point": (2, 8),
    "points 2-6": (2, 6),
    "points 3-8 (tail)": (3, 8),
}
PLOT_SUBFITS = ["without first point"]   # which sub-fit lines are drawn
TAIL_POINTS = (3, 6)             # Al points (1-indexed, inclusive) averaged for the tail level
INCLUDE_PB = False               # Pb rows are never fitted; True draws them hollow
N_EXPECTED_CM2G = 105.0          # cm^2/g, Co-60 read off Knoll Fig. 2.16 (E_m line); CONFIRM
N_EXPECTED_ERR = 10.0            # cm^2/g, my reading uncertainty (about 10%); CONFIRM
E_CO60_FIG = 0.32                # MeV, Co-60 E_m marker height in Fig. 2.16 (CONFIRM)
# Fig. 2.16, E_m line read as a straight line on log-log axes: E = E10 * (n/10)^-P
FIG216_E10_MEV, FIG216_P = 1.47, 0.668

# ---- plot style -----------------------------------------------------------
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


# =========================================================================
# Fitting
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


def line_fit(x, y, sy, sx=None):
    """Wrapper: dict with a, b, errors, chi2/ndf and the Birge-scaled slope error."""
    x, y, sy = (np.asarray(v, float) for v in (x, y, sy))
    sx = np.zeros_like(x) if sx is None else np.asarray(sx, float)
    a, b, cov, chi2, ndf = weighted_line_fit(x, y, sy, sx)
    sc = np.sqrt(chi2 / ndf) if ndf > 0 and chi2 / ndf > 1 else 1.0
    return dict(a=a, b=b, cov=cov, sa=np.sqrt(cov[0, 0]), sb=np.sqrt(cov[1, 1]),
                chi2=chi2, ndf=ndf, scale=sc, n=len(x))


def x_intercept(f):
    """x0 = -a/b with error from Eq. 3.37 using the full covariance."""
    a, b, c = f["a"], f["b"], f["cov"]
    var = c[0, 0] / b**2 + a**2 * c[1, 1] / b**4 - 2 * a * c[0, 1] / b**3
    return -a / b, np.sqrt(var)


# =========================================================================
# A, B. Counting curve and pulse height vs high voltage
# =========================================================================
def load_counting():
    d = pd.read_csv(COUNT_CSV)
    d.columns = ["hv", "counts", "amp", "samp"]
    d["rate"] = d["counts"] / COUNT_TIME                    # Eq. 3.40 (t constant)
    d["srate"] = np.sqrt(d["counts"]) / COUNT_TIME          # Eq. 3.29 / 3.40: sigma_N = sqrt(N)
    return d


def plateau_fit(d, lo, hi):
    w = d[(d["hv"] >= lo) & (d["hv"] <= hi)]
    f = line_fit(w["hv"], w["rate"], w["srate"])
    f["mean"] = w["rate"].mean()
    f["at_start"] = f["a"] + f["b"] * lo
    return f


def plot_amplitude(d):
    """A. Pulse height vs HV: points with scope-reading error bars, weighted straight-line
    fit over AMP_FIT_RANGE (weights 1/sigma^2, Eq. 3.37 effective variance with no x error),
    x-intercept with propagated error, residual panel. Knoll p. 209: amplitude ~ overvoltage."""
    lo, hi = AMP_FIT_RANGE
    fitd = d[(d["hv"] >= lo) & (d["hv"] <= hi)]
    f = line_fit(fitd["hv"], fitd["amp"], fitd["samp"])
    x0, sx0 = x_intercept(f)
    R("amp-HV slope", f["b"], f["sb"], "mV/V", f"weighted fit {lo}-{hi} V, no chi2 scaling")
    R("amp-HV slope (chi2-scaled error)", f["b"], f["sb"] * f["scale"], "mV/V", "x sqrt(chi2/ndf)")
    R("amp-HV intercept (mV)", f["a"], f["sa"], "mV", "weighted fit")
    R("amp-HV x-intercept", x0, sx0, "V", "Eq. 3.37 with covariance")
    R("amp-HV chi2/ndf", f["chi2"] / f["ndf"], None, "", f"chi2={f['chi2']:.1f}, ndf={f['ndf']}")
    R("first-count (starting) voltage", V_START, None, "V", "data: 44 counts at 670 V, 0 at 650 V")
    print(f"\n--- A. Pulse height vs HV: fit {lo}-{hi} V ({f['n']} points, ndf {f['ndf']}) ---")
    print(f"slope = {f['b']:.3f} +/- {f['sb']:.3f} mV/V (scaled err {f['sb']*f['scale']:.3f}); "
          f"intercept = {f['a']:.1f} +/- {f['sa']:.1f} mV; chi2/ndf = {f['chi2']:.1f}/{f['ndf']}")
    print(f"x-intercept = {x0:.1f} +/- {sx0:.1f} V  (first counts at {V_START:.0f} V; "
          f"Knoll p. 209 overvoltage = V - V_min)")
    show = d[d["amp"] > 0].copy()
    show["fit"] = f["a"] + f["b"] * show["hv"]
    show["resid"] = show["amp"] - show["fit"]
    show["pull"] = show["resid"] / show["samp"]
    print(show[["hv", "amp", "samp", "fit", "resid", "pull"]].round(2).to_string(index=False))
    print("  (910 V is not in the fit; its residual shows the extrapolation)")

    fig, ax = plt.subplots(figsize=(W_HALF, 3.0))
    pos = d[d["amp"] > 0]
    inside = pos[pos["hv"] != V_RUNAWAY]
    outside = pos[pos["hv"] == V_RUNAWAY]
    ax.errorbar(inside["hv"], inside["amp"], yerr=inside["samp"], fmt="o", color=BLUE, capsize=2,
                mec=SURFACE, label="pulse height")
    ax.errorbar(outside["hv"], outside["amp"], yerr=outside["samp"], fmt="D", color=GRAY,
                capsize=2, mfc=SURFACE)
    zero = d[d["amp"] == 0]
    ax.plot(zero["hv"], zero["amp"], "s", mfc=SURFACE, color=INK2)
    xx = np.linspace(lo, hi, 50)
    ax.plot(xx, f["a"] + f["b"] * xx, color=ORANGE, label="linear fit")
    ax.axvline(V_OP, color=PURPLE, ls="--", label="operating V")
    ax.set_ylabel("pulse height (mV)")
    ax.set_ylim(bottom=-20)
    title(ax, "Pulse height vs high voltage")
    leg(ax, "upper left")
    ax.set_xlabel("high voltage (V)")
    fig.tight_layout()
    save(fig, "A_pulse_height_vs_hv")
    return fig


def plot_counting(d):
    """B. Counting curve: rate = N/3 s, sigma = sqrt(N)/3 (Eq. 3.38-3.40), weighted plateau fit
    (1/sigma^2) over PLATEAU with starting voltage, knee, operating voltage and runaway marked."""
    print(f"\n--- B. Counting curve (count time {COUNT_TIME:g} s) ---")
    print(f"settings: PLATEAU={PLATEAU}, alternates={PLATEAU_ALTS}, KNEE_HV={KNEE_HV:g}, V_OP={V_OP:g}")
    print("N=0 at 650 V gives sigma = 0 (sqrt(0)); drawn without an error bar.")
    for win in [PLATEAU] + PLATEAU_ALTS:
        f = plateau_fit(d, *win)
        p_start = 100 * 100 * f["b"] / f["at_start"]
        p_mean = 100 * 100 * f["b"] / f["mean"]
        e_start = 100 * 100 * f["sb"] / f["at_start"]
        e_mean = 100 * 100 * f["sb"] / f["mean"]
        tag = f"plateau {win[0]}-{win[1]} V"
        print(f"{tag}: {f['n']} pts, slope = {f['b']:.4f} +/- {f['sb']:.4f} /s/V "
              f"(scaled err {f['sb']*f['scale']:.4f}), chi2/ndf = {f['chi2']:.1f}/{f['ndf']}")
        print(f"    percent per 100 V: {p_start:.1f} +/- {e_start:.1f} % (ref = fit at {win[0]} V, "
              f"{f['at_start']:.1f}/s);  {p_mean:.1f} +/- {e_mean:.1f} % (ref = mean rate {f['mean']:.1f}/s)")
        R(f"{tag} slope", f["b"], f["sb"], "counts/s/V", "weighted fit; Eq. 3.38-3.40 weights")
        R(f"{tag} slope (chi2-scaled error)", f["b"], f["sb"] * f["scale"], "counts/s/V", "x sqrt(chi2/ndf) if >1")
        R(f"{tag} chi2/ndf", f["chi2"] / f["ndf"], None, "", f"chi2={f['chi2']:.1f}, ndf={f['ndf']}")
        R(f"{tag} %/100V (ref: fit at window start)", p_start, e_start, "%", "slope*100V / rate; ref error ignored")
        R(f"{tag} %/100V (ref: plateau mean)", p_mean, e_mean, "%", "slope*100V / rate; ref error ignored")
    print("Knoll p. 216 quotes 2-3 %/100 V (organic quench) but does not define the reference rate: ASK.")
    fm = plateau_fit(d, *PLATEAU)

    fig, ax = plt.subplots(figsize=(W_HALF, 3.0))
    draw_counting(ax, d, fm)
    fig.tight_layout()
    save(fig, "B_counting_curve")
    return fig


def draw_counting(ax, d, f):
    lo, hi = PLATEAU
    ax.axvspan(lo, hi, color=GREEN, alpha=0.10, lw=0, label="plateau")
    ax.errorbar(d["hv"], d["rate"], yerr=d["srate"], fmt="o", color=BLUE, capsize=2,
                mec=SURFACE, label="count rate")
    xx = np.array([lo, hi])
    ax.plot(xx, f["a"] + f["b"] * xx, color=BLACK, lw=1.6, label="plateau fit")
    ax.axvline(V_OP, color=PURPLE, ls="--", label="operating V")
    ax.set_ylabel("count rate (s$^{-1}$)")
    ax.set_xlabel("high voltage (V)")
    ax.set_ylim(-3, d["rate"].max() * 1.08)
    title(ax, "Counting curve")
    leg(ax, "lower right")


# =========================================================================
# C. Pulse height consistency
# =========================================================================
def load_ph():
    if not PH_CSV.exists():
        pd.DataFrame({"source": ["Co-60", "C-14", "Cl-36"], "centroid_channel": [2906, 3374, 1939],
                      "gross_counts": [4419, 1280, 13986], "real_time_s": [30, 30, 30]}
                     ).to_csv(PH_CSV, index=False)
        print(f"wrote {PH_CSV.name} from the notebook values (30 s real time)")
    d = pd.read_csv(PH_CSV)
    d["amp_V"] = (CAL_OFFSET_MV + CAL_SLOPE_MV * d["centroid_channel"]) / 1000.0
    d["amp_V_alt"] = (CAL_OFFSET_MV + CAL_SLOPE_NOTEBOOK_MV * d["centroid_channel"]) / 1000.0
    d["rate"] = d["gross_counts"] / d["real_time_s"]
    d["srate"] = np.sqrt(d["gross_counts"]) / d["real_time_s"]
    return d


def plot_ph(d):
    """C. Amplitude from the calibrated centroid, V(n) = -36.0 mV + 1.31 mV n, per source, and
    amplitude vs gross count rate (N/30 s, sqrt(N)/t, Eq. 3.40). No trend line through 3 points."""
    print("\n--- C. Pulse height consistency (30 s real time) ---")
    print(d[["source", "centroid_channel", "gross_counts", "amp_V", "amp_V_alt", "rate", "srate"]]
          .round(3).to_string(index=False))
    for _, r in d.iterrows():
        R(f"{r.source} amplitude", r.amp_V, None, "V", "-36.0 mV + 1.31 mV/ch * centroid; no unc. recorded")
        R(f"{r.source} gross rate", r.rate, r.srate, "counts/s", "N/30 s, sqrt(N)/30 s (Eq. 3.40)")
        if r.source in PH_NOTEBOOK_V:
            diff = 100 * (r.amp_V - PH_NOTEBOOK_V[r.source]) / PH_NOTEBOOK_V[r.source]
            print(f"  {r.source}: 1.31 mV/ch gives {r.amp_V:.3f} V; 1.305 mV/ch gives {r.amp_V_alt:.3f} V; "
                  f"notebook {PH_NOTEBOOK_V[r.source]:.2f} V; 1.31 vs notebook = {diff:+.2f} %")
    print("No centroid or calibration uncertainty was recorded: none drawn on amplitude (ASK).")
    order = d.sort_values("rate")
    print("amplitude falls as rate rises: " + " > ".join(f"{s} ({a:.2f} V @ {r:.0f}/s)"
          for s, a, r in zip(order.source, order.amp_V, order.rate)))

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(W_FULL, 3.0))
    cols = [BLUE, ORANGE, GREEN]
    mk = ["o", "s", "^"]
    a1.bar(d["source"], d["amp_V"], color=cols, width=0.55)
    for i, r in d.iterrows():
        a1.text(i, r.amp_V + 0.06, f"{r.amp_V:.2f} V\n{r.rate:.0f} s$^{{-1}}$", ha="center", va="bottom")
    a1.set_ylim(0, d["amp_V"].max() * 1.3)
    a1.set_ylabel("amplitude from centroid (V)")
    a1.grid(axis="x", visible=False)
    title(a1, "Amplitude by source (label: rate)")
    for i, r in d.iterrows():
        a2.errorbar(r.rate, r.amp_V, xerr=r.srate, fmt=mk[i], color=cols[i], capsize=2, ms=7, mec=SURFACE)
        a2.annotate(r.source, (r.rate, r.amp_V), textcoords="offset points", xytext=(6, 6))
    a2.set_xlabel("gross count rate (s$^{-1}$)")
    a2.set_ylabel("amplitude (V)")
    a2.set_xlim(0, d["rate"].max() * 1.2)
    a2.set_ylim(d["amp_V"].min() * 0.8, d["amp_V"].max() * 1.12)
    title(a2, "Amplitude vs count rate")
    fig.tight_layout()
    save(fig, "C_pulse_height_consistency")
    return fig


# =========================================================================
# D. Beta attenuation
# =========================================================================
def beta_attenuation():
    """D. ln(net rate) vs mass thickness. net r = G/tg - B/tb, sigma_r = sqrt(G/tg^2 + B/tb^2)
    (Eq. 3.52-3.53); y error sigma_r/r, x error 10 % (manual). Effective-variance weighted fits
    (Eq. 3.37), first-two-point slope, expected-n line from Fig. 2.16, endpoint energy."""
    df = pd.read_csv(ATTEN_CSV, keep_default_na=False, na_values=[""])
    df = df.iloc[:, :4]
    df.columns = ["material", "t_mg", "counts", "time"]
    df = df.dropna(subset=["counts"]).copy()
    df["material"] = df["material"].astype(str).str.strip()
    bg = df[df["material"] == "None"].iloc[0]
    C_bg, T_bg = bg["counts"], bg["time"]

    def net(c, t):
        r = c / t - C_bg / T_bg
        s = np.sqrt(c / t**2 + C_bg / T_bg**2)      # Eq. 3.53
        return r, s

    al = df[df["material"] == "Al"].reset_index(drop=True)
    al["gross_rate"] = al["counts"] / al["time"]
    al["r"], al["sr"] = net(al["counts"].to_numpy(float), al["time"].to_numpy(float))
    al["y"] = np.log(al["r"])
    al["sy"] = al["sr"] / al["r"]
    al["sx"] = X_REL_ERR * al["t_mg"]
    if C_bg < 10:
        print(f"WARNING: background N = {C_bg:.0f} (< 10): sqrt(N) is a poor error estimate (see E).")

    print("\n--- D. Beta attenuation (Eq. 2.14: I = I0 exp(-n t)); t in mg/cm^2, n converted to cm^2/g ---")
    print(f"background: {C_bg:.0f} counts / {T_bg:.0f} s = {C_bg/T_bg:.2f} /s")
    print(al[["t_mg", "counts", "time", "gross_rate", "r", "sr", "y", "sy", "sx"]].round(3).to_string(index=False))
    pb = df[df["material"] == "Pb"].copy()
    pb["r"], pb["sr"] = net(pb["counts"].to_numpy(float), pb["time"].to_numpy(float))
    print("Pb (never fitted):", "; ".join(f"{t:.0f} mg/cm2 net {r:.2f} +/- {s:.2f} /s"
          for t, r, s in zip(pb["t_mg"], pb["r"], pb["sr"])))
    R("beta background rate", C_bg / T_bg, np.sqrt(C_bg) / T_bg, "counts/s", f"{C_bg:.0f} counts / {T_bg:.0f} s")

    fits = {}
    for name, (i0, i1) in SUBFITS.items():
        w = al.iloc[i0 - 1:i1]
        if FIT_MAX_THICKNESS is not None:
            w = w[w["t_mg"] <= FIT_MAX_THICKNESS]
        f = line_fit(w["t_mg"], w["y"], w["sy"], w["sx"])
        f["n_cm2g"], f["sn_cm2g"] = -f["b"] * 1000.0, f["sb"] * 1000.0
        f["I0"] = np.exp(f["a"])
        fits[name] = f
        print(f"fit '{name}': {f['n']} points, ndf {f['ndf']}: n = {f['n_cm2g']:.2f} +/- {f['sn_cm2g']:.2f} cm^2/g, "
              f"I0 = {f['I0']:.1f} /s, chi2/ndf = {f['chi2']:.1f}/{f['ndf']}")
        R(f"beta n [{name}]", f["n_cm2g"], f["sn_cm2g"], "cm^2/g", f"weighted fit, {f['n']} pts, ndf {f['ndf']}; Eq. 2.14, 3.37")
        R(f"beta I0 [{name}]", f["I0"], f["I0"] * f["sa"], "counts/s", "exp(intercept)")
        R(f"beta chi2/ndf [{name}]", f["chi2"] / f["ndf"], None, "", f"chi2={f['chi2']:.1f}, ndf={f['ndf']}")
    if fits["all points"]["chi2"] / fits["all points"]["ndf"] > 2:
        print("WARNING: chi2/ndf of the all-points fit is large; a single exponential does not describe "
              "these points (Knoll p. 45: only approximately exponential).")

    # first-two-point slope (Eq. 3.37 on n12 = ln(r1/r2)/(t2 - t1))
    p1, p2 = al.iloc[0], al.iloc[1]
    dt = p2.t_mg - p1.t_mg
    n12 = np.log(p1.r / p2.r) / dt
    var = (p1.sy**2 + p2.sy**2) / dt**2 + n12**2 * (p1.sx**2 + p2.sx**2) / dt**2
    n12_c, s12_c = n12 * 1000, np.sqrt(var) * 1000
    print(f"first-two-point slope n12 = {n12_c:.1f} +/- {s12_c:.1f} cm^2/g (y and 10% x errors, Eq. 3.37); "
          f"y-only error {1000*np.sqrt((p1.sy**2+p2.sy**2))/dt:.1f}")
    R("beta n12 (first two points)", n12_c, s12_c, "cm^2/g", "ln(r1/r2)/(t2-t1); Eq. 3.37 incl. 10% x error")
    a12 = p1.y + n12 * p1.t_mg    # line through point 1 with slope -n12 passes through point 2 as well

    # tail level
    k0, k1 = TAIL_POINTS
    tw = al.iloc[k0 - 1:k1]
    wts = 1 / tw["sr"] ** 2
    tail = float((wts * tw["r"]).sum() / wts.sum())
    stail = float(1 / np.sqrt(wts.sum()))
    chi_t = float((wts * (tw["r"] - tail) ** 2).sum())
    print(f"tail level (points {k0}-{k1}): {tail:.2f} +/- {stail:.2f} /s weighted mean, chi2/ndf = "
          f"{chi_t:.1f}/{len(tw)-1}  (judgment call: TAIL_POINTS; rates {', '.join(f'{v:.1f}' for v in tw['r'])})")
    R("beta tail level (weighted mean)", tail, stail, "counts/s", f"points {k0}-{k1}; Eq. 3.37 weighted mean; judgment call")

    # expected n and endpoint energy
    n_exp = N_EXPECTED_CM2G
    print(f"expected n (Co-60, Knoll Fig. 2.16, E_m line, E = {E_CO60_FIG} MeV): {n_exp:.0f} +/- {N_EXPECTED_ERR:.0f} cm^2/g "
          f"(my graph reading: CONFIRM)")
    R("beta n expected (Co-60, Fig. 2.16)", n_exp, N_EXPECTED_ERR, "cm^2/g", f"read from E_m line at {E_CO60_FIG} MeV; confirm")
    print(f"E_m line used for inversion: E = {FIG216_E10_MEV} MeV * (n/10 cm^2/g)^-{FIG216_P} "
          f"(straight line on the log-log axes, read from the figure)")
    for name, nv, sn in [("all points", fits["all points"]["n_cm2g"], fits["all points"]["sn_cm2g"]),
                         ("without first point", fits["without first point"]["n_cm2g"], fits["without first point"]["sn_cm2g"]),
                         ("first two points", n12_c, s12_c)]:
        E = FIG216_E10_MEV * (nv / 10) ** (-FIG216_P)
        sE = E * FIG216_P * sn / nv                  # Eq. 3.37
        flag = "  (n below the 3-600 cm^2/g range plotted in Fig. 2.16: extrapolation)" if nv < 3 else ""
        print(f"endpoint energy from n [{name}] = {nv:.2f} cm^2/g: E_m = {E:.2f} +/- {sE:.2f} MeV (from sigma_n only){flag}")
        R(f"beta endpoint energy [{name}]", E, sE, "MeV", "Fig. 2.16 E_m line inverted; error from sigma_n only (Eq. 3.37)")

    # ---------- figure D: ln(rate) ----------
    fig, ax = plt.subplots(figsize=(W_FULL, 3.6))
    ax.errorbar(al["t_mg"], al["y"], xerr=al["sx"], yerr=al["sy"], fmt="o", color=BLUE,
                capsize=2.5, elinewidth=1.1, mec=SURFACE, zorder=3, label="data")
    tmax = al["t_mg"].max() * 1.05
    xx = np.linspace(0, tmax, 300)
    for name in PLOT_SUBFITS:
        f = fits[name]
        ax.plot(xx, f["a"] + f["b"] * xx, color=BLUE, ls="--", zorder=2, label="fit, points 2-8")
    if INCLUDE_PB:
        ax.errorbar(pb["t_mg"], np.log(pb["r"]), xerr=X_REL_ERR * pb["t_mg"], yerr=pb["sr"] / pb["r"],
                    fmt="s", mfc=SURFACE, color=GRAY, capsize=2.5, label="Pb (not fitted)")
    ax.set_xlabel("absorber mass thickness (mg/cm$^2$)")
    ax.set_ylabel("ln(net count rate / s$^{-1}$)")
    ax.set_xlim(0, tmax)
    ax.set_ylim((al["y"] - al["sy"]).min() - 0.3, (al["y"] + al["sy"]).max() + 0.4)
    title(ax, "Beta attenuation in aluminum (Co-60)")
    leg(ax, "upper right")
    fig.tight_layout()
    save(fig, "D_beta_attenuation_ln")

    return al, pb, C_bg, T_bg, fits


# =========================================================================
# E. Dead time
# =========================================================================
def n_nonpar(m, tau):                       # Eq. 4.24
    return m / (1.0 - m * tau)


def m_nonpar(n, tau):
    return n / (1.0 + n * tau)


def n_par(m, tau):
    """Invert m = n exp(-n tau) on the low-rate branch (Eq. 4.27)."""
    if m > 1.0 / (np.e * tau):              # above the maximum of the curve
        return np.nan
    lo, hi = m, 1.0 / tau
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if mid * np.exp(-mid * tau) < m:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def m_par(n, tau):
    return n * np.exp(-n * tau)


def predicted_m12(m1, m2, mb, tau, model):
    """Combined rate expected from the single-source rates (Eq. 4.30)."""
    if model == "nonpar":
        if max(m1, m2) * tau >= 1:
            return np.nan
        n12 = n_nonpar(m1, tau) + n_nonpar(m2, tau) - n_nonpar(mb, tau)
        return m_nonpar(n12, tau)
    n12 = n_par(m1, tau) + n_par(m2, tau) - n_par(mb, tau)
    return m_par(n12, tau)


def tau_two_source(m1, m2, m12, mb):
    """Eq. 4.32 (nonparalyzable). Returns nan if Z > 1 (no real solution)."""
    X = m1 * m2 - mb * m12
    Y = m1 * m2 * (m12 + mb) - mb * m12 * (m1 + m2)
    Z = Y * (m1 + m2 - m12 - mb) / X**2
    tau = X * (1 - np.sqrt(1 - Z)) / Y if Z <= 1 else np.nan
    return tau, Z, X / Y


def tau_from_counts(N, T):
    """tau (s) from counts N = [background, source 1, source 2, both] over time T (Eq. 4.32)."""
    mb, m1, m2, m12 = (np.asarray(N, float) / T)
    return tau_two_source(m1, m2, m12, mb)[0]


def sigma_tau(N, T):
    """Propagate sigma_N = sqrt(N) (Eq. 3.29) through Eq. 4.32 with Eq. 3.37; central differences."""
    N = np.asarray(N, float)
    var = 0.0
    for i in range(4):
        h = 1e-4 * max(N[i], 1.0)
        up, dn = N.copy(), N.copy()
        up[i] += h
        dn[i] -= h
        d = (tau_from_counts(up, T) - tau_from_counts(dn, T)) / (2 * h)
        var += d**2 * N[i]
    return np.sqrt(var)


def dead_time():
    """E. Two-source dead time. Per run and pooled: Eq. 4.32 tau, Eq. 3.37 sigma_tau with
    sigma_N = sqrt(N), Z, fractional dead time m12*tau (Knoll p. 125 wants >= 20 %);
    mean, sample std (Eq. 3.9, N-1) and standard error s/sqrt(3) of the three runs."""
    df = pd.read_csv(TWOSRC_CSV)
    df.columns = ["Nb", "N1", "N2", "N12", "tau_csv"]
    df.index = np.arange(1, len(df) + 1)
    T = T_TWO_SRC
    print(f"\n--- E. Two-source dead time (Eqs. 4.30-4.32), T = {T:g} s per measurement ---")
    rows = []
    for run, r in df.iterrows():
        N = [r.Nb, r.N1, r.N2, r.N12]
        tau, Z, _ = tau_two_source(r.N1 / T, r.N2 / T, r.N12 / T, r.Nb / T)
        s = sigma_tau(N, T)
        rows.append(dict(run=run, mb=r.Nb / T, m1=r.N1 / T, m2=r.N2 / T, m12=r.N12 / T, Z=Z, tau=tau,
                         stau=s, frac=r.N12 / T * tau, csv=r.tau_csv))
        print(f"run {run}: m_b={r.Nb/T:.2f} m1={r.N1/T:.1f} m2={r.N2/T:.1f} m12={r.N12/T:.1f} /s; Z={Z:.4f}; "
              f"tau = {tau*1e6:.1f} +/- {s*1e6:.0f} us (CSV {r.tau_csv:.2f} us, diff {tau*1e6 - r.tau_csv:+.2f}); "
              f"m12*tau = {100*r.N12/T*tau:.1f} %")
        if r.Nb < 10:
            print(f"   WARNING: background N = {r.Nb:.0f} (< 10): sqrt(N) is a crude error; Knoll Ch. 3 treats N < 30 "
                  f"as Poisson (var = mean) and gives no separate small-count formula, so sqrt(N) is kept.")
        R(f"run {run} tau", tau * 1e6, s * 1e6, "us", "Eq. 4.32; sigma Eq. 3.37 with sigma_N=sqrt(N)")
        R(f"run {run} Z", Z, None, "", "Eq. 4.32")
        R(f"run {run} m12*tau", 100 * r.N12 / T * tau, None, "%", "Knoll p. 125: want >= 20 %")
    res = pd.DataFrame(rows)
    ok = np.allclose(res["tau"] * 1e6, res["csv"], atol=0.01)
    print(f"check against CSV 'Dead Time' column (298, 612, 971 us): {'reproduced' if ok else 'MISMATCH'}")

    taus = res["tau"].to_numpy() * 1e6
    mean, sd = taus.mean(), taus.std(ddof=1)               # Eq. 3.5, 3.9
    sem = sd / np.sqrt(len(taus))
    print(f"mean tau = {mean:.0f} us, sample std = {sd:.0f} us (N-1), standard error of mean = {sem:.0f} us")
    R("tau mean of 3 runs", mean, sem, "us", "Eq. 3.5; error = s/sqrt(3) (Eq. 3.9, 3.41-3.43)")
    R("tau sample std (3 runs)", sd, None, "us", "Eq. 3.9, N-1")

    Np = [df.Nb.sum(), df.N1.sum(), df.N2.sum(), df.N12.sum()]
    Tp = T * len(df)
    mbp, m1p, m2p, m12p = (np.array(Np) / Tp)
    taup, Zp, _ = tau_two_source(m1p, m2p, m12p, mbp)
    sp = sigma_tau(Np, Tp)
    print(f"pooled ({Tp:g} s): m_b={mbp:.2f} m1={m1p:.1f} m2={m2p:.1f} m12={m12p:.1f}; Z={Zp:.4f}; "
          f"tau = {taup*1e6:.0f} +/- {sp*1e6:.0f} us; m12*tau = {100*m12p*taup:.1f} %")
    R("pooled tau", taup * 1e6, sp * 1e6, "us", "Eq. 4.32 on summed counts; Eq. 3.37")
    R("pooled Z", Zp, None, "", "Eq. 4.32")
    R("scope dead time", TAU_DEAD_SCOPE * 1e6, None, "us", "scope cursor, Sec. 5.1; no uncertainty recorded")
    R("scope recovery time", TAU_RECOVERY_SCOPE * 1e6, None, "us", "notebook; screenshot cursors read 480 us")
    print(f"sigma_tau per run (us): {', '.join(f'{s*1e6:.0f}' for s in res['stau'])} "
          f"(your check: ~570, 730, 630). Fractional dead time is {100*res['frac'].min():.1f}-{100*res['frac'].max():.1f} %"
          f", far below Knoll's recommended >= 20 %.")

    # ---- E1: per-run tau ----
    fig, ax = plt.subplots(figsize=(W_HALF, 3.0))
    x = res["run"].to_numpy()
    ax.axhspan(mean - sem, mean + sem, color=BLUE, alpha=0.20, lw=0, label="mean $\\pm$ SEM")
    ax.errorbar(x, taus, yerr=res["stau"] * 1e6, fmt="o", color=BLUE, capsize=3, mec=SURFACE, label="per run")
    ax.axhline(TAU_DEAD_SCOPE * 1e6, color=GREEN, ls="--", label="scope dead time")
    ax.axhline(TAU_RECOVERY_SCOPE * 1e6, color=PURPLE, ls="-.", label="scope recovery time")
    ax.set_xticks([1, 2, 3])
    ax.set_xlim(0.5, 3.5)
    ax.set_ylim(-400, 2300)
    ax.set_xlabel("run")
    ax.set_ylabel("dead time $\\tau$ ($\\mu$s)")
    title(ax, "Two-source dead time per run")
    leg(ax, "upper left")
    fig.tight_layout()
    save(fig, "E1_tau_per_run")
    return df, res, (Np, Tp, taup, sp, mean, sd, sem)


def scope_overlay():
    """Scope screenshots with markers at the dead-time and recovery-time cursor positions.
    Time axis: 100 us/div, trigger point (screen centre) at 440 us delay, 10 divisions across."""
    if not (SCOPE_DEAD_IMG.exists() and SCOPE_REC_IMG.exists()):
        print(f"\nScope screenshots not found in {SCOPE_DIR}: ASK where print_008/print_009 are.")
        return None
    fig, axs = plt.subplots(1, 2, figsize=(W_FULL, 2.8))
    items = [(SCOPE_DEAD_IMG, -2.0, 358.0, "$\\tau$ = 360 $\\mu$s", GREEN),
             (SCOPE_REC_IMG, -2.0, 838.0, "$T_r$ = 480 $\\mu$s (cursor)", PURPLE)]
    for ax, (path, t0, t1, lab, c) in zip(axs, items):
        img = plt.imread(path)
        H, W = img.shape[:2]
        ax.imshow(img[: int(H * 0.88)], aspect="auto")
        ax.grid(False)
        ax.axis("off")
        centre = W * 0.51
        for t in (t0, t1):
            x = centre + (t - 440.0) * (W / 1024.0)
            ax.axvline(x, color=c, lw=1.4, ls="--")
        xa = centre + (t0 - 440.0) * (W / 1024.0)
        xb = centre + (t1 - 440.0) * (W / 1024.0)
        yy = H * 0.52
        ax.annotate("", xy=(xb, yy), xytext=(xa, yy), arrowprops=dict(arrowstyle="<->", color=c, lw=1.4))
        ax.text((xa + xb) / 2, yy - H * 0.03, lab, color=c, ha="center", va="bottom", fontsize=FONT,
                bbox=dict(fc=SURFACE, ec="none", pad=1.5))
    fig.tight_layout()
    save(fig, "E5_scope_dead_and_recovery_time")
    print(f"\nScope screenshots: markers drawn at the saved cursor positions (dead 360 us, recovery 480 us). "
          f"Notebook lists recovery = {TAU_RECOVERY_SCOPE*1e6:.0f} us; the screenshot cursors read 480.0 us.")
    return fig


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


def make_tables(dc, dph, al, pb, C_bg, T_bg, ts_df, ts_res):
    pm = "$\\pm$"
    tex_table("t1_counting_curve_raw", "Counting-curve data (Th-232 source).", "tab:counting-raw",
              ["HV (V)", "Counts", "$\\Delta t$ (s)", "Pulse height (mV)"],
              [[f"{r.hv:.0f}", f"{r.counts:.0f}", f"{COUNT_TIME:g}",
                "0" if r.amp == 0 else f"{r.amp:.2f} {pm} {r.samp:.2f}"] for r in dc.itertuples()])
    tex_table("t2_pulse_height_raw", "Pulse-height consistency data, MCA spectra.", "tab:ph-raw",
              ["Source", "Centroid channel", "Gross counts", "Real time (s)"],
              [[r.source, f"{r.centroid_channel:.0f}", f"{r.gross_counts:.0f}", f"{r.real_time_s:.0f}"]
               for r in dph.itertuples()], spec="lrrr")
    allb = pd.read_csv(ATTEN_CSV, keep_default_na=False, na_values=[""]).iloc[:, :4].dropna(subset=["Counts"])
    allb.columns = ["m", "t", "c", "dt"]
    tex_table("t3_beta_raw", "Beta attenuation data, Co-60 source.", "tab:beta-raw",
              ["Material", "Mass thickness (mg/cm$^2$)", "Counts", "Time (s)"],
              [[r.m, f"{r.t:g}", f"{r.c:.0f}", f"{r.dt:.0f}"] for r in allb.itertuples()], spec="lrrr")
    tex_table("t4_two_source_raw", f"Two-source data, $T = {T_TWO_SRC:g}$ s per measurement.", "tab:twosrc-raw",
              ["Run", "Background", "Th-232", "Cl-36", "Both"],
              [[i, r.Nb, r.N1, r.N2, r.N12] for i, r in ts_df.iterrows()], spec="lrrrr")
    # analysis tables
    tex_table("t5a_counting_rates", "Counting-curve rates, $\\sigma_r=\\sqrt{N}/t$.", "tab:counting-rates",
              ["HV (V)", "Rate (s$^{-1}$)", "$\\sigma_r$ (s$^{-1}$)"],
              [[f"{r.hv:.0f}", f"{r.rate:.2f}", f"{r.srate:.2f}"] for r in dc.itertuples()])
    tex_table("t5b_beta_net_rates", "Net beta rates and uncertainties (aluminum).", "tab:beta-net",
              ["$t$ (mg/cm$^2$)", "$r$ (s$^{-1}$)", "$\\sigma_r$ (s$^{-1}$)", "$\\ln r$", "$\\sigma_y$", "$\\sigma_x$ (mg/cm$^2$)"],
              [[f"{r.t_mg:.2f}", f"{r.r:.2f}", f"{r.sr:.2f}", f"{r.y:.3f}", f"{r.sy:.3f}", f"{r.sx:.1f}"]
               for r in al.itertuples()])
    tex_table("t5c_dead_time_runs", "Two-source dead time per run (Eq.~4.32), Poisson uncertainties.", "tab:tau-runs",
              ["Run", "$m_1$", "$m_2$", "$m_{12}$", "$m_b$", "$Z$", "$\\tau$ ($\\mu$s)", "$\\sigma_\\tau$ ($\\mu$s)", "$m_{12}\\tau$ (\\%)"],
              [[int(r.run), f"{r.m1:.1f}", f"{r.m2:.1f}", f"{r.m12:.1f}", f"{r.mb:.2f}", f"{r.Z:.3f}",
                f"{r.tau*1e6:.0f}", f"{r.stau*1e6:.0f}", f"{100*r.frac:.1f}"] for r in ts_res.itertuples()])
    print(f"\nwrote 7 LaTeX tables to {TAB_DIR}")


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


if __name__ == "__main__":
    print("settings:", dict(SHOW_TITLES=SHOW_TITLES, KNEE_HV=KNEE_HV, PLATEAU=PLATEAU, PLATEAU_ALTS=PLATEAU_ALTS,
                            AMP_FIT_RANGE=AMP_FIT_RANGE, SUBFITS=list(SUBFITS), PLOT_SUBFITS=PLOT_SUBFITS,
                            TAIL_POINTS=TAIL_POINTS, N_EXPECTED_CM2G=N_EXPECTED_CM2G, INCLUDE_PB=INCLUDE_PB))
    dc = load_counting()
    plot_amplitude(dc)
    plot_counting(dc)
    dph = load_ph()
    plot_ph(dph)
    al, pb, C_bg, T_bg, fits = beta_attenuation()
    ts_df, ts_res, _ = dead_time()
    scope_overlay()
    make_tables(dc, dph, al, pb, C_bg, T_bg, ts_df, ts_res)
    write_summary()
    plt.close("all")
