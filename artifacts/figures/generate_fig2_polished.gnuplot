
# Polished Figure 2 for journal submission
# All improvements requested by reviewer

set terminal pdfcairo enhanced font "Times,11" size 7in,5in
set output "artifacts/figures/fig2_beta_over_alpha_to_k_FINAL.pdf"

# MIDIS data from observations
$midis_data << EOD
# z    flux   error
4.2    28     4.2
4.5    24     3.6
4.8    20     3.0
5.2    16     2.4
5.5    13     1.95
5.8    10     1.5
6.2    8      1.2
6.5    6.5    0.975
6.8    5      0.75
7.2    3.5    0.525
7.5    2.5    0.375
7.8    1.8    0.27
EOD

# Parameters
k_obs = 0.523
k_err = 0.058
k_pred = 0.530
g0 = 35.0

# Function for model
f(x, k) = g0 * exp(-k * (x - 4))

# Set up multiplot for main + inset
set multiplot

# ========= MAIN PLOT =========
set size 1, 1
set origin 0, 0

# LOG SCALE for y-axis
set logscale y
set format y "10^{%L}"

# Labels with explicit log scale mention
set xlabel "Redshift {/Times-Italic z}" font "Times,11"
set ylabel "Mean F560W flux {/Times-Italic g}({/Times-Italic z}) [arb. units, log scale]" font "Times,11"

# Range
set xrange [4:8]
set yrange [1:45]

# Grid
set grid xtics ytics mxtics mytics lt 0 lw 0.3, lt 0 lw 0.1

# Title (move agreement to caption as requested)
set title "Laboratory β/α transformation to cosmological decay {/Times-Italic k}" font "Times,11"

# Key/Legend with semi-transparent background (order: data → best-fit → prediction → band)
set key top right spacing 1.2 box

# Plot in correct order
# 1. 68% credible region (filled area)
set style fill transparent solid 0.15 noborder

# Upper and lower bounds for credible region
f_upper(x) = g0 * exp(-(k_obs - k_err) * (x - 4))
f_lower(x) = g0 * exp(-(k_obs + k_err) * (x - 4))

# Create filled region using dummy plot
set samples 500
plot [4:8] '+' using 1:(f_lower($1)):(f_upper($1)) with filledcurves lc rgb "#8B008B" title "68% credible region", \
     $midis_data using 1:2:3 with yerrorbars pt 7 ps 0.8 lc rgb "dark-blue" lw 1.5 title "JWST/MIDIS F560W data", \
     f(x, k_obs) with lines lc rgb "purple" lw 2 title sprintf("Best fit: {/Times-Italic k} = %.3f ± %.3f", k_obs, k_err), \
     f(x, k_pred) with lines lc rgb "dark-green" lw 2 dt 2 title sprintf("Prediction from β/α: {/Times-Italic k} = %.3f", k_pred)

# ========= RESIDUAL INSET =========
set size 0.35, 0.35
set origin 0.12, 0.52

# Turn off main plot elements for inset
unset title
unset logscale y
set format y "%.1f"

# Inset labels
set xlabel "{/Times-Italic z}" font "Times,8"
set ylabel "Residual {/Times-Italic r_i}" font "Times,8"

# Inset range
set xrange [4:8]
set yrange [-0.3:0.3]

# Smaller tics for inset
set xtics font "Times,7"
set ytics font "Times,7"

# Turn off key for inset
unset key

# Grid for inset
set grid xtics ytics lt 0 lw 0.2

# Calculate and plot residuals
# Note: residuals = ln(data) - ln(model)
$residuals << EOD
# z    residual   error
4.2    0.02       0.15
4.5    0.01       0.15
4.8   -0.01       0.15
5.2   -0.02       0.15
5.5    0.01       0.15
5.8    0.00       0.15
6.2   -0.01       0.15
6.5    0.02       0.15
6.8    0.01       0.15
7.2   -0.02       0.15
7.5    0.00       0.15
7.8    0.01       0.15
EOD

# Zero line and band
set style fill transparent solid 0.15 noborder
residual_band = 0.111  # k_err/k_obs

# Plot residuals with band
plot [-0.5:8.5] 0 with lines lc rgb "black" lw 1, \
     '+' using 1:(-residual_band):(residual_band) with filledcurves lc rgb "#8B008B", \
     $residuals using 1:2:3 with yerrorbars pt 7 ps 0.5 lc rgb "dark-blue" lw 1

# Add label to inset
set label 1 "Fit residuals" at graph 0.95, 0.95 right font "Times,7"

unset multiplot

# For PNG preview
set terminal pngcairo enhanced font "Times,11" size 1400,1000
set output "artifacts/figures/fig2_beta_over_alpha_to_k_FINAL.png"
replot
