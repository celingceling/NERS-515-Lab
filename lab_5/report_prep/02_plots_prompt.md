# Prompt 2: Lab 5 figures (paste into Claude Code, run from `NERS-515-Lab/lab_5/`)

Write `lab_5_plots.py` in `NERS-515-Lab/lab_5/` that makes the figures and numbers for my NERS 515 Lab 5 report (Proportional Counter). Reuse the style of `../lab_4/lab_4_plots.py` (copy its style constants, colors, `weighted_line_fit` and the PNG/PDF saving helper) so the Lab 5 figures look like the final Lab 4 ones.

## Rules

1. **Keep every figure simple.** Look at the Lab 4 figures I kept (`../lab_4/figures/B_counting_curve.png`, `D_beta_attenuation_ln.png`): one panel, the data, at most one fit or one reference line, a short legend. The Lab 4 plot prompt asked for much more (extra reference lines, alternate fits, residual panels, text notes, shading for every region) and I removed it. So: no text annotations on the plot, no titles (the caption does that), no second panels, no alternate fits, at most 3 legend entries.
2. **Error bars on every data point, always.** Counts: σ_N = √N; rates σ_r = √N/t (Knoll Eq. 3.40, p. 88). Derived quantities: propagate with Knoll Eq. 3.37 (p. 86). MCA centroids: σ_c = σ/√A with σ = FWHM/2.35 and A the peak area (Knoll p. 728). FWHM was not recorded. We state σ_c < 1 channel (even an FWHM of several hundred channels gives that with A ≈ 6×10⁵), so draw centroid error bars at ±1 channel as an upper bound, make `SIGMA_CENTROID = 1.0` a setting, and note in the caption suggestion that the bars are smaller than the markers. Never plot without error bars.
3. Formulas only from Knoll 4th ed. (`../../Knoll_Radiation_Detection_Fourth.pdf`), the slides (`../../lectures/`) and the Lab 5 manual (`../../Lab 5/`). Put the source in a comment at each formula. If something is not in those sources, ask me.
4. Do not change the data files. If something looks wrong, tell me.
5. Save each figure as PNG (dpi 200) and PDF in `figures/`, sized to be readable at half page width (fonts ≥ 9 pt in print), colorblind-safe, distinct markers, legend off the data.
6. Print every number the report quotes and save them to `results_summary.txt` and `results_summary.csv` (name, value, uncertainty, unit, source). Write LaTeX tables (booktabs) to `tables/`: raw-data tables for the Data section (only what was measured, counts with ±√N) and one derived table per analysis subsection.
7. Judgment calls (fit range, which points to exclude, count times not in the files) are named settings at the top of the script; print what each is set to and ask me before locking them in.

## Data (`data/`)

- `Lab 5 - 2. Shaping time.csv`: shaping time (µs), centroid channel, gross peak area. The 10 µs area is blank and isn't needed for the plot. For σ_c at 10 µs, extrapolate the area from the shorter shaping times (state the method, e.g. a straight line through the 3 and 6 µs areas; check: about 7.7×10⁵) and label it as estimated in the table and printout.
- `Lab 5 - 2. Counting Curve - Alpha.csv`: Am-241, LLD channel 1738. Columns: voltage, gross counts above LLD, peak centroid, rate. Rate column = counts/30 s, so `T_ALPHA = 30.0`.
- `Lab 5 - 2. Counting Curve - Beta.csv`: Cl-36, LLD channel 307, 30 s per point (`T_BETA = 30.0`).
- `Lab 5 - 3. Counting Efficiency.csv`: Cl-36, 1,428,191 counts in 60 s; "count rate (uC)" 0.6433 is the rate divided by 3.7×10⁴; "Original" 1.032 µCi; date Aug 1 2026. Messy layout, parse by hand.
- `Lab 5 - 4. Gamma Response, .csv`: LLD channel 229, voltage vs gross counts, 30 s per point (`T_GAMMA = 30.0`).
- No .SPE spectra were saved, so there is no spectrum figure (see F4).

## Figures (in report order)

