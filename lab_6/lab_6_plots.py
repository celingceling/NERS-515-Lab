"""
NERS 515 Lab 6 (scintillation detectors): every plot, number and table for the report.

Run from anywhere:  python3 lab_6_plots.py
Reads   SPE_files/*.Spe (MAESTRO ASCII: $MEAS_TIM: live real, $DATA:) and
        "Lab_6_Data - voltage vs photopeak.csv" (HV scan, 2x2 NaI(Tl), 20 s live, amp gain 20 x 0.5)
Writes  figures/*.png + *.pdf, tables/*.tex, results_summary.txt, results_summary.csv

Sources: Knoll 4th ed., the Lab 6 manual, lecture slides and our Lab 2 report only.
Never edits the raw files. Needs numpy, matplotlib, scipy.
"""
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

ROOT = Path(__file__).resolve().parent
SPE_DIR = ROOT / "SPE_files"
HV_CSV = ROOT / "Lab_6_Data - voltage vs photopeak.csv"
FIG_DIR, TAB_DIR = ROOT / "figures", ROOT / "tables"

# ---- configurations: (key, file stem with %s, label, photopeak search window in channels) ----
CONFIGS = [
    ("NaI2x2_WC", "NaI_%s_WC",       "2x2 NaI(Tl), grease",    (700, 1000)),
    ("NaI1x1_WC", "NaI1x1_%s_WC",    "1x1 NaI(Tl), grease",    (550, 800)),
    ("NaI1x1_NC", "NaI1x1_%s_NC",    "1x1 NaI(Tl), no grease", (550, 800)),
    ("BGO_WC",    "BGO_%s_WC",       "1x1 BGO, grease",        (100, 220)),
    ("CsI_WC",    "CsI(TI)_%s_WC",   "1x1 CsI(Tl), grease",    (340, 460)),
    ("EJ200_WC",  "EJ-200_%s_WC",    "1x1 EJ-200, grease",     None),       # no photopeak
]
DIST = [("source", "0 in"), ("2inch", "2 in")]
NO_PEAK = {("CsI_WC", "source")}   # no resolvable photopeak in the net spectrum (only a shoulder)

# ---- constants from sources ------------------------------------------------
E_GAMMA = 662.0     # keV, Cs-137 / Ba-137m gamma (Knoll Table 1.2; Eq. 10.14 discussion)
ME_C2 = 511.0       # keV
E_BAX = 32.0        # keV, Ba K X-rays "about 32 keV" (Knoll p. 252)
CAL_SLOPE, CAL_INT, CAL_SV = 765.8, 27.6, 0.0254   # channel = 765.8 V + 27.6, sigma_V = 25.4 mV (Lab 2)

# ---- judgment calls (named so they can be changed) ------------------------
K_ROI = 1.5         # ROI = centroid +/- K_ROI * FWHM
K_ROI_ALT = (1.0, 2.0)   # sensitivity check
N_SIDE = 3          # channels averaged on each side of the ROI for the linear continuum (Knoll p. 728)
FIT_V = (600, 1000) # V, points used for the log-log gain fit (centroid stops rising above 1000 V)
XMAX = {"NaI2x2_WC": 1300, "NaI1x1_WC": 1100, "NaI1x1_NC": 1100, "BGO_WC": 450,
        "CsI_WC": 700, "EJ200_WC": 300}

# MAESTRO values typed into the Lab_6_Data sheet (for the cross-check only)
SHEET = {("NaI2x2_WC", "source"): (500662, 836.3, 60.0), ("NaI2x2_WC", "2inch"): (146649, 819.5, 61.34),
         ("NaI1x1_NC", "source"): (479750, 663.01, 53.29), ("NaI1x1_NC", "2inch"): (31793, 747.7, 42.31),
         ("NaI1x1_WC", "source"): (468213, 682.16, 52.89), ("NaI1x1_WC", "2inch"): (31425, 662.99, 44.85),
         ("BGO_WC", "source"): (2943641, 146.19, 26.59)}

# ---- plot style (copied from lab_5_plots.py) -------------------------------
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e3e2de"
BLUE, ORANGE, GRAY = "#2a78d6", "#eb6834", "#8a8984"
GREEN, PURPLE, BLACK = "#009E73", "#CC79A7", "#000000"
FONT = 11
W_HALF = 3.5
plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "axes.edgecolor": INK2, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False,
    "font.size": FONT, "axes.labelsize": FONT, "xtick.labelsize": FONT, "ytick.labelsize": FONT,
    "legend.fontsize": FONT - 1, "lines.linewidth": 1.2, "lines.markersize": 5,
    "savefig.facecolor": SURFACE,
})
COL = {"source": BLUE, "2inch": ORANGE}
RESULTS = []


def R(name, value, unc=None, unit="", src=""):
    RESULTS.append((name, value, unc, unit, src))


