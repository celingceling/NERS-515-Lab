# Lab 4 report outline (my sections), for approval

Template: `report_prep/04_lab4_blank.tex`. I write the Introduction, Equipment and Procedure, Data, and the calculations in Data Analysis. My partner writes Theory, the Data Analysis discussion and Conclusions. The abstract is written last by whoever finishes last. Sources are Knoll 4th ed. (K, book page numbers), the lecture slides (L, slide numbers), and the Lab 4 manual (M). Slide numbers come from the pair markers in the handout PDFs, so please spot-check them.

## A. What the graders rewarded and penalized (annotated reports from a past student, including the same G-M lab)

| Area | What the grader wrote | What I do about it |
|---|---|---|
| Intro and abstract | "Don't include theory here. Focus on objective and methodology." Objective means what the lab sets out to understand. Methodology means what was measured. | Intro is one paragraph: objective, then the four measurements. No theory, no results. |
| Equipment and Procedure | Usually 5/5. Lost points for no manual reference (twice) and a wrong block diagram: "The HVPS should connect to the GM tube/pre-amp, not the amplifier." | Cite the manual in every procedure paragraph. Draw the block diagram from M §2.1.2 and check the HV path. |
| Data | 25/25 every time. One note: "Counts should always have uncertainty." Another: "Some narrative still needs to be included for the tables." | Write ±√N next to every raw count. Add commentary under every table. |
| Analysis | "The result and calculation should be shown before the discussion of that result." "Include a sample uncertainty calculation." "Include the equations here. It's more clear for the reader." "Reference back to the figures specifically." "Some discussion of the uncertainties used here would be beneficial." | Each subsection runs: equation, sample calculation, result, figure. Include a sample uncertainty calculation. Name each figure in the text. |
| Plateau and tail (same lab) | "As long as there's no tail in the spectrum. The tail is from multiple effects, not just the recovery time events." | See the tail note in section E. |
| Dead time (same lab) | "Use better wording here: 'the oscilloscope estimate is deemed more likely to be accurate'." "Discussion of the uncertainties used here would be beneficial." | Give an uncertainty on every τ. State which uncertainties went in. |
| Conclusion | "Result + Conclusion → Result + Conclusion." Put numbers in separate sentences. | Passed to my partner. |
| Style | Pick one voice ("we") and keep it. Cut wordiness. | Use "we" throughout. |

## B. Page budget (≤ 15 pages including the contents page, excluding the title page and appendices)

| Section | Pages | Owner |
|---|---|---|
| Contents | 1.0 | — |
| Abstract + Introduction | 0.6 | last / me |
| Theory | 2.5 | partner |
| Equipment and Procedure | 1.7 | me |
| Data | 3.0 | me |
| Analysis of Data | 5.0 (about 3.0 calculations, 2.0 discussion) | me + partner |
| Conclusions | 0.7 | partner |
| **Total** | **14.5** | |

That is tight. Sample calculations and the derived-values tables go in appendices.

## C. Outline

### 1 Introduction (me, 0.3 page)
- One paragraph. Objective: characterize a G-M tube and its counting system. Methodology: counting curve and pulse height vs HV; pulse height consistency; beta attenuation in Al; dead time by scope and two-source. Source: M §§1–5 (the purpose sentences of §§3, 4, 5). Draft is already in the template.

### 3 Equipment and Procedure (me, 1.7 pages)
**3.1 Equipment**
- Paragraph: list in Table 1; NIM serial-number sentence (same as Lab 3); sources used.
- **Table 1** (equipment): Purpose / Manufacturer / Model / Serial, the five Lab 3 rows only. As in Lab 3, the G-M tube, pre-amplifier, MCA and the sources (Th-232, Co-60, C-14, Cl-36) are named in the text, since we have no make/model/serial for them.
- **Figure 1** (block diagram): GM tube + pre-amp (HV supply into the pre-amp) → split to scope and amplifier → SCA → counter/timer; amplifier → MCA branch. Source: M §2.1.2.

