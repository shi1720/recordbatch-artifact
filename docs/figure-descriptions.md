# Figure descriptions

1. Structure. Three horizontal pass intervals on one uniform axis illustrate
   nested pass events. A shared uniform value 0.4 passes tests with marginals
   0.8 and 0.6 but fails a test with marginal 0.3. A flow diagram shows a
   singleton at 0.8, a singleton at 0.3 and one residual batch, with continuation
   only after a pass. This is an illustrative structure, not an optimized
   numerical schedule.
2. Synthetic comparisons. Boxplots group four setup ratios. Worst-case ratios
   are at most one; nominal independent-law ratios are at least one. The
   nominal panel has a logarithmic vertical axis. Outlier markers are hidden,
   not deleted from the results or summary calculations.
3. Runtime. Log-log paired timing curves show cubic and lower-envelope
   implementations on the same five instances per size, with minimum-to-maximum
   shading. The cubic curve ends at 512 tests and the envelope at 2048.
4. Replay. Nine systems by four setup ratios form a heatmap of percentage
   held-out cost premiums over IndependentDP. Each cell is labeled numerically.
   Red positive values mean higher RecordBatch cost; near-white values are near
   zero. The symmetric color range is minus 350 to plus 350 percent. These
   configurations share sessions and are not independent replicates.

All figures are programmatically drawn from recorded numerical results or a
specified mathematical schematic. No generated experimental imagery is used.