def leg(ax, loc):
    ax.legend(loc=loc, frameon=True, framealpha=0.9, edgecolor="none", handlelength=1.4,
              borderpad=0.3, labelspacing=0.25, borderaxespad=0.3)


def leg_top(ax, ncol=2):
    """Legend above the axes so it never covers data."""
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=ncol, frameon=False,
              handlelength=1.2, columnspacing=0.9, borderaxespad=0.2, labelspacing=0.2)


def save(fig, name):
    FIG_DIR.mkdir(exist_ok=True)
    fig.savefig(FIG_DIR / f"{name}.png", dpi=200)
    fig.savefig(FIG_DIR / f"{name}.pdf")
    plt.close(fig)


def volt_axis(ax):
    """Right axis: MCA channel -> amplitude (V), Lab 2 calibration channel = 765.8 V + 27.6."""
    sec = ax.secondary_yaxis("right", functions=(lambda c: (np.asarray(c) - CAL_INT) / CAL_SLOPE,
                                                 lambda v: CAL_SLOPE * np.asarray(v) + CAL_INT))
    sec.set_ylabel("amplitude (V)")
    return sec


# =========================================================================
# Loading
# =========================================================================
def read_spe(path):
    lines = path.read_text().splitlines()
    i = lines.index("$MEAS_TIM:")
    live, real = map(float, lines[i + 1].split())
    j = lines.index("$DATA:")
    a, b = map(int, lines[j + 1].split())
    counts = np.array([int(x) for x in lines[j + 2:j + 3 + b - a]], float)
    return dict(live=live, real=real, counts=counts, date=lines[lines.index("$DATE_MEA:") + 1])


def load_spectra():
    S = {}
    for key, stem, _, _ in CONFIGS:
        S[key] = {t: read_spe(SPE_DIR / f"{stem % t}.Spe") for t in ("bg", "source", "2inch")}
        bg = S[key]["bg"]
        for t, _ in DIST:
            s = S[key][t]
            k = s["live"] / bg["live"]
            # net = (N_s/t_s - N_b/t_b) t_s, sigma^2 = N_s + (t_s/t_b)^2 N_b  (sigma_N = sqrt(N), quadrature)
            s["net"] = s["counts"] - k * bg["counts"]
            s["var"] = s["counts"] + k**2 * bg["counts"]
            s["k"] = k
    return S


def load_hv():
    rows = list(csv.reader(HV_CSV.open()))[1:]
    hv, c, a, f = (np.array([float(r[i]) for r in rows]) for i in range(4))
    sc = (f / 2.35) / np.sqrt(a)   # sigma_c = (FWHM/2.35)/sqrt(A), Knoll p. 728 (A = gross area recorded)
    return hv, c, a, f, sc


# =========================================================================
# Photopeak analysis on the net spectrum
# =========================================================================
def half_max(pk, var, lo_ch):
    """FWHM of a continuum-subtracted peak by linear interpolation of the half-maximum crossings.
    Y = mean of the 3 channels around the maximum. sigma of each crossing = sigma_y/|slope|, with
    sigma_y combining the counts at the crossing and sigma_Y/2 (quadrature)."""
    im = int(np.argmax(pk))
    Y = pk[im - 1:im + 2].mean()
    sY = np.sqrt(var[im - 1:im + 2].sum()) / 3
    h = Y / 2
    i = im
    while pk[i] > h:
        i -= 1
    s_l = pk[i + 1] - pk[i]
    xl = i + (h - pk[i]) / s_l
    sxl = np.sqrt((var[i] + var[i + 1]) / 2 + (sY / 2) ** 2) / abs(s_l)
    i = im
    while pk[i] > h:
        i += 1
    s_r = pk[i] - pk[i - 1]
    xr = (i - 1) + (h - pk[i - 1]) / s_r
    sxr = np.sqrt((var[i] + var[i - 1]) / 2 + (sY / 2) ** 2) / abs(s_r)
    return xr - xl, np.hypot(sxl, sxr), lo_ch + xl, lo_ch + xr, Y


