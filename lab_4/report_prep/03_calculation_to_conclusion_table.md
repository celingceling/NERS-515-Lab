# Lab 4: what each calculation or value is used to conclude

"Check value" is from a quick pass I ran on the updated CSVs. The plotting script is the authority; use these only to catch mistakes. Sources: K = Knoll 4th ed., L = lecture slides, M = lab manual. "Req." is the Lab 4 manual's report requirement (Section 6).

| # | Calculation / value | How (source) | Check value | What it is used to conclude (Req.) | Goes in |
|---|---|---|---|---|---|
| 1 | Count rate vs HV, r = N/3 s, σ_r = √N/t | K Eq. 3.38-3.40 | 0 at 650 V; 14.7 s⁻¹ at 670; about 51 at 710; about 54-62 at 730-890; 89 at 910 | Counting curve shape: starting voltage, knee, plateau, runaway (Req. Counting Curve) | Data Analysis |
| 2 | Starting voltage, knee, end of plateau | read from the curve; K Fig. 7.5, K pp. 214-215 | first counts 670 V; knee near 710 V; plateau to 890 V; discharge onset at 910 V | Explains each feature of the curve and where it is safe to operate | Data Analysis |
| 3 | Plateau slope (counts s⁻¹ V⁻¹ and % per 100 V), weighted line fit | K Eq. 3.37, weights 1/σ²; % reference rate to confirm with K/L | 710-890 V: 0.050 ± 0.024 s⁻¹V⁻¹ (about 8.7 %/100 V of the mean rate), χ²/ndf 1.3; 730-890 V: 0.040 ± 0.028 (about 6.9 %); 770-890 V: 0.029 ± 0.042 (about 5 %) | Why the plateau is not flat, and whether it is consistent with 0 (Req. Counting Curve: measure the slope, explain it). With ±σ this large the slope is only marginally nonzero | Data Analysis |
| 4 | Operating voltage 840 V | M §3: higher-voltage side of the smoothest plateau region | 830 V and 850 V rates are 61.0 and 61.7 s⁻¹ | Justifies using 840 V for Sections 3-5 | Procedure (settings table), Data Analysis |
| 5 | Noise LLD = 0.1 V | M §2.2.1 (found at 800 V, source removed) | notebook | Shows counts are not noise | Procedure (settings table) |
| 6 | Pulse height vs HV with error bars; linear fit and x-intercept | K p. 209 (amplitude ∝ overvoltage), K Fig. 7.3 (shaping); weighted line fit | linear fit 690-890 V about 1.7 mV/V, x-intercept about 700 V; data are curved (quadratic term significant) | Explains the shape: amplitude grows with overvoltage, independent of primary ionization (Req. Pulse Height vs HV). The curvature and the intercept compared with the 650-670 V first-count voltage are the points to discuss honestly | Data Analysis |
| 7 | Centroid channel → voltage, V = (n − 27.6)/765.8 from Lab 2 (channel = 765.8 V + 27.6); the notebook has +35.98 mV + 1.31 mV × n, opposite intercept sign, to be resolved | Co-60 3.76 V; C-14 4.37 V; Cl-36 2.50 V (with the notebook's sign: 3.84, 4.46, 2.58 V) | Amplitude for each source (Req. Pulse Height Consistency) | Data (raw centroids), Data Analysis (volts) |
| 8 | Count rate per source = N/30 s, σ = √N/t | K Eq. 3.38-3.40 | Co-60 147 s⁻¹; C-14 43 s⁻¹; Cl-36 466 s⁻¹ (30 s real time) | Relationship between rate and amplitude: amplitude does not follow the source type, it falls as rate rises (466 → 2.50 V, 147 → 3.76 V, 43 → 4.37 V). The partner explains this with recovery/dead time (K p. 213, Fig. 7.4) | Data Analysis |
| 9 | Net beta rate r = G/t_g − B/t_b and σ_r | K Eq. 3.52-3.53 | 67.0, 15.6, 12.8, 13.0, 10.8, 10.6, 5.0, 6.1 s⁻¹ (σ_r/r 5-16 %); background 1 s⁻¹ | Input to every beta result below | Data Analysis |
| 10 | ln(r) vs mass thickness with x error 10 % and y error σ_r/r | K Eq. 2.14, K Eq. 3.37 (effective variance); M (10 % x error) | n/a | The requested ln plot (Req. Beta Attenuation) | Data Analysis |
| 11 | Absorption coefficient n from the fit, in cm²/g | slope of ln r vs t (K Eq. 2.14, p. 45) | all 8 pts: 2.04 ± 0.13, χ²/ndf about 203/6; without first point: 0.66 ± 0.11, χ²/ndf 6.2/5; pts 2-6: 0.44 ± 0.18, χ²/ndf 1.3/3 | Measured n and whether one exponential describes the data (Req. Beta Attenuation: measure n and compare with expected). The poor χ² for all points is itself a result | Data Analysis |
| 12 | n from the first two points | ln(r₁/r₂)/(t₂ − t₁), error by K Eq. 3.37 | about 28 cm²/g | The beta component sits in the first points; gives a beta-dominated n to compare with Fig. 2.16 | Data Analysis |
| 13 | Penetrating tail level | mean net rate of the flat points (named range in the script) | about 10.6-13 s⁻¹ for 177-843 mg/cm², then 5-6 s⁻¹ at 1279 and 1541 mg/cm² | Shows a non-beta (gamma/bremsstrahlung) component (K pp. 45-46, 218); explains why n from all points is too small | Data Analysis |
| 14 | Expected n for Co-60 | read from K Fig. 2.16 | read from figure; confirm with me | Comparison "how does this compare with the expected value" (Req. Beta Attenuation) | Data Analysis |
| 15 | Endpoint energy estimate from measured n | invert K Fig. 2.16 (log-log relation); propagate σ_n | from the figure | Req. Beta Attenuation: estimate endpoint energy; compare with the source's endpoint energy in Fig. 2.16 | Data Analysis |
| 16 | Scope dead time and recovery time from the cursor screenshots | K Fig. 7.4, p. 213; M §5.1 | dead time 360 µs (−2 to 358 µs); 480 µs from 358 to 838 µs; recovery time from the initial pulse about 840 µs (definition to confirm) | How the recovery time was measured, using markers on the image (Req. Dead Time); the first of the two independent measurements | Data (screenshot, readings), Data Analysis (marked figure) |
| 17 | Two-source τ per run | K Eq. 4.30-4.32, L slide 61 (nonparalyzable) | 298, 612, 971 µs (Z = 0.09, 0.14, 0.26) | Second independent measurement of dead time; what model it assumes (nonparalyzable) (Req. Dead Time) | Data Analysis |
| 18 | σ_τ per run | K Eq. 3.37 with σ_N = √N on all four counts | about ±570, ±730, ±630 µs | The two-source result has no real precision here; matters for "which do you trust more" | Data Analysis |
| 19 | Mean, standard deviation and SEM of the three τ | sample statistics (K ch. 3 / L Ch. 3) | mean 627 µs, s = 337 µs, SEM = 195 µs; pooled counts give 605 µs | One number with an uncertainty to compare with the scope's 360 µs. 360 µs lies within about 1.4 SEM of the mean, so the two are consistent but the two-source value is imprecise | Data Analysis |
| 20 | Fractional dead time m₁₂τ | K pp. 124-125 (recommends ≥ 20 %, confirm page) | about 5 %, 7 %, 14 % | Explains why the two-source result is noisy and what to change next time (higher rates, more counting time) | Data Analysis |
| 21 | Predicted vs observed m₁₂ at the scope τ (both models) | K Eq. 4.24, 4.27, 4.30 | observed 116-159 s⁻¹ band vs predictions | Which dead-time model fits and whether the scope τ reproduces the combined rate | Data Analysis |
| 22 | 1/τ and 1/(eτ) limits | K Eq. 4.24, 4.27 | 1/360 µs = 2780 s⁻¹ | Shows we operate far below saturation (rates ≤ 160 s⁻¹), so models are hard to tell apart | Data Analysis |

## Requirement to figure map (for the Data / Data Analysis split)

| Manual requirement (Section 6) | Raw data table (Data) | Figure / calculation (Data Analysis) |
|---|---|---|
| Pulse height vs HV: plot and explain | counting_curve.csv columns HV, pulse height, uncertainty | Plot A, fit, residuals (#6) |
| Counting curve: plot, plateau slope, why not flat | counting_curve.csv HV, counts, Δt | Plot B, #1-5 |
| Pulse height consistency: results, rate vs amplitude | centroid channels, gross counts, 30 s | Plot C, #7-8 |
| Beta attenuation: ln plot with error bars, n, expected value, endpoint energy | beta_attenuation.csv | Plot D, #9-15 |
| Dead time: scope markers, compare two measurements, model, which to trust | scope readings and screenshot; two_source_dead_time.csv | Plots E1-E3, #16-22 |
