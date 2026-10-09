import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# ============================================================================
# LOAD DATA
# ============================================================================
gaussian_data = pd.read_csv('count_30.csv')
poisson_data = pd.read_csv('count_7.csv')

gaussian_counts = gaussian_data['Count'].values
poisson_counts = poisson_data['Count'].values

print("="*80)
print("LAB 3: COUNTING STATISTICS AND ERROR ANALYSIS")
print("="*80)

# ============================================================================
# SECTION 2.2.1: GAUSSIAN DISTRIBUTION ANALYSIS (50 measurements, avg ~30)
# ============================================================================
print("\n" + "="*80)
print("2.2.1 MEASUREMENT OF GAUSSIAN DISTRIBUTION (N=50, avg≈30)")
print("="*80)

# Calculate statistics
gaussian_mean = np.mean(gaussian_counts)
gaussian_std = np.std(gaussian_counts, ddof=1)  # Sample std dev
gaussian_var = np.var(gaussian_counts, ddof=1)

print(f"\nExperimental Statistics:")
print(f"  Mean (μ):              {gaussian_mean:.2f}")
print(f"  Standard Deviation:    {gaussian_std:.2f}")
print(f"  Variance (σ²):         {gaussian_var:.2f}")
print(f"  √N (expected σ):       {np.sqrt(gaussian_mean):.2f}")
print(f"  Min Count:             {np.min(gaussian_counts)}")
print(f"  Max Count:             {np.max(gaussian_counts)}")

# Create frequency table
print("\n" + "-"*60)
print("FREQUENCY TABLE - Gaussian Distribution")
print("-"*60)
print(f"{'Count':<10} {'Frequency':<12} {'P(Count)':<15}")
print("-"*60)

gaussian_freq_dict = {}
for i in range(np.min(gaussian_counts), np.max(gaussian_counts) + 1):
    freq = np.sum(gaussian_counts == i)
    if freq > 0:
        gaussian_freq_dict[i] = freq
        prob = freq / len(gaussian_counts)
        print(f"{i:<10} {freq:<12} {prob:<15.4f}")

print("-"*60)
print(f"{'TOTAL':<10} {len(gaussian_counts):<12} {1.0:<15.4f}")
print("-"*60)

# ============================================================================
# SECTION 2.2.2: POISSON DISTRIBUTION ANALYSIS (1000 measurements, avg ~7)
# ============================================================================
print("\n" + "="*80)
print("2.2.2 MEASUREMENT OF POISSON DISTRIBUTION (N=1000, avg≈7)")
print("="*80)

# Calculate statistics
poisson_mean = np.mean(poisson_counts)
poisson_std = np.std(poisson_counts, ddof=1)
poisson_var = np.var(poisson_counts, ddof=1)

print(f"\nExperimental Statistics:")
print(f"  Mean (μ):              {poisson_mean:.2f}")
print(f"  Standard Deviation:    {poisson_std:.2f}")
print(f"  Variance (σ²):         {poisson_var:.2f}")
print(f"  √N (expected σ):       {np.sqrt(poisson_mean):.2f}")
print(f"  Min Count:             {np.min(poisson_counts)}")
print(f"  Max Count:             {np.max(poisson_counts)}")
print(f"  Note: For Poisson, σ² should ≈ μ. Ratio σ²/μ = {poisson_var/poisson_mean:.3f}")

# Create frequency table
print("\n" + "-"*60)
print("FREQUENCY TABLE - Poisson Distribution")
print("-"*60)
print(f"{'Count':<10} {'Frequency':<12} {'P(Count)':<15}")
print("-"*60)

poisson_freq_dict = {}
for i in range(np.min(poisson_counts), np.max(poisson_counts) + 1):
    freq = np.sum(poisson_counts == i)
    if freq > 0:
        poisson_freq_dict[i] = freq
        prob = freq / len(poisson_counts)
        print(f"{i:<10} {freq:<12} {prob:<15.4f}")

print("-"*60)
print(f"{'TOTAL':<10} {len(poisson_counts):<12} {1.0:<15.4f}")
print("-"*60)

# ============================================================================
# CHI-SQUARED GOODNESS-OF-FIT TEST
# ============================================================================

def chi_squared_test(data):
    """
    Textbook chi-squared (dispersion) test for Poisson counting statistics:

        chi2 = sum((x_i - x_bar)^2) / x_bar = (N - 1) * s^2 / x_bar

    where x_i are the N individual counts and x_bar is the sample mean.
    Degrees of freedom: N - 1.

    Returns
    -------
    chi2_stat : float
    p_value : float   P(chi2 >= observed) if the counts are Poisson distributed
    dof : int
    """
    n = len(data)
    x_bar = np.mean(data)
    chi2_stat = np.sum((data - x_bar)**2) / x_bar
    dof = n - 1
    p_value = stats.chi2.sf(chi2_stat, dof)
    return chi2_stat, p_value, dof