def photopeak(net, var, raw, window, k_roi=K_ROI):
    lo, hi = window
    sm = np.convolve(net, np.ones(9) / 9, "same")
    c = lo + int(np.argmax(sm[lo:hi]))
    i = c
    while sm[i] > sm[c] / 2:
        i -= 1
    F = 2 * (c - i)
    for _ in range(20):
        L, Rr = int(round(c - k_roi * F)), int(round(c + k_roi * F))
        bl, br = net[L - N_SIDE:L].mean(), net[Rr + 1:Rr + 1 + N_SIDE].mean()
        vbl, vbr = var[L - N_SIDE:L].sum() / N_SIDE**2, var[Rr + 1:Rr + 1 + N_SIDE].sum() / N_SIDE**2
        ch = np.arange(L, Rr + 1)
        line = bl + (br - bl) * (ch - L) / (Rr - L)
        pk = net[L:Rr + 1] - line
        n = len(ch)
        A = pk.sum()
        sA = np.sqrt(var[L:Rr + 1].sum() + (n / 2) ** 2 * (vbl + vbr))
        c_new = (ch * pk).sum() / A
        F_new, sF, xl, xr, Y = half_max(pk, var[L:Rr + 1], L)
        done = abs(c_new - c) < 0.01 and abs(F_new - F) < 0.01
        c, F = c_new, F_new
        if done:
            break
    sc = (F / 2.35) / np.sqrt(A)
    Rres = F / c
    sR = Rres * np.hypot(sF / F, sc / c)
    return dict(c=c, sc=sc, F=F, sF=sF, A=A, sA=sA, R=Rres, sR=sR, L=L, Rch=Rr, bl=bl, br=br,
                cont=n * (bl + br) / 2, gross=raw[L:Rr + 1].sum(), xl=xl, xr=xr, Y=Y)


def gauss_lin(x, A, H, sg, a, b):
    """Gaussian of area A, centroid H, width sg on a straight-line continuum a + b (x - H)."""
    return A / (sg * np.sqrt(2 * np.pi)) * np.exp(-((x - H) ** 2) / (2 * sg**2)) + a + b * (x - H)


def gauss_fit(net, var, c, F, k_roi=K_ROI, fixwin=None):
    """Knoll Ch. 18 (p. 728): least-squares fit of a Gaussian plus a straight-line continuum to the net
    spectrum, weights 1/sigma_net^2. ROI = c +/- k_roi FWHM, iterated until H0 and FWHM change < 0.01 ch.
    Area, centroid and width come from the fitted parameters, uncertainties from the fit covariance."""
    for it in range(30):
        L, Rr = fixwin if fixwin else (int(round(c - k_roi * F)), int(round(c + k_roi * F)))
        x = np.arange(L, Rr + 1)
        y, sy = net[L:Rr + 1], np.sqrt(np.clip(var[L:Rr + 1], 1, None))
        p0 = [max(y.sum() - 0.5 * (y[0] + y[-1]) * len(x), 1.0), c, F / 2.3548, 0.5 * (y[0] + y[-1]),
              (y[-1] - y[0]) / (Rr - L)]
        par, cov = curve_fit(gauss_lin, x, y, p0=p0, sigma=sy, absolute_sigma=True, maxfev=20000)
        e = np.sqrt(np.diag(cov))
        chi2 = float((((y - gauss_lin(x, *par)) / sy) ** 2).sum())
        ndf = len(x) - 5
        H, Fn = par[1], 2.3548 * abs(par[2])
        done = fixwin is not None or (abs(H - c) < 0.01 and abs(Fn - F) < 0.01)
        c, F = H, Fn
        if done:
            break
    A, sA, sH, sF = par[0], e[0], e[1], 2.3548 * e[2]
    Rres = F / H
    sR = Rres * np.sqrt((sF / F) ** 2 + (sH / H) ** 2)
    return dict(c=H, sc=sH, F=F, sF=sF, A=A, sA=sA, R=Rres, sR=sR, L=L, Rch=Rr, par=par, cov=cov,
                chi2=chi2, ndf=ndf, passes=it + 1, Y=par[0] / (abs(par[2]) * np.sqrt(2 * np.pi)))


def edge_half_height(net, lo, hi):
    """Compton edge as the channel where the smoothed net spectrum falls halfway from the shoulder
    maximum to the minimum on its high side, searched in [lo, hi]."""
    sm = np.convolve(net, np.ones(15) / 15, "same")
    ish = lo + int(np.argmax(sm[lo:hi]))
    ival = ish + int(np.argmin(sm[ish:hi + 150]))
    h = (sm[ish] + sm[ival]) / 2
    i = ish
    while sm[i] > h:
        i += 1
    return i - 1 + (sm[i - 1] - h) / (sm[i - 1] - sm[i]), ish, ival