**3.2 Experimental Procedure** (one paragraph each, each citing M)
1. Setup and counting curve (M §2): LLD found at 800 V with the source removed, so 0.1 V; Th-232; HV from 650 V to 910 V in 20 V steps, 30 s settle before each 3 s count; pulse height from the scope persistence display with a −2.625 mV baseline correction; stopped at 910 V after the rate jump (M's safety line).
2. Operating voltage (M §3): 840 V, on the high-voltage side of the smoothest plateau region.
3. Pulse height consistency (M §3): MCA from the amplifier; Co-60, C-14, Cl-36; 30 s real time; centroid and gross counts; channel to voltage with the MCA calibration from our Lab 2 report \cite{lab2} (see question 5).
4. Beta attenuation (M §4): SCA; Co-60 on tray 2; 5 s background; 8 Al absorbers 14.67 to 1540.52 mg/cm² with count times of 5 to 14 s; two Pb absorbers. **Deviation:** the manual asks for several thousand counts per second at tray 2; our unattenuated rate was only about 70 s⁻¹.
5. Scope dead time (M §5.1): Co-60 on the top shelf, Normal trigger, ∞ persist, 100 µs/div, cursors placed on the saved screenshots (Figure 3).
6. Two-source (M §5.2): Th-232 (A) and Cl-36 (B) on shelf 3, about 3 cm from the tube, side by side about 3 cm apart. A was never moved and only B was inserted and removed. Order: background, A, A+B, B. Three repeats of 10 s each.
- **Table 2** (settings found and used): V_op, noise LLD, SCA mode, count interval, start HV and step, baseline, MCA time, source and tray, absorber set, scope settings.

### 4 Data (me, 3.0 pages: raw values only, each table followed by commentary)
**4.1 Counting curve and pulse height**
- **Table 3**: HV, counts ± √N (3 s), pulse height ± reading uncertainty.
- Commentary: first counts at 670 V; counts level off from about 710 V; jump from 177 to 267 counts at 910 V and we stopped; pulse heights read as zero at 650 and 670 V even though 44 counts appeared at 670 V (the scope could not resolve them); the reading uncertainty grows with HV.

**4.2 Pulse height consistency**
- **Table 4**: source, centroid channel, gross counts ± √N, real time 30 s.
- Optional **Figure 2**: the three Maestro spectra overlaid with centroid markers (needs the .Chn files).
- Commentary: C-14 had the lowest counts, Cl-36 the highest; centroid order is Cl-36 < Co-60 < C-14.

**4.3 Beta attenuation**
- **Table 5**: material, mass thickness, counts ± √N, time (background row first).
- Commentary: steep drop over the first two points, then a flat stretch; Pb points; no unattenuated source measurement; count times lengthened with thickness as M asks.

**4.4 Dead time**
- **Figure 3(a)(b)**: the two scope screenshots with the cursors on them. (a) cursors at −2 µs and 358 µs, ΔX = 360 µs: the dead time, from the initial pulse to where later pulses first appear. (b) cursors at 358 µs and 838 µs, ΔX = 480 µs: the interval from the end of the dead time to where pulses reach full height. Files are in `report_prep/figures/`.
- **Table 6**: cursor readings (X1, X2, ΔX) for both screenshots, with the reading uncertainty (cursor step is 2 µs).
- **Table 7**: two-source counts per run (background, A, B, A+B, T = 10 s).
- Commentary: geometry and the no-move precaution; the Th-232-only counts ranged from 722 to 1174 in 10 s against about ±30 expected from Poisson, so something moved or drifted despite the care.

### 5 Analysis of Data (me: calculations; partner: discussion after each subsection)
Each subsection: equation with source, sample calculation, result table or figure, then `% PARTNER:`.

| Subsection | Calculations and results | Sources | Figure / table |
|---|---|---|---|
| 5.1 Pulse height vs HV | Weighted line fit over a stated range; slope, x-intercept; residuals | K p. 209; L 58–59 | Fig. 4, Table 8 |
| 5.2 Counting curve and plateau | r = N/t, σ_r = √N/t; plateau fit over a stated window with sensitivity to window; slope in s⁻¹V⁻¹ and in %/100 V; knee, starting voltage, 910 V; check that rates stay below a few hundred s⁻¹ | K Eq. 3.38–3.40; K pp. 214–215, Fig. 7.5; L 62; L (Ch4+10) 7–8 | Fig. 5, Table 9 |
| 5.3 Pulse height consistency | V(n) calibration; rate = N/30 s; amplitude vs rate | K Eq. 3.38–3.40; M §3 | Fig. 6, Table 10 |
| 5.4 Beta attenuation | Net rate and σ_r; ln r with σ_y = σ_r/r and σ_x = 10%; n from the fit (all points) and from the first two points; expected n and endpoint energy from Fig. 2.16 | K Eq. 3.52–3.53, Eq. 3.37, Eq. 2.14, Fig. 2.16, p. 45; M §4 | Fig. 7, Table 11 |
| 5.5 Dead time | Scope dead time 360 µs; recovery time stated both as the 480 µs interval and as 840 µs from the initial pulse (Knoll Fig. 7.4, see question 3); two-source τ per run from Eq. 4.32 with Z; σ_τ by Eq. 3.37; mean, spread and standard error of the three; m₁₂τ vs 20%; predicted vs observed m₁₂ for both models; 1/τ and 1/(eτ) limits | K Eq. 4.24, 4.27, 4.30–4.32, pp. 124–125; L 55–62; L (Ch3) 25–26 | Fig. 8, Fig. 9, Table 12 |

### Appendices (not counted)
- A: sample calculations (σ_r, ln r and σ_y, Eq. 4.32 with its σ_τ).
- B: derived-values tables (rates with σ for all counting-curve points, beta net rates).

## D. Equation handoff list for my partner's Theory

| Topic | Source |
|---|---|
| Cylindrical field E(r) = V/(r ln(b/a)), why a thin wire | K Eq. 6.3; L (Ch5-7) 27–28 |
| Avalanche, UV photons, criticality N₀P ≷ 1, termination by space charge | K ch. 6–7; L 54–57 |
| Quenching (external, internal), multiple pulsing | K ch. 7; L 59 |
| Pulse amplitude vs HV; all pulses the same size | K p. 209; L 58 |
| Counting curve, knee, plateau, slope causes, 2–3 %/100 V | K pp. 214–215, Fig. 7.5; L 62; L (Ch4+10) 7–8 |
| Dead, resolving, recovery time | K p. 213, Fig. 7.4; L 63 |
| σ_N = √N, net-rate σ_r | K Eq. 3.38–3.40, 3.52–3.53; L (Ch3) 29–30, 33–36 |
| Error propagation | K Eq. 3.37; L (Ch3) 25–26 |
| Beta absorption n, Fig. 2.16, electron range | K Eq. 2.14, pp. 44–45 |
| Dead-time models | K Eq. 4.24, 4.27–4.29; L (Ch3) 55–58 |
| Two-source and decaying-source methods | K Eq. 4.30–4.36, pp. 124–125; L (Ch3) 59–62 |
| G-M gamma response and efficiency | K p. 118, p. 218, Fig. 7.8; L 64 |
| Pre-lab Q1–5 (the old reports lost points when these were missing from Theory) | reading-notes doc, re-checked against the sources above |

## E. Concerns and questions for me

Answered by you: shelf and geometry; 30 s real-time MCA; HV step 20 V from 650 to 910 V with a 30 s settle; no equipment details; the first two-source data set is not mentioned; channel calibration comes from Lab 2.

1. **Line fitting is not in the three sources.** Knoll p. 92 gives the weighting rule (weight each point inversely as the square of its error) and Eq. 3.37 gives propagation, but neither Knoll nor the slides cover least-squares line fitting or the "effective variance" with x errors. Options: (a) weighted straight-line fit, justified by the p. 92 rule, performed numerically, with no outside citation; (b) report two-point slopes with Eq. 3.37 errors as the sourced numbers and show the fit only as a visual. I suggest both, with (b) as the cross-check.
2. **The beta tail.** The flat stretch is from 177 mg/cm² onward at about 10–13 s⁻¹, then 5–6 s⁻¹. The sources give a basis to say it is not beta (K p. 44 range rule) and that a G-M tube sees gammas through its wall (K p. 218). They do not tell us how to subtract it. Default: fit all points (as M asks) and also give n from the first two points, labeled. Do not subtract unless you say so (or the TA does).
3. **Recovery time definition.** In Knoll Fig. 7.4 (p. 213) both the dead time and the recovery time are measured from the initial pulse. Our screenshots give 360 µs from the initial pulse to where later pulses appear, and 480 µs from there to full height, so the Knoll recovery time is about 840 µs (−2 µs to 838 µs). Which do you want to report as "recovery time"? I suggest stating both with their definitions: 480 µs as the interval after the dead time, 840 µs as the recovery time in Fig. 7.4's sense. Also, your notebook and the plot script use 482 µs but the screenshot reads 480.000 µs.
4. **Scope reading uncertainty.** The cursors move in 2 µs steps, but the start of the later pulses and the return to full height are gradual edges, so the real uncertainty is larger. What should we use (for example half the span over which the edge is ambiguous), and how did you judge the edges?
5. **Calibration sign.** Lab 2 gives channel = 765.8 V + 27.6 (R² = 0.9999). Inverting it gives V = (n − 27.6)/765.8, that is V(n) = −36.0 mV + 1.306 mV × n. The notebook and your message have +35.98 mV. With the minus sign the amplitudes are Co-60 3.76 V, C-14 4.37 V, Cl-36 2.50 V (the plus sign gives 3.83, 4.44, 2.57). Which is right? Also, the Lab 2 fit only applies if the same MCA and ADC settings were used.
6. **Source rate on tray 2.** M asks for several thousand s⁻¹; ours was about 70 s⁻¹. State this as a deviation?
7. **Pb absorbers.** Why were they measured, and should they appear in the report?
8. **Pulse height uncertainty.** How is the "Uncertainty mV" column defined (half-width of the persistence band?), and is the −2.625 mV baseline already applied to the table values? Why do 650 and 670 V read zero when counts appeared at 670 V?
9. **MCA spectra files** (.Chn or screenshots) for an overlay figure. The previous grader mentioned the "tail in the spectrum".
10. **Block diagram:** reuse the Lab 3 figure with changes, or draw a new one (TikZ)?
11. **Plateau slope reference rate** (rate at start of plateau, plateau mean?): Knoll p. 215 only says "percent per 100 V".
12. **Counts ± √N in raw tables:** OK to include (grader asked for it)?
