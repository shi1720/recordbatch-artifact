# Literature and overlap audit

Search and source review: 11–12 October 2026. This is a bounded audit, not proof
of universal novelty or a patent clearance search. The proposal remains a
research draft requiring independent expert assessment.

## Claim map

| Claim | Status |
| --- | --- |
| Fixed-marginal intersection maximum equals minimum marginal | Classical Fréchet upper bound; not new |
| Shared-uniform law maximizes all nonnegative conjunction terms | Classical comonotonic/supermodular maximization; not new |
| Ordered partition represents deterministic AND batch policy | Standard model observation |
| Singleton probability-record prefix plus one residual batch | Proposed new scoped structural result |
| Terminal-marginal shortest-path reduction | Proposed result for this exact model |
| Monotone-slope lower envelope | Standard data structure applied to the new reduction |
| O(n² log n) optimizer | Proposed algorithmic consequence |
| O(n log n) zero-setup specialization | Proposed fixed-terminal consequence; independently checked |
| Pointwise tail refinement at zero setup | Elementary splitting dominance; repairs an operational tie |
| Failure under any positive nominal weight | Three-test boundary example; not a hardness claim |
| Unbounded robust loss of independence-designed schedules | Proposed separation family for this model |
| Interval upper endpoints, Lipschitz and Hoeffding bounds | Elementary corollaries using standard tools |
| Capacity hardness | Packing reduction for this robust model; capacity testing is already known hard in other models |
| CP-SAT encoding | Direct implementation using standard solver primitives |
| Commercial applicability or patentability | Not established |

## Primary sources reviewed

1. Agrawal, Ding, Saberi, Ye (2012), Price of correlations in stochastic
   optimization. DOI: https://doi.org/10.1287/opre.1110.1011
   The downloaded full text's supermodular discussion and comonotonic law
   establish the classical nature of our extremal coupling.
2. Daldal et al. (2017), Sequential testing in batches.
   https://doi.org/10.1007/s10479-016-2345-7
   Existing batch-testing problem; no claim to originate batching.
3. Segev and Shaposhnik, online 2021, volume 2022, PTAS for series systems.
   https://doi.org/10.1287/opre.2019.1967
   Independent-outcome approximation results, not the ambiguity model here.
4. Tan, Xu, Nagarajan (2025), A general framework for sequential batch-testing.
   https://doi.org/10.1016/j.orl.2025.107348
   Full 2024 author preprint reviewed. Independent Bernoulli outcomes,
   additive test costs plus setup, generic approximation reduction.
5. Harris, Nagarajan, Tan (2025), Sequential testing with subadditive costs.
   https://doi.org/10.1007/978-3-031-93112-3_21
   https://arxiv.org/abs/2501.18010
   Full preprint reviewed; richer costs with independent outcomes.
6. Tan and Nagarajan (2026), Distributionally Robust k-of-n Sequential Testing.
   https://arxiv.org/abs/2603.23705
   Full preprint reviewed. Test probabilities vary in intervals; tests remain
   independent. This is the closest terminology overlap and is explicitly
   contrasted, not overlooked.
7. Ghuge, Moondra, Singh (2026), Stochastic Function Certification with Correlations.
   https://arxiv.org/abs/2604.02611
   Primary abstract/model reviewed: supplied joint law; chiefly certification
   and matroid settings, not optimization over all couplings.
8. Yang, Hermans, Zufferey, Leus (2024), Sequential testing in batches with
   resource constraints. https://doi.org/10.1016/j.eswa.2024.124858
   Publisher description and author institutional record reviewed.
   Existing capacity-constrained batch optimization and hardness; do not claim
   our CP formulation introduces this general extension.
9. Ünlüyurt (2004), Sequential testing of complex systems: a review.
   Classical problem context. The 2025 follow-up review was also downloaded
   and its model, correlated-evaluation discussion, batch section and conclusion
   inspected: https://arxiv.org/abs/2511.15742
   https://doi.org/10.1016/j.dam.2025.07.039
   It surveys product-law batching and supplied correlated laws and identifies
   robust parameter uncertainty as a research direction. It does not establish
   absence of all fixed-marginal results under other terminology.
10. Perron, Didier, Gay (2023), The CP-SAT-LP Solver.
    https://doi.org/10.4230/LIPIcs.CP.2023.3
    Solver attribution, not a novelty source for the model.
11. Strandberg (2022), The Westermo test results data set.
    https://arxiv.org/abs/2211.13622
    https://github.com/westermo/test-results-dataset
    Repository documentation reviewed for verdict semantics and source license.
12. Hoeffding (1963), Probability inequalities for sums of bounded random variables.
    https://doi.org/10.1080/01621459.1963.10500830
    Classical estimation tool; no novel statistical inequality claimed.
13. Kaplan, Kushilevitz, Mansour (2005), Learning with attribute costs.
    https://doi.org/10.1145/1060590.1060644
    https://www.cs.umd.edu/projects/reucaar/learningwacosts.pdf
    Supplied potentially correlated distribution and clause evaluation, rather
    than fixed marginals with arbitrary-coupling optimization. Added to the
    paper to acknowledge the older correlated-evaluation literature.

## Search families

Queries combined sequential testing, batch testing, stochastic Boolean function
evaluation, series-system testing, AND testing, unknown dependence,
distributionally robust, fixed marginals, Fréchet bounds, comonotonicity,
correlation gap, shared failures, uncertainty intervals, batching setup costs,
resource capacity, robust ordering and correlated function certification.
Exact combinations such as "sequential testing" "comonotonic",
"batch testing" "marginal" "robust", and "sequential testing"
"unknown dependence" did not identify an identical record-path formulation.
Absence from search results is not evidence of absolute absence from the field.

## Remaining novelty risk

The mathematical contribution is narrow and its proof is short. A reviewer may
regard it as an incremental consequence of known comonotonic optimization, or
an equivalent sequential-search formulation may exist under different names.
No claim of an industry-defining breakthrough is justified. The exact algorithm,
the model separation, and the candid operational evidence are the defensible
submission argument. A further expert literature review is needed before
asserting priority or deciding whether the contribution meets a long-paper bar.

## Critical revision, 12 October

Repeated searches for fixed-marginal robust batch testing and comonotonic
series-system ordering did not expose the same record-path formulation.
Many hits concern statistical hypothesis testing, a different problem.
The contribution is still scoped; lack of a search hit does not prove priority.
The zero-setup specialization and mixed-objective boundary strengthen the
technical account. The ablation repairs an avoidable performance weakness,
without converting replay into a claim of broad industrial cost savings.