# =========================================================================
# HV scan
# =========================================================================
def hv_scan():
    hv, c, a, f, sc = load_hv()
    print("\n--- HV scan (2x2 NaI(Tl), 20 s live, amp gain 20 x 0.5) ---")
    for v, ci, ai, fi, si in zip(hv, c, a, f, sc):
        print(f"  {v:5.0f} V: C = {ci:8.2f} +/- {si:.3f} ch ({(ci - CAL_INT) / CAL_SLOPE:.3f} V), A = {ai:.0f}, FWHM = {fi}")
    m = (hv >= FIT_V[0]) & (hv <= FIT_V[1])
    x, y = np.log(hv[m]), np.log(c[m])
    b, a0 = np.polyfit(x, y, 1)
    res = y - (a0 + b * x)
    sb = np.sqrt((res**2).sum() / (len(x) - 2) / ((x - x.mean()) ** 2).sum())
    R("gain exponent (slope ln C vs ln V, 600-1000 V)", b, sb, "", "least squares, Knoll Eq. 9.3 G ~ V^(beta N)")
    loc = np.diff(np.log(c)) / np.diff(np.log(hv))
    print(f"log-log slope {FIT_V[0]}-{FIT_V[1]} V: {b:.3f} +/- {sb:.3f}")
    print("two-point local slopes:", ", ".join(f"{hv[i]:.0f}-{hv[i+1]:.0f}: {s:.2f}" for i, s in enumerate(loc)))
    for v in (1000, 1050, 1150):
        ci = c[hv == v][0]
        R(f"HV-scan centroid at {v:.0f} V", ci, sc[hv == v][0], "channel", "MAESTRO, Lab_6_Data")
        R(f"HV-scan amplitude at {v:.0f} V", (ci - CAL_INT) / CAL_SLOPE, CAL_SV, "V", "Lab 2 calibration")

    fig, ax = plt.subplots(figsize=(W_HALF, 2.8))
    ax.errorbar(hv, c, yerr=sc, fmt="o", color=BLUE, mec=SURFACE, capsize=2)
    ax.set_xlabel("high voltage (V)")
    ax.set_ylabel("centroid (channel)")
    volt_axis(ax)
    fig.tight_layout()
    save(fig, "F1_hv_centroid")

    fig, ax = plt.subplots(figsize=(W_HALF, 2.8))
    ax.errorbar(hv[m], c[m], yerr=sc[m], fmt="o", color=BLUE, mec=SURFACE, capsize=2, label="600–1000 V (fit)")
    ax.errorbar(hv[~m], c[~m], yerr=sc[~m], fmt="o", mfc="none", color=BLUE, capsize=2, label="1050–1150 V")
    xx = np.linspace(FIT_V[0], FIT_V[1], 50)
    ax.plot(xx, np.exp(a0) * xx**b, color=ORANGE, lw=1.2, label=f"slope {b:.2f}")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks([600, 700, 800, 1000, 1150])
    ax.set_xticklabels(["600", "700", "800", "1000", "1150"])
    ax.minorticks_off()
    ax.set_xlabel("high voltage (V)")
    ax.set_ylabel("centroid (channel)")
    leg(ax, "upper left")
    fig.tight_layout()
    save(fig, "F2_hv_centroid_loglog")
    return dict(hv=hv, c=c, a=a, f=f, sc=sc, b=b, sb=sb)


# =========================================================================
# Spectra plots
# =========================================================================
def band(ax, y, var, color, label, xmax, alpha=0.55):
    x = np.arange(xmax)
    y, s = y[:xmax], np.sqrt(np.clip(var[:xmax], 0, None))
    yp = np.where(y > 0, y, np.nan)
    ax.fill_between(x, np.clip(y - s, 0.5, None), y + s, color=color, alpha=0.25, lw=0, step="mid")
    ax.step(x, yp, where="mid", color=color, alpha=alpha + 0.2, lw=0.8, label=label)


def spectra_plots(S, which):
    """which = 'raw' (gross 2-min source spectra) or 'net' (background subtracted)."""
    for key, _, label, _ in CONFIGS:
        fig, ax = plt.subplots(figsize=(W_HALF, 2.6))
        xm = XMAX[key]
        keys = [key] if key != "NaI1x1_WC" else ["NaI1x1_WC", "NaI1x1_NC"]
        if key == "NaI1x1_NC":
            plt.close(fig)
            continue
        for kk in keys:
            for t, tl in DIST:
                s = S[kk][t]
                y, v = (s["counts"], s["counts"]) if which == "raw" else (s["net"], s["var"])
                col = COL[t] if kk.endswith("WC") else (PURPLE if t == "source" else GREEN)
                lab = tl if len(keys) == 1 else f"{tl}, {'grease' if kk.endswith('WC') else 'no gr.'}"
                band(ax, y, v, col, lab, xm)
        ax.set_yscale("log")
        ax.set_xlim(0, xm)
        ax.set_ylim(bottom=0.8)
        ax.set_xlabel("channel")
        ax.set_ylabel("counts per channel" if which == "raw" else "net counts per channel")
        leg_top(ax, 2)
        fig.tight_layout()
        save(fig, f"{'F3' if which == 'raw' else 'F5'}_{which}_{key}")


