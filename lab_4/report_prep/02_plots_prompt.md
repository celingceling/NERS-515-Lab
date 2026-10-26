# Prompt 2: Lab 4 plots (paste into Claude Code, run from `NERS-515-Lab/lab_4/`)

Modify the existing `lab_4_plots.py` in this folder (do not rewrite it from scratch; keep its style constants, `weighted_line_fit`, dead-time model functions and `tau_two_source`). Make it produce every plot and number needed for my NERS 515 Lab 4 (Geiger-Müller counting) report.

## Rules

1. Sources for every formula and error calculation: Knoll 4th ed. (`../../Knoll_Radiation_Detection_Fourth.pdf`), the lecture slides (`../../lectures/`), and the Lab 4 manual (`../../Lab 4/`). Nothing else. No solutions manual, no web, no formulas from memory. Put the source in a code comment at each formula (e.g. `# Knoll Eq. 3.53`). If a formula or convention is not in those three sources, or two disagree, stop and ask me.
2. Do not change the data. If a CSV looks wrong, tell me.
3. Print a summary of every number to the terminal and also save them to `results_summary.txt` and `results_summary.csv` (one row per quantity: name, value, uncertainty, unit, source/equation). My report will quote these.
4. Save each figure as PNG (dpi 200) and PDF to `figures/`. Figures must be readable at half page width in a LaTeX report: font ≥ 9 pt in print, no title baked in if a caption does the job (keep a short title anyway but make it optional with a `SHOW_TITLES` flag), colorblind-safe, distinct marker shapes as well as colors, legend not covering data.
5. When something is a judgment call (fit range, how to treat a tail, which plateau window), make it a named setting at the top of the file, print what it is set to, and ask me before locking it in.

## Data files (in `data/`)

- `beta_attenuation.csv` : header `Material, attenuation mu/rho (mg/cm^2), Counts, Time Interval, count rate`. The thickness column is mass thickness in mg/cm². The row with material `None` (0 mg/cm², 5 counts, 5 s) is the background. Al rows are the data. A blank row separates the Pb rows (4534 and 7302 mg/cm²), which are not part of the Al fit. Read with `keep_default_na=False` so "None" is not NaN. The script's current filename `beta_attenuation_data.csv` is stale: fix it.
- `counting_curve.csv` : `HV, Counts, Pre-amp Pulse Height mV, Uncertainty mV`. Counting interval was 3 s per point (from my notebook; there is no time column, so make it a constant `COUNT_TIME = 3.0`). The rate jump at 910 V is the start of continuous discharge; we stopped there.
- `two_source_dead_time.csv` : wide format, one row per run, columns Background, Th-232, Cl-36, Both, Dead Time (µs); T = 10 s per measurement (`T_TWO_SRC = 10.0`). The script's current reader expects an old long-format file with 8 s: replace it. The CSV's own "Dead Time" column is Eq. 4.32 per run; your calculation must reproduce it (298, 612, 971 µs), and you should print the check.
- Scope (from the two screenshots in `../report_prep/figures/`): cursors at −2 µs and 358 µs give the dead time, 360 µs; cursors at 358 µs and 838 µs give 480 µs, the interval from the end of the dead time to full pulse height. In Knoll Fig. 7.4 the recovery time is measured from the initial pulse, so it would be 838 − (−2) = 840 µs. The existing script has `TAU_RECOVERY_SCOPE = 482e-6`, which is wrong (the screenshot reads 480.000 µs). Define `TAU_DEAD_SCOPE = 360e-6`, `T_INTERVAL_SCOPE = 480e-6`, `TAU_RECOVERY_SCOPE = 840e-6`, mark all three in the dead-time figures, and ask me which one to call the recovery time.
- Pulse height consistency (from my notebook, not a CSV yet; put it in a small `pulse_height_consistency.csv` and tell me): sources Co-60, C-14, Cl-36; 30 s **real time** spectra; MCA centroid channel / gross counts: Co-60 2906 / 4419, C-14 3374 / 1280, Cl-36 1939 / 13986. Calibration channel → voltage: from my Lab 2 report, channel = 765.8 × V + 27.6 (R² = 0.9999), so V = (n − 27.6)/765.8. My notebook instead has V(n) = 35.98 mV + 1.31 mV × n, which differs in the sign of the intercept. Compute the three amplitudes both ways (minus sign: about 3.76, 4.37, 2.50 V; plus sign: about 3.84, 4.46, 2.58 V), print both, and ask me which to use before making the plots. No uncertainty was recorded for the centroid or the calibration, so ask me before inventing one; until then show √N on the counts only. Rate = counts / 30 s.
- Two-source geometry (for captions and notes): 3rd shelf, about 3 cm from the tube, sources side by side about 3 cm apart, source A not moved between measurements, only B inserted and removed.

