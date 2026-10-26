# Prompt 1: Lab 4 report (paste into a new Claude session or Claude Code with the NERS 515 folder connected)

You are helping me (Celing Li, NERS 515, Fall 2026, partner Charalampos Alexander Korfiatis) write my part of the Lab 4 report (Geiger-Müller Counting). Work in my folder `NERS 515/`. Do not write anything yet. Your first output is an outline for me to approve (Step 1).

## 0. What I own and what my partner owns

I write: **Introduction, Equipment and Procedure, Data** (raw data tables with commentary), and the **calculations in Data Analysis** (formulas used, sample calculation, result tables, plots, captions).

My partner writes: **Theory, the discussion/interpretation in Data Analysis, and Conclusions.** Leave `% PARTNER:` placeholders for his parts. The Abstract is written last by whoever finishes their part last, so leave it empty.

My partner's Theory depends on the equations my calculations use, so give him a handoff list: every equation and method used in my sections with its source (Knoll eq./page, slide, manual section). I still have to hand over every number and figure the manual's report requirements ask for (see `03_calculation_to_conclusion_table.md`).

## 1. Hard rule on sources (cheating risk)

Every concept, equation, definition and method in the report must come from one of these three sources only:

1. Knoll, *Radiation Detection and Measurement*, 4th ed. (`Knoll_Radiation_Detection_Fourth.pdf`; book page N = PDF page N + 28)
2. The course lecture slides (`lectures/`, especially Ch3, Ch4+10, Ch5-7, Ch1_2)
3. The Lab 4 manual (`Lab 4/`, three PDFs)

Do not use the web, your own memory, or `pdfcoffee.com-knoll-solutions-manual-3rd-ed.pdf` as a source. The reading-notes doc ("Lab 4 GM Counting: Reading Notes and Pre-Lab Answers") is a map to Knoll, not a source: re-check every equation against Knoll or the slides and cite Knoll/slides, never the notes.

Cite every equation and non-obvious claim in the Lab 3 style: `(Knoll, Eq. 4.32) \cite{knoll}`, or a slide reference. If something I need cannot be traced to a page, equation or slide, stop and ask me. Do not fill the gap yourself. Also ask if two sources disagree.

## 2. Files to read first