# Chi-squared test for Gaussian data against Poisson distribution
print("\n" + "="*80)
print("CHI-SQUARED GOODNESS-OF-FIT TESTS")
print("="*80)

print("\n" + "-"*60)
print("Gaussian Distribution (N=50) vs Poisson Distribution")
print("-"*60)
chi2_gauss_poisson, p_gauss_poisson, dof_gauss_poisson = chi_squared_test(gaussian_counts)
print(f"Chi-squared statistic (χ²):  {chi2_gauss_poisson:.4f}")
print(f"Degrees of freedom (ν):      {dof_gauss_poisson}")
print(f"Reduced χ² (χ²/ν):           {chi2_gauss_poisson/dof_gauss_poisson:.4f}")
print(f"P-value:                     {p_gauss_poisson:.4f}")
print(f"Interpretation: {'Good fit (accept Poisson model)' if p_gauss_poisson > 0.05 else 'Poor fit (reject Poisson model)'}")
print(f"                P(random sample shows larger fluctuation) = {p_gauss_poisson:.2%}")

print("\n" + "-"*60)
print("Poisson Distribution (N=1000) vs Poisson Distribution")
print("-"*60)
chi2_poisson_poisson, p_poisson_poisson, dof_poisson_poisson = chi_squared_test(poisson_counts)
print(f"Chi-squared statistic (χ²):  {chi2_poisson_poisson:.4f}")
print(f"Degrees of freedom (ν):      {dof_poisson_poisson}")
print(f"Reduced χ² (χ²/ν):           {chi2_poisson_poisson/dof_poisson_poisson:.4f}")
print(f"P-value:                     {p_poisson_poisson:.4f}")
print(f"Interpretation: {'Good fit (accept Poisson model)' if p_poisson_poisson > 0.05 else 'Poor fit (reject Poisson model)'}")
print(f"                P(random sample shows larger fluctuation) = {p_poisson_poisson:.2%}")

# ============================================================================
# GENERATE PLOTS
# ============================================================================

# -------- FIGURE 1: Gaussian Distribution (50 measurements) --------
fig1, ax1 = plt.subplots(figsize=(12, 6))

# Plot histogram
counts_edges = np.arange(np.min(gaussian_counts) - 0.5, np.max(gaussian_counts) + 1.5)
n_hist, bins_edges, patches = ax1.hist(gaussian_counts, bins=counts_edges, density=True, 
                                        alpha=0.6, color='steelblue', edgecolor='black', 
                                        label='Measured Data')

# Generate theoretical distributions
x_range = np.linspace(np.min(gaussian_counts) - 2, np.max(gaussian_counts) + 2, 200)

# Poisson (mean = experimental mean), drawn at integer counts
x_discrete = np.arange(0, np.max(gaussian_counts) + 1)
poisson_pmf = stats.poisson.pmf(x_discrete, gaussian_mean)
ax1.plot(x_discrete, poisson_pmf, 'r-o', linewidth=2.5, markersize=6,
         label='Poisson Fit (μ = x̄ = {:.2f})'.format(gaussian_mean))

# Gaussian (experimental mean and experimental standard deviation)
gaussian_theory = stats.norm.pdf(x_range, gaussian_mean, gaussian_std)
ax1.plot(x_range, gaussian_theory, color='green', linestyle='--', linewidth=2,
         label='Gaussian (μ = x̄, σ = s = {:.2f})'.format(gaussian_std))

# Labels and formatting
ax1.set_xlabel('Number of Counts', fontsize=12, fontweight='bold')
ax1.set_ylabel('Probability P(i)', fontsize=12, fontweight='bold')
ax1.set_title('Gaussian Distribution (50 Measurements, μ ≈ 30)\n' + 
              f'μ = {gaussian_mean:.2f}, σ = {gaussian_std:.2f}, χ² = {chi2_gauss_poisson:.2f}, ν = {dof_gauss_poisson} (p = {p_gauss_poisson:.4f})',
              fontsize=13, fontweight='bold')
ax1.legend(fontsize=11, loc='upper right')
ax1.grid(True, alpha=0.3)
ax1.set_xlim(np.min(gaussian_counts) - 1, np.max(gaussian_counts) + 1)

plt.tight_layout()
plt.savefig('Lab3_Gaussian_N50.png', dpi=300, bbox_inches='tight')
print("\n✓ Saved: Lab3_Gaussian_N50.png")

# -------- FIGURE 2: Poisson Distribution (1000 measurements) --------
fig2, ax2 = plt.subplots(figsize=(12, 6))