## Plots to produce (in report order)

**A. Pulse height vs high voltage.** Points with y error bars (the `Uncertainty mV` column) and a legend entry for the scope reading uncertainty. Mark the starting voltage and the operating voltage 840 V with vertical references. Points at 650 and 670 V are zeros because no pulse could be read; draw them as hollow markers or leave them out of any fit, and say which. Also give a straight-line fit of amplitude vs HV over an explicit range (named setting), weighted by the error bars, print slope ± error and the x-intercept ± error, and overlay it. Knoll p. 209 states amplitude is proportional to overvoltage: put a text note or reference marker for the Knoll starting voltage definition so we can compare the intercept with the first-count voltage. The data look curved, so also print the residuals (or a small residual panel beneath) so the report can say honestly how linear it is.

**B. Counting curve.**
- rate = counts/3 s, y error bars σ_r = √N/t (Knoll Eq. 3.38-3.40; σ_N = √N).
- Shade/mark: starting voltage (first counts at 670 V), knee, plateau window, operating voltage 840 V (vertical line), the 910 V runaway point (distinct marker with note "continuous discharge onset; not in plateau").
- Plateau fit: weighted straight line (weights 1/σ²) over a named window `PLATEAU = (710, 890)` (and print results for alternates (730, 890) and (770, 890) so I can see the sensitivity). Report slope ± error in counts s⁻¹ V⁻¹ and percent per 100 V. Percent per 100 V requires a reference rate: ask me what Knoll/the slides use, and print both the fit value at the plateau start and the plateau mean until I tell you. Overlay the fit line over the window, and print χ²/ndf.
- Optional second panel or twin axis: pulse height vs HV on the same HV axis, so the plateau and the amplitude growth can be compared (Knoll Fig. 7.5 shows the integral/differential relationship).

**C. Pulse height consistency.** Bar or point plot of the amplitude (V, from the calibrated centroid) for each source, with the gross count rate (counts/30 s, √N/t error) shown as a second panel or labeled on the points. Also a scatter of amplitude vs count rate with one labeled point per source. The question the manual asks is the relationship between count rate and observed amplitude, so show it directly. Do not add a trend line through three points.

**D. Beta attenuation.**
- y = ln(net rate), net rate = G/t_g − B/t_b, σ_r = √(G/t_g² + B/t_b²) (Knoll Eq. 3.52-3.53), y error σ_r / r, x error = 10 % of mass thickness (manual).
- Weighted fit with the existing effective-variance fit (derived from Knoll Eq. 3.37). Keep the all-points fit and the fit without the first point that the script already has. Add the sub-fits I need to discuss the tail (e.g. points 2-6) as named settings, but flag how many points and degrees of freedom each has. Print n in cm²/g (convert from mg/cm²), I₀, χ²/ndf.
- Add the first-two-points slope n₁₂ = ln(r₁/r₂)/(t₂ − t₁) with its propagated uncertainty (Eq. 3.37), as a separate, clearly-labelled estimate: those two points carry the beta component, and the rest looks like a penetrating tail.
- Reference lines/markers: background rate (dashed, already there); a horizontal line at the plateau level of the tail (named setting, with the points averaged shown); the expected-n line: read the Co-60 curve in Knoll Fig. 2.16 (n vs endpoint energy, log-log, Al) and draw a line with slope −n_expected through the first point, so the data can be compared with the expected attenuation visually. Knoll Fig. 2.16 (book p. 45) plots E (MeV) on the vertical axis against n (cm²/g) on the horizontal axis, both logarithmic, with separate lines for E_m, E_av and E′ and the isotopes labeled; Co-60 sits near the middle of the n axis, so read it carefully. Ask me to confirm the n_expected you read off the figure (give the endpoint energy used and how you read it).
- Mark each point's count time and counts in a table next to or beneath the figure (rates, net rates, σ, ln r, σ_y, σ_x) for the Data Analysis section.
- Endpoint energy estimate: invert the Fig. 2.16 relationship for the measured n (read the graph, or use its straight-line form on log-log axes: say which); give the result with an uncertainty propagated from σ_n. Ask me if the figure's labels or axes are unclear.
- A second figure with the same data on a log-y axis plotted as rate (not ln) is optional and useful if the ln plot looks cluttered.