def bg_plot(S):
    fig, ax = plt.subplots(figsize=(W_HALF, 2.6))
    cols = [BLUE, ORANGE, PURPLE, GREEN, BLACK, GRAY]
    names = ["2x2 NaI", "1x1 NaI", "1x1 NaI, no gr.", "BGO", "CsI(Tl)", "EJ-200"]
    fig.set_size_inches(W_HALF, 3.0)
    for (key, *_), col, nm in zip(CONFIGS, cols, names):
        b = S[key]["bg"]["counts"]
        bb = b[:2048].reshape(-1, 16).sum(1)          # 16-channel bins for readability
        x = np.arange(len(bb)) * 16 + 8
        ax.errorbar(x, np.where(bb > 0, bb, np.nan), yerr=np.sqrt(bb), fmt="-", color=col, lw=0.9,
                    elinewidth=0.5, alpha=0.8, label=nm)
    ax.set_yscale("log")
    ax.set_xlim(0, 2048)
    ax.set_xlabel("channel")
    ax.set_ylabel("counts per 16 channels")
    leg_top(ax, 2)
    fig.tight_layout()
    save(fig, "F4_backgrounds")


def labeled_nai(S, pk):
    """Net 2x2 NaI(Tl) spectrum at 2 in with the predicted feature positions. Energy -> channel through the
    photopeak and the Lab 2 zero (channel 27.6 at 0 V): ch = 27.6 + E (H0 - 27.6)/662."""
    s = S["NaI2x2_WC"]["2inch"]
    H0 = pk[("NaI2x2_WC", "2inch")]["c"]
    ch_of = lambda E: CAL_INT + E * (H0 - CAL_INT) / E_GAMMA
    E_of = lambda ch: E_GAMMA * (ch - CAL_INT) / (H0 - CAL_INT)
    eps = 2 * E_GAMMA / ME_C2
    E_ce = E_GAMMA * eps / (1 + eps)            # Compton edge, Knoll Eq. 10.4
    E_bs = E_GAMMA / (1 + eps)                  # backscatter, Knoll Eq. 10.3 at theta = pi
    pred = {"Compton edge": E_ce, "backscatter": E_bs, "Ba K X-ray": E_BAX}
    sm = np.convolve(s["net"], np.ones(9) / 9, "same")
    meas = {}
    meas["Ba K X-ray"] = 10 + int(np.argmax(sm[10:120]))
    ce, ish, ival = edge_half_height(s["net"], int(ch_of(E_ce)) - 120, int(ch_of(E_ce)) + 40)
    meas["Compton edge"] = ce
    # backscatter: the only local maximum of the continuum between the X-ray peak and the edge shoulder
    lo = int(ch_of(100.0))
    meas["backscatter"] = lo + int(np.argmax(sm[lo:ish - 100]))
    print("\n--- Features, 2x2 NaI(Tl) 2 in (calibration through Lab 2 zero and the photopeak) ---")
    for nm in pred:
        print(f"  {nm:13s}: predicted {pred[nm]:6.1f} keV -> ch {ch_of(pred[nm]):6.1f};"
              f" measured ch {meas[nm]:6.1f} -> {E_of(meas[nm]):6.1f} keV")
        R(f"{nm} predicted energy", pred[nm], None, "keV", "Knoll Eqs. 10.3-10.4 / p. 252")
        R(f"{nm} measured channel (2x2 NaI, 2 in)", meas[nm], None, "channel", "local max / edge half-height, net spectrum")
        R(f"{nm} measured energy (2x2 NaI, 2 in)", E_of(meas[nm]), None, "keV", "ch -> E through Lab 2 zero and photopeak")
    print(f"  Compton edge shoulder max ch {ish}, valley min ch {ival}")

    fig, ax = plt.subplots(figsize=(W_HALF, 3.0))
    band(ax, s["net"], s["var"], BLUE, None, 1100)
    ax.set_yscale("log")
    ax.set_xlim(0, 1100)
    ax.set_ylim(5, 2e5)
    ax.set_xlabel("channel")
    ax.set_ylabel("net counts per channel")
    # vertical labels just left of each dashed line, above the spectrum
    for t, x in (("photopeak", H0), ("Compton edge", meas["Compton edge"]),
                 ("backscatter", meas["backscatter"])):
        ax.text(x - 10, 2600, t, rotation=90, ha="right", va="bottom", fontsize=FONT - 1, color=INK)
    ax.text(meas["Ba K X-ray"] + 12, 2600, "Ba X-ray", rotation=90, ha="left", va="bottom", fontsize=FONT - 1,
            color=INK)
    ax.text(420, 120, "Compton continuum", ha="center", va="bottom", fontsize=FONT - 1, color=INK)
    for x in (H0, meas["Compton edge"], meas["backscatter"], meas["Ba K X-ray"]):
        ax.axvline(x, color=GRAY, lw=0.8, ls="--", zorder=0)
    fig.tight_layout()
    save(fig, "F6_labeled_NaI2x2")
    return meas, pred, E_of