**F1. Peak centroid vs shaping time** (manual 2.2.2). Points only, x = shaping time (µs, log axis is fine), y = centroid channel, error bars once I give the centroid uncertainty. One vertical dashed line at the chosen shaping time, 3 µs (where the centroid levels off), is allowed; nothing else. Print the ballistic deficit relative to 10 µs, BD = (C₁₀ − C)/C₁₀ × 100 % (Knoll p. 649, Fig. 17.22 for the definition), with propagated uncertainty, for every shaping time. Checks: 28.8 % (0.5 µs), 16.4 % (1), 8.5 % (2), 2.2 % (3), 1.6 % (6).

**F2. Alpha counting curve** (2.3.1). Count rate vs voltage with √N/t error bars. Rates span 0.77 to 22,322 s⁻¹, so try a log y axis and show me both linear and log versions; I'll pick one. We raised the voltage until the plateau appeared; at 1050 V the count dropped to 9,537 s⁻¹ and stayed there on repeated measurements. Plot 1050 V with a hollow marker, exclude it from the plateau, and set `PLATEAU_START = 1000` V (the last point before the drop). At most one vertical dashed line at 1000 V. Caption info only: LLD channel 1738, 30 s per point.

**F3. Alpha pulse amplitude vs voltage, log-linear** (2.3.1, compared in the text with Knoll Fig. 6.11, p. 171). y = peak centroid on a log axis. The centroids from 500 to 800 V sit at about 1750-1880, right at the LLD (1738), so they are probably not the alpha peak position. Make `AMPLITUDE_POINTS` a setting: default 900 and 1000 V as filled markers (peak clearly above the LLD), 1050 V hollow (the drop), and the 500-850 V points left out or shown faint-hollow (ask me which). No fit line with only two good points; print the two-point slope Δln(centroid)/ΔV ± error (Eq. 3.37) for 900-1000 V and for 1000-1050 V so the report can compare them with Knoll Eq. 6.10 (ln M roughly linear in V, pp. 170-171). No Fig. 6.11 overlay.

**F4. Calibrated alpha spectrum: skipped** (no .SPE saved). Print the one-point calibration factor from the 3 µs shaping-time run: k = 5.486 MeV / 2367.29 = 2.317 keV/channel (Knoll Table 1.3, p. 8, main Am-241 group), through the origin, with σ_k from σ_c ≤ 1 channel (Eq. 3.37). Valid only at 800 V, gain 50 (coarse 100 × fine 0.5; fine-dial reading possibly 6.00, see the report prompt), 3 µs shaping.

**F5. Beta and gamma counting curves** (2.3.2 and 4). One figure, two series (Cl-36 beta, LLD 307; gamma, LLD 229) with distinct markers, rate vs voltage, √N/t error bars. Nothing else on it. If the two curves are hard to read together, make two separate figures (F5, F6) and tell me.

**Efficiency (3): table only, no figure.** Compute rate r = N/t ± √N/t; marked activity in Bq (1 µCi = 3.7×10⁴ Bq, Knoll p. 2: 1 Ci = 3.7×10¹⁰ s⁻¹); decay correction A(t) = A₀ e^(−λt), λ = ln2/T½, T½(Cl-36) = 3.08×10⁵ y (Knoll Eq. 1.1 p. 2, Table 1.1 p. 4); ε_abs = r/A(t); ε_int = ε_abs × 4π/Ω with Ω = 2π (Knoll pp. 118-119, p. 166). Run settings: Cl-36 (marked 1.032 µCi on Aug 1 2026), 1500 V (chosen from the beta plateau), LLD 307 and the same gain as the beta curve, 60 s. Propagate counting uncertainty (Eq. 3.37); the marked activity has no stated uncertainty, so ask me. Check: ε_abs ≈ 0.623, above the 2π maximum of 0.5; ε_int ≈ 1.25. Flag this in the printout. Also print the beta-curve rates at 1500 and 1550 V next to the efficiency-run rate for comparison.

## Flag to me (do not work around)

- Alpha centroids at the LLD for 500-850 V; the 1050 V drop.
- Gamma source (Co-60 or Cs-137) for the legend.
- The efficiency-run rate is about 7 % above the beta-curve rate at the same 1500 V and LLD.
- Efficiency above the 2π limit.

## Output

Run it, show me each figure, the printed summary, and a list of assumptions and open questions. Short docstring per plot function: what it plots and which equation it uses.