# Plot histogram
counts_edges_poisson = np.arange(np.min(poisson_counts) - 0.5, np.max(poisson_counts) + 1.5)
n_hist2, bins_edges2, patches2 = ax2.hist(poisson_counts, bins=counts_edges_poisson, density=True,
                                           alpha=0.6, color='steelblue', edgecolor='black',
                                           label='Measured Data')

# Generate theoretical distributions
x_range_poisson = np.linspace(np.min(poisson_counts) - 1, np.max(poisson_counts) + 1, 200)

# Poisson fit (mean = experimental mean) -- the primary fit for this dataset
x_discrete_poisson = np.arange(0, np.max(poisson_counts) + 1)
poisson_pmf_poisson = stats.poisson.pmf(x_discrete_poisson, poisson_mean)
ax2.plot(x_discrete_poisson, poisson_pmf_poisson, 'r-o', linewidth=2.5, markersize=6,
         label='Poisson Fit (μ = x̄ = {:.2f})'.format(poisson_mean))

# Gaussian for comparison (mean = experimental mean, variance = experimental mean)
gaussian_theory_poisson = stats.norm.pdf(x_range_poisson, poisson_mean, np.sqrt(poisson_mean))
ax2.plot(x_range_poisson, gaussian_theory_poisson, color='green', linestyle='--', linewidth=2,
         label='Gaussian (μ = x̄, σ² = x̄)')

# Labels and formatting
ax2.set_xlabel('Number of Counts', fontsize=12, fontweight='bold')
ax2.set_ylabel('Probability P(i)', fontsize=12, fontweight='bold')
ax2.set_title('Poisson Distribution (1000 Measurements, μ ≈ 7)\n' +
              f'μ = {poisson_mean:.2f}, σ = {poisson_std:.2f}, χ² = {chi2_poisson_poisson:.2f}, ν = {dof_poisson_poisson} (p = {p_poisson_poisson:.4f})',
              fontsize=13, fontweight='bold')
ax2.legend(fontsize=11, loc='upper right')
ax2.grid(True, alpha=0.3)
ax2.set_xlim(np.min(poisson_counts) - 0.5, np.max(poisson_counts) + 0.5)

plt.tight_layout()
plt.savefig('Lab3_Poisson_N1000.png', dpi=300, bbox_inches='tight')
print("✓ Saved: Lab3_Poisson_N1000.png")
plt.show()

# ============================================================================
# SUMMARY TABLE
# ============================================================================

print("\n" + "="*80)
print("SUMMARY STATISTICS TABLE")
print("="*80)

summary_data = {
    'Parameter': ['N (measurements)', 'Mean (μ)', 'Std Dev (σ)', 'Variance (σ²)', '√μ (predicted σ)', 'Min Count', 'Max Count', 'χ² (vs Poisson)', 'P-value', 'Fit Quality'],
    'Gaussian (50)': [
        len(gaussian_counts),
        f'{gaussian_mean:.2f}',
        f'{gaussian_std:.2f}',
        f'{gaussian_var:.2f}',
        f'{np.sqrt(gaussian_mean):.2f}',
        np.min(gaussian_counts),
        np.max(gaussian_counts),
        f'{chi2_gauss_poisson:.4f}',
        f'{p_gauss_poisson:.4f}',
        'Good' if p_gauss_poisson > 0.05 else 'Poor'
    ],
    'Poisson (1000)': [
        len(poisson_counts),
        f'{poisson_mean:.2f}',
        f'{poisson_std:.2f}',
        f'{poisson_var:.2f}',
        f'{np.sqrt(poisson_mean):.2f}',
        np.min(poisson_counts),
        np.max(poisson_counts),
        f'{chi2_poisson_poisson:.4f}',
        f'{p_poisson_poisson:.4f}',
        'Good' if p_poisson_poisson > 0.05 else 'Poor'
    ]
}

summary_df = pd.DataFrame(summary_data)
print(summary_df.to_string(index=False))

print("\n" + "="*80)
print("KEY OBSERVATIONS")
print("="*80)
print("""
For Gaussian Distribution (50 measurements, μ ≈ 30):
  • The measured distribution shows a peak around 30 counts
  • Theoretical prediction: σ ≈ √30 ≈ 5.5 counts
  • The Poisson model should fit reasonably well for this moderate count rate
  
For Poisson Distribution (1000 measurements, μ ≈ 7):
  • The measured distribution shows expected Poisson characteristics
  • For Poisson: variance should equal mean (σ² ≈ μ)
  • The Gaussian approximation works (μ > 10 not quite met, but 1000 samples helps)
  • The Poisson model should fit very well since data were collected from random events

Chi-squared Test Interpretation:
  • p-value > 0.05: Data consistent with theoretical model (good fit)
  • p-value < 0.05: Data deviates from theoretical model (poor fit)
  • The p-value represents P(random sample shows larger fluctuation than observed)
""")

print("\n" + "="*80)
print("Analysis Complete!")
print("="*80)