# =========================================================================
def analyse(S):
    pk, alt = {}, {}
    print("\n--- Photopeaks (net spectrum, linear continuum, ROI = c +/- %.1f FWHM) ---" % K_ROI)
    for key, _, label, win in CONFIGS:
        for t, tl in DIST:
            s = S[key][t]
            tot = s["net"].sum()
            stot = np.sqrt(s["var"].sum())
            s["tot"], s["stot"] = tot, stot
            R(f"net total counts {key} {tl}", tot, stot, "counts", "sum of net spectrum, all channels")
            if (key, t) in NO_PEAK:
                print(f"  {key:10s} {tl}: NO resolvable photopeak; net total {tot:.0f} +/- {stot:.0f}")
                continue
            if win is None:
                ce, ish, ival = edge_half_height(s["net"], 40, 200)
                s["edge"] = ce
                print(f"  {key:10s} {tl}: no photopeak; Compton edge (half-height) ch {ce:.1f}; net total {tot:.0f} +/- {stot:.0f}")
                R(f"Compton edge channel {key} {tl}", ce, None, "channel", "edge half-height, net spectrum")
                continue
            ps = photopeak(s["net"], s["var"], s["counts"], win)          # summation: start values only
            p = gauss_fit(s["net"], s["var"], ps["c"], ps["F"])
            q = gauss_fit(s["net"], s["var"], ps["c"], ps["F"], K_ROI_ALT[0])
            q2 = gauss_fit(s["net"], s["var"], ps["c"], ps["F"], K_ROI_ALT[1])
            pk[(key, t)], alt[(key, t)] = p, (q, q2)
            dA = 100 * (q["A"] - p["A"]) / p["A"]
            dA2 = 100 * (q2["A"] - p["A"]) / p["A"]
            print(f"  {key:10s} {tl}: C = {p['c']:.2f}+/-{p['sc']:.2f}  FWHM = {p['F']:.2f}+/-{p['sF']:.2f}  "
                  f"R = {100*p['R']:.2f}+/-{100*p['sR']:.2f}%  A = {p['A']:.0f}+/-{p['sA']:.0f}  ROI [{p['L']},{p['Rch']}]"
                  f"  chi2/ndf = {p['chi2']:.0f}/{p['ndf']} = {p['chi2']/p['ndf']:.2f}  passes {p['passes']}"
                  f" | +/-1 FWHM: A {dA:+.1f}%, F {q['F']:.1f}; +/-2 FWHM: A {dA2:+.1f}%, F {q2['F']:.1f}"
                  f" | summation: A {ps['A']:.0f}, C {ps['c']:.1f}, F {ps['F']:.1f} | net total {tot:.0f}+/-{stot:.0f}"
                  f"  P/T = {p['A']/tot:.3f}")
            for nm, v, u, un in (("centroid", p["c"], p["sc"], "channel"), ("FWHM", p["F"], p["sF"], "channel"),
                                 ("resolution", 100 * p["R"], 100 * p["sR"], "%"), ("net photopeak counts", p["A"], p["sA"], "counts")):
                R(f"{nm} {key} {tl}", v, u, un, "Gaussian + line fit to net spectrum, Knoll p. 728; Eq. 10.14")
            R(f"chi2/ndf {key} {tl}", p["chi2"] / p["ndf"], None, "", f"{p['chi2']:.0f}/{p['ndf']}")
            R(f"net photopeak counts +/-1 FWHM ROI {key} {tl}", q["A"], q["sA"], "counts", "ROI sensitivity check")
            R(f"net photopeak counts +/-2 FWHM ROI {key} {tl}", q2["A"], q2["sA"], "counts", "ROI sensitivity check")
            R(f"photopeak/total {key} {tl}", p["A"] / tot, None, "", "net peak / net total")
            if (key, t) in SHEET:
                a, c, f = SHEET[(key, t)]
                print(f"      sheet (MAESTRO): area {a}, centroid {c}, FWHM {f}")
    return pk, alt


def net_peak_plots(S, pk):
    """F7. Net photopeak: background-subtracted counts minus the fitted straight-line continuum, +/-1 sigma
    band (counting only), the fitted Gaussian, its FWHM and centroid."""
    for (key, t), p in pk.items():
        s = S[key][t]
        L, Rr = p["L"], p["Rch"]
        A, H, sg, a, b = p["par"]
        ch = np.arange(L, Rr + 1)
        y = s["net"][L:Rr + 1] - (a + b * (ch - H))
        sig = np.sqrt(np.clip(s["var"][L:Rr + 1], 0, None))
        xx = np.linspace(L, Rr, 600)
        fig, ax = plt.subplots(figsize=(W_HALF, 2.5))
        ax.fill_between(ch, y - sig, y + sig, color=BLUE, alpha=0.25, lw=0, step="mid")
        ax.step(ch, y, where="mid", color=BLUE, lw=0.9, label="net peak")
        ax.plot(xx, gauss_lin(xx, A, H, sg, 0, 0), color=BLACK, lw=1.1, label="fit")
        ax.hlines(p["Y"] / 2, H - p["F"] / 2, H + p["F"] / 2, color=ORANGE, lw=1.6, label="FWHM")
        ax.axvline(H, color=GRAY, ls="--", lw=0.9)
        ax.axhline(0, color=INK2, lw=0.6)
        ax.set_xlim(L, Rr)
        ax.set_xlabel("channel")
        ax.set_ylabel("net peak counts")
        leg_top(ax, 3)
        fig.tight_layout()
        save(fig, f"F7_peak_{key}_{t}")