- `Lab 4/` : manual (three PDFs) and `lab4_notebook.pdf` (my handwritten settings and values, pp. 19-23).
- `NERS-515-Lab/lab_4/data/` : `beta_attenuation.csv`, `counting_curve.csv`, `two_source_dead_time.csv` (the dead-time run was re-recorded, T = 10 s per measurement; use this, not the notebook's old 8 s numbers).
- `NERS-515-Lab/lab_4/lab_4_plots.py` : the plotting script (a separate prompt handles it; you only need its outputs and numbers).
- `guidelines/` : the three guideline PDFs. Follow them: computer-prepared, numbered pages, brief and concise, answers first, equipment identified by name/manufacturer/model/serial, voluminous tables and sample calculations in appendices, proper citations. Max 15 pages excluding the title page and appendices.
- `lab 3/NERS_515___Lab_3_Report.pdf` and `lab 2/NERS_515___Lab_2_Report.pdf` : my earlier reports. They scored low, so take only writing style and layout (compact paragraphs, caption format, citation format), not the content or analysis approach.
- `old/annotated-NERS515_LabReport7-1 (1)/` and `lab 1/annotated-Lab_1_Report.pdf` : annotated reports. Read the grader's margin comments and tell me, in the outline, what they penalize and reward (e.g. missing uncertainties, unexplained figures, wrong units). Use this to avoid the same mistakes.
- Scope screenshots: `NERS-515-Lab/lab_4/report_prep/figures/scope_dead_time.jpg` (cursors −2 µs to 358 µs, ΔX = 360 µs) and `scope_recovery_time.jpg` (cursors 358 µs to 838 µs, ΔX = 480 µs). The cursors on the images are the markers the manual asks for; use these images as they are (100 µs/div, Normal trigger, ∞ persist, trigger level −78.2 mV).
- **The LaTeX template:** `NERS-515-Lab/lab_4/report_prep/04_lab4_blank.tex` with `references.bib` and `michigan_seal.png`. This is my real template (same preamble, title page and headings as Labs 2 and 3), with the Lab 3 content removed. Do not change the preamble, title page or section headings. Cite with `\cite{knoll}`, `\cite{labmanual}` and `\cite{lab2}` (our Lab 2 report, for the MCA calibration). Add new entries to `references.bib` only for allowed sources.

## 3. Step 1: outline for my approval (stop after this)

Produce an outline that, for each section and subsection I write, gives:

- purpose in one line
- what goes in it (bullets)
- every equation used, with its source (Knoll eq./page, slide, or manual section)
- every figure and table: number, one-line draft caption, and where it sits (Data vs Data Analysis)
- rough page budget (total ≤ 15 pages before appendices; my sections plus room for my partner's)
- which items go to an appendix

Also include: (a) the grader-comment patterns you found in the annotated reports; (b) the equation handoff list for my partner's Theory; (c) a list of questions for me (anything you could not source, treatment choices in Section 7). Then stop and wait. Do not write the full text until I approve.

## 4. Step 2: writing (only after I approve the outline)

Write section by section in the template. Compile it (pdflatex, bibtex, pdflatex twice) and report the page count after each major section.

**Introduction (short, one paragraph).** State the purpose of the lab: characterize a G-M tube and its counting system. Name the four measurements in one sentence each at most (counting curve and pulse height vs HV, pulse height consistency, beta attenuation, dead time by two methods) and what each is for. No results, no theory, no background the reader already has. A draft is already in the template: tighten it, do not lengthen it. Source: the manual.

**Equipment and Procedure.** Follow the manual and cite it. Do not write the procedure out step by step. Write a short paragraph per measurement pointing at the manual section, plus a settings table of what we had to find or choose (from my notebook): operating voltage 840 V, noise LLD 0.1 V (found at 800 V with the source removed), SCA integral mode, counting interval 3 s, scope baseline correction −2.625 mV, HV from 650 V to 910 V in 20 V steps with a 30 s settle before each 3 s count, MCA spectra 30 s real time, channel-to-voltage calibration taken from our Lab 2 report, beta source (Co-60) and tray position, absorber thicknesses and count times, scope persist settings. Confirm each value with me if it is not clearly in the notebook.

Two-source geometry (from me): the sources were on the **3rd shelf, about 3 cm from the tube**, placed **side by side about 3 cm apart**. At that distance a millimeter of movement changes the rate noticeably, so we did not move the source that stays in place between measurements (source A), and only source B was inserted and removed. Say this in the procedure and refer to it in the Data commentary.

Equipment table: keep the template's format (Purpose / Manufacturer / Model / Serial Number) and the five Lab 3 rows only. We have no make/model/serial for the G-M tube, pre-amplifier, MCA or sources, so, as in Lab 3, name them in the sentence above the table (G-M tube, pre-amplifier, MCA, and the Th-232, Co-60, C-14 and Cl-36 sources). Do not invent details. We did not open the NIM, so "-" for the SCA and HV supply with the same sentence as Lab 3.

**Data.** Raw data only, in tables with brief captions, each followed by commentary. Raw means as recorded: HV, counts, counting interval, scope pulse height ± reading uncertainty; MCA centroid channel and gross counts per source (30 s real time); absorber material, mass thickness, counts, time; scope τ and recovery time readings; two-source counts per run (background, A, B, A+B) and time. Rates, uncertainties, logs and fitted values go in Data Analysis, not here. Commentary states what happened and what looks off, without interpreting the physics (that is my partner's part). For example: where counts first appeared, the abrupt rate jump at 910 V and that we stopped there; the beta rates dropping quickly and then flattening; the spread of the Th-232-only counts across the three runs (722 to 1174 in 10 s, versus about ±30 expected from Poisson) despite the care taken with source position. Both scope screenshots belong here as Figure 3(a)(b), with a table of the cursor readings. Do not mention any earlier two-source measurement; the report only contains the final data set.

**Data Analysis (my calculations only).** For each manual requirement, give the formula (cited), a sample calculation with units, the result table, and the figure with a brief caption. Use the plots from the plotting prompt. End each subsection with a `% PARTNER:` placeholder. Subsections: pulse height vs HV; counting curve and plateau slope; pulse height consistency; beta attenuation; dead time (scope and two-source, with uncertainties). Move long sample calculations to an appendix.

## 5. Style

- Write in my voice: plain, direct and a bit informal for a lab report. Shorter sentences, no filler such as "it is important to note", "furthermore", "in order to", "plays a crucial role". Prefer "we" for what was done. Avoid em-dash chains and inflated phrasing. Look at my Lab 3 text for the register and match it.
- Answers first, then support. Compact paragraphs. Define a symbol once.
- Figures and tables: clear axis labels with units, readable fonts, brief caption, each referenced in the text.
- Uncertainties on every quoted result, with the method named.
- Anything you are unsure about gets flagged to me, not smoothed over.

## 6. Data issues to be honest about (do not hide or smooth)

- **Beta attenuation is not one exponential.** Net rates are about 67, 15.6, 12.8, 13, 10.8, 10.6, 5.0, 6.1 s⁻¹ for 14.7 to 1541 mg/cm² Al: a steep drop over the first two points, then a slow "tail" from about 177 mg/cm² on. Knoll p. 45 says the beta curve is only approximately exponential, empirical, and steeper at first because soft betas stop quickly. By Knoll's rule of thumb on p. 44 (about 1 mm of a moderate-density material per MeV), betas of a few tenths of an MeV are stopped well before 200 mg/cm² of Al, so the tail is not beta particles. Knoll p. 218 says a G-M tube responds to gammas through wall interactions with efficiency of a few percent at most, which fits a source that also emits gammas (Co-60). The zero-absorber row is the background (5 counts in 5 s); there is no unattenuated source measurement, so I₀ comes from the fit. The Pb rows are not in the Al fit.
- **Two-source dead time:** per-trial τ = 298, 612, 971 µs. The fractional dead time m₁₂τ is only about 5-14%, below the 20% Knoll recommends in the two-source discussion (Knoll pp. 124-125; confirm the page), and propagated Poisson uncertainties on each τ are as large as τ itself. Report this plainly.
- **Scope times:** the dead time is 360 µs (cursors from the initial pulse at −2 µs to where later pulses first appear at 358 µs). The 480 µs reading is from 358 µs to 838 µs, where pulses reach full height. In Knoll Fig. 7.4 (p. 213) the recovery time is measured from the initial pulse, which gives about 840 µs. Report both with their definitions and ask me which to call the recovery time. My notebook says 482 µs but the screenshot reads 480.000 µs: use the screenshot.
- **Pulse height consistency:** the three sources do not give the same amplitude, and amplitude falls as count rate rises. Report the numbers and do not explain them away (my partner discusses).
- Plateau slope depends on how the plateau range and reference rate are chosen. State both. Ask me if Knoll or the slides define it differently from what you assume.

## 7. Questions to ask me before settling on a method

- **Treatment of the beta tail.** None of the three sources says to subtract a gamma component. Options: (a) fit all points, as the manual literally asks, and report the poor χ²; (b) also report n from the first two points, labeled as such; (c) subtract a flat tail level before taking the log. Do (a) and (b) by default. Do not do (c) unless I say so, and if we do, label it as our own treatment. I may ask the TA first.
- How the plateau slope is defined in Knoll/slides (reference rate, units).
- The uncertainty of the MCA centroid and of the calibration (not recorded), and the scope cursor reading uncertainty (the cursor step is 2 µs but the pulse edges are gradual).
- **Calibration sign:** Lab 2 gives channel = 765.8 V + 27.6, so V = (n − 27.6)/765.8, i.e. −36.0 mV + 1.306 mV × n. My notebook has +35.98 mV. Compute both, show the difference in the three amplitudes, and ask me which is right before using either.

## 8. Delivery

Save the .tex files under `NERS-515-Lab/lab_4/report/` and compile a PDF. Tell me the page count, anything missing, and every place where you inferred rather than took a value from my notebook or the data.