**E. Dead time.**
- Two-source: use the Eq. 4.32 function for each run with rates m = N/10 s and the pooled sums. Propagate Poisson uncertainties (σ_N = √N, with N=0..5 for background, use √N but warn if N < 10 and tell me how the textbook says to handle small counts) through Eq. 4.32 numerically with Eq. 3.37; print σ_τ per run. (My own check gave about ±570, ±730 and ±630 µs, i.e. comparable to τ itself; confirm.) Also print the mean and standard deviation of the three τ and the standard error of the mean using the sample-statistics formulas in the lecture/Knoll, and print Z and the fractional dead time m₁₂τ for each run against Knoll's recommended ≥ 20 %.
- Figure E1: per-run τ with error bars, a band for the mean ± SEM, horizontal lines for the scope dead time (360 µs) and recovery time (482 µs). This is the main dead-time comparison.
- Figure E2 (existing "predicted vs observed combined rate"): rebuild with the new data, with the observed m₁₂ ± σ as a band and the nonparalyzable/paralyzable predictions vs assumed τ; mark the scope τ and recovery time. Keep the existing behavior where the paralyzable curve stops where it has no solution, and replace the hardcoded axis limits and text positions (y from 700 to 1000, label height 985) with data-driven ones, because the new rates are different (m₁₂ is about 116-159 s⁻¹, not about 800).
- Figure E3 (existing bar chart): keep, per run or pooled, but make it clear which τ is used.
- Optional: a plot of m vs n for both models with τ = 360 µs and the three measured single-source rates marked, with the 1/τ saturation line (Eq. 4.24) and the 1/(eτ) maximum of the paralyzable curve (Eq. 4.27), to show how far below saturation we are.
- Scope dead time and recovery time: the two screenshots are already in `../report_prep/figures/` with the cursors on them (the manual's markers). Do not redraw them. Just use the numbers above in the dead-time figures.

## Tables to generate as LaTeX (`tables/*.tex`, booktabs, each with a caption and label)

1. Counting curve raw data (HV, counts, Δt, pulse height ± σ) for the Data section.
2. Pulse height consistency raw data (source, centroid channel, gross counts, time).
3. Beta attenuation raw data (material, mass thickness, counts, time).
4. Two-source raw data (run, background, Th-232, Cl-36, both, T).
5. For Data Analysis: counting rates with σ; net beta rates with σ_r, ln r, σ_y, σ_x; per-run dead-time results (m₁, m₂, m₁₂, m_b, Z, τ, σ_τ, m₁₂τ).

Raw-data tables contain only what was measured. Anything computed goes in the Data Analysis tables.

## Things to flag to me (do not silently work around)

- Beta data are not a single exponential (rates ~67, 15.6, 12.8, 13, 10.8, 10.6, 5.0, 6.1 s⁻¹): two steep points, then a slow tail from about 177 mg/cm² on. Knoll p. 45 calls the beta curve only approximately exponential, and p. 218 gives the gamma response of a G-M tube through its wall. Do not subtract a tail level unless I say so; fit all points (what the manual asks) and report the first-two-point slope as a separate, labeled estimate. Fitting all eight points gives a very large χ²/ndf (about 203/6 in my check, n ≈ 2.0 cm²/g); dropping the first gives about 0.66 cm²/g, χ²/ndf about 6/5; the first two points alone give about 28 cm²/g. Tell me if your numbers differ.
- Two-source τ values are very spread and the method has low fractional dead time here.
- Plateau slope is sensitive to the window; show the sensitivity.
- Pulse height decreases as the count rate rises across the three sources.
- Anything where the manual and Knoll differ.

## Output

Run it, show me the figures, the printed summary, and a list of every assumption and open question. Keep the code readable with a short docstring at each plot function saying what it plots and which equation it uses.