def net_peak_overlays(S, pk):
    """F8. Net photopeaks (background and fitted continuum removed) overlaid by distance for each crystal,
    log y as in F3/F5. Step: data, +/-1 sigma band. Thin line: fitted Gaussian. Bar: FWHM at half maximum."""
    groups = [("NaI2x2_WC", ["NaI2x2_WC"]), ("NaI1x1_WC", ["NaI1x1_WC", "NaI1x1_NC"]),
              ("BGO_WC", ["BGO_WC"]), ("CsI_WC", ["CsI_WC"])]
    for name, keys in groups:
        fig, ax = plt.subplots(figsize=(W_HALF, 2.6))
        lo, hi, ymin = 1e9, 0, 1e9
        for kk in keys:
            for t, tl in DIST:
                if (kk, t) not in pk:
                    continue
                p, s = pk[(kk, t)], S[kk][t]
                A, H, sg, a, b = p["par"]
                L, Rr = p["L"], p["Rch"]
                ch = np.arange(L, Rr + 1)
                y = s["net"][L:Rr + 1] - (a + b * (ch - H))
                sig = np.sqrt(np.clip(s["var"][L:Rr + 1], 0, None))
                col = COL[t] if kk.endswith("WC") else (PURPLE if t == "source" else GREEN)
                lab = tl if len(keys) == 1 else f"{tl}, {'grease' if kk.endswith('WC') else 'no gr.'}"
                ax.fill_between(ch, np.clip(y - sig, 0.5, None), y + sig, color=col, alpha=0.25, lw=0, step="mid")
                ax.step(ch, np.where(y > 0, y, np.nan), where="mid", color=col, lw=0.8, alpha=0.8, label=lab)
                xx = np.linspace(L, Rr, 600)
                ax.plot(xx, gauss_lin(xx, A, H, sg, 0, 0), color=col, lw=1.0, ls="--")
                ax.hlines(p["Y"] / 2, H - p["F"] / 2, H + p["F"] / 2, color=col, lw=2.0)
                lo, hi, ymin = min(lo, L), max(hi, Rr), min(ymin, p["Y"])
        ax.set_yscale("log")
        ax.set_xlim(lo, hi)
        ax.set_ylim(max(1.0, ymin / 100), None)
        ax.set_xlabel("channel")
        ax.set_ylabel("net peak counts")
        leg_top(ax, 2)
        fig.tight_layout()
        save(fig, f"F8_peaks_{name}")


def no_peak_checks(S):
    """Gaussian + line fits for the spectra without a clear photopeak, over several fixed windows."""
    print("\n--- Fits where no photopeak is evident (fixed windows) ---")
    trials = {("CsI_WC", "source"): [(300, 470), (320, 470), (330, 480), (340, 470), (350, 460), (300, 500)],
              ("EJ200_WC", "source"): [(40, 110), (45, 100), (35, 130), (30, 150)],
              ("EJ200_WC", "2inch"): [(40, 110), (45, 100), (35, 130), (30, 150)]}
    for (key, t), wins in trials.items():
        s = S[key][t]
        for w in wins:
            try:
                with np.errstate(all="ignore"):
                    f = gauss_fit(s["net"], s["var"], (w[0] + w[1]) / 2, (w[1] - w[0]) / 3, fixwin=w)
                print(f"  {key:9s} {t:6s} window {w}: H0 = {f['c']:.1f} +/- {f['sc']:.3g}, FWHM = {f['F']:.4g} "
                      f"+/- {f['sF']:.3g}, A = {f['A']:.4g} +/- {f['sA']:.3g}, chi2/ndf = {f['chi2']/f['ndf']:.1f}")
                R(f"no-peak fit {key} {t} {w}", f["c"], f["sc"], "channel", f"FWHM {f['F']:.4g}, A {f['A']:.4g}, chi2/ndf {f['chi2']/f['ndf']:.1f}")
            except Exception as ex:
                print(f"  {key} {t} window {w}: fit failed ({ex})")


def sum_peak_check(S, pk):
    """Close-geometry (0 in) spectra: excess of the smoothed net spectrum at twice the photopeak channel over
    the mean of the levels 2 FWHM either side (a straight-line continuum, as for the photopeak)."""
    print("\n--- Sum-peak check, 0 in spectra (excess at 2C over the line through 2C +/- 2 FWHM) ---")
    for key, _, label, win in CONFIGS:
        if (key, "source") not in pk:
            continue
        p, s = pk[(key, "source")], S[key]["source"]
        sm = np.convolve(s["net"], np.ones(15) / 15, "same")
        c2, F = int(round(2 * p["c"])), p["F"]
        lo, hi = int(round(c2 - 2 * F)), int(round(c2 + 2 * F))
        im = lo + int(np.argmax(sm[lo:hi]))
        base = (sm[lo] + sm[hi]) / 2
        print(f"  {key:10s}: 2C = {c2}; smoothed level at 2C {sm[c2]:.1f}/ch, max {sm[im]:.1f}/ch at {im}; "
              f"line {base:.1f}/ch")
        R(f"sum-peak excess at 2C {key} 0 in", sm[c2] - base, None, "counts/channel",
          f"2C = {c2}; level {sm[c2]:.1f}, line {base:.1f}")


def tables(S, hv, pk, alt):
    pm = "$\\pm$"
    TAB_DIR.mkdir(exist_ok=True)
    # T1 HV scan
    rows = [f"{v:.0f} & {c:.2f} {pm} {s:.2f} & {(c - CAL_INT)/CAL_SLOPE:.3f} \\\\" for v, c, s in zip(hv["hv"], hv["c"], hv["sc"])]
    (TAB_DIR / "t1_hv.tex").write_text("\n".join(rows) + "\n")
    # T2 spectrum summary
    rows = []
    for key, _, label, _ in CONFIGS:
        b, s0, s2 = S[key]["bg"], S[key]["source"], S[key]["2inch"]
        dt = lambda s: 100 * (1 - s["live"] / s["real"])
        rows.append(f"{label} & {b['counts'].sum():.0f} {pm} {np.sqrt(b['counts'].sum()):.0f} & "
                    f"{s0['counts'].sum():.0f} {pm} {np.sqrt(s0['counts'].sum()):.0f} & {s0['real']:.0f} & {dt(s0):.1f} & "
                    f"{s2['counts'].sum():.0f} {pm} {np.sqrt(s2['counts'].sum()):.0f} & {s2['real']:.0f} & {dt(s2):.1f} \\\\")
    (TAB_DIR / "t2_spectra.tex").write_text("\n".join(rows) + "\n")
    # T3 photopeak results
    rows = []
    for key, _, label, win in CONFIGS:
        for t, tl in DIST:
            s = S[key][t]
            if win is None or (key, t) in NO_PEAK:
                rows.append(f"{label} & {tl} & -- & -- & -- & -- & -- & {s['tot']:.0f} {pm} {s['stot']:.0f} \\\\")
                continue
            p = pk[(key, t)]
            rows.append(f"{label} & {tl} & {p['c']:.2f} {pm} {p['sc']:.2f} & {p['F']:.2f} {pm} {p['sF']:.2f} & "
                        f"{p['A']:.0f} {pm} {p['sA']:.0f} & {100*p['R']:.2f} {pm} {100*p['sR']:.2f} & "
                        f"{p['chi2']/p['ndf']:.2f} & {s['tot']:.0f} {pm} {s['stot']:.0f} \\\\")
    (TAB_DIR / "t3_photopeaks.tex").write_text("\n".join(rows) + "\n")
    print(f"\nwrote tables to {TAB_DIR}")


def write_summary():
    lines, out = [], []
    for name, v, u, unit, src in RESULTS:
        us = "" if u is None else f" +/- {u:.4g}"
        lines.append(f"{name}: {v:.6g}{us} {unit}   [{src}]")
        out.append([name, v, "" if u is None else u, unit, src])
    (ROOT / "results_summary.txt").write_text("\n".join(lines) + "\n")
    with (ROOT / "results_summary.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["name", "value", "uncertainty", "unit", "source"])
        w.writerows(out)


if __name__ == "__main__":
    print("settings:", dict(K_ROI=K_ROI, K_ROI_ALT=K_ROI_ALT, N_SIDE=N_SIDE, FIT_V=FIT_V))
    S = load_spectra()
    print("\n--- Files ---")
    for key, stem, *_ in CONFIGS:
        for t in ("bg", "source", "2inch"):
            s = S[key][t]
            print(f"  {stem % t:20s} live {s['live']:5.0f} real {s['real']:5.0f} gross {s['counts'].sum():9.0f}  {s['date']}")
    hv = hv_scan()
    pk, alt = analyse(S)
    meas, pred, E_of = labeled_nai(S, pk)
    sum_peak_check(S, pk)
    net_peak_plots(S, pk)
    net_peak_overlays(S, pk)
    no_peak_checks(S)
    spectra_plots(S, "raw")
    spectra_plots(S, "net")
    bg_plot(S)
    tables(S, hv, pk, alt)
    write_summary()
