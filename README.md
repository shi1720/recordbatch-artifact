# RecordBatch reproducibility artifact

RecordBatch: Exact Sequential Batch Testing under Unknown Dependence.
Author: Shivam Gupta. Research candidate, October 2026; not peer reviewed.

The paper establishes a record-prefix normal form for fixed-marginal,
unknown-dependence AND batch testing, with additive committed costs and setup.
The optimizer uses O(n² log n) arithmetic; a zero-setup specialization uses
O(n log n). The least-favorable comonotonic coupling is classical. Exact
optimality in this model does not establish deployment savings.

## Reproduce

Use Python 3.9 or newer and the pinned requirements:

    python3 -m venv .venv
    .venv/bin/python -m pip install -r requirements.txt
    .venv/bin/python -m pytest tests -q

Tests and their recorded output are supplied. To regenerate the principal
experiments (subset-DP baselines are exponential):

    .venv/bin/python experiments/run_synthetic.py
    .venv/bin/python experiments/run_envelope.py
    .venv/bin/python experiments/benchmark.py
    .venv/bin/python experiments/run_capacity_large.py
    .venv/bin/python experiments/replay_panels.py
    .venv/bin/python experiments/review_zero_setup.py --benchmark
    .venv/bin/python experiments/make_figures.py
    cd paper
    tectonic paper.tex

The source paper and PDF are in paper/. Four vector figures, two tables,
fourteen references, complete proofs, and an assistance disclosure are included.
Measured timings depend on hardware and load. The original benchmark machine
and software versions are recorded in results/environment.json.

## Evidence and limits

Eleven test functions include 1,315 enumerated or seeded instance checks,
plus boundary and invalid-input checks. The released 480 synthetic instances
compare exact robust and independent-law optimizers. All 180 replay rows can
be reconstructed from the nine distributed derived panels (797 held-out
sessions). Refined RecordBatch has lower/equal/higher replay cost in 3/20/13
configurations; its median premium is zero, but positive-setup losses can
be large. These are related configurations, not independent replicates.

Zero-setup refinement splits a residual batch and never increases cost on
any Boolean outcome. Original and refined policies remain in ablation CSVs.
Its median independent-law premium on the zero-setup synthetic cases falls
from 49.64% to 0.01%. It does not optimize nominal cost over all robust ties.
The fast zero-setup algorithm can choose a different robust-optimal prefix.

The industrial setup cost is modeled, not measured. Complete-case selection,
censoring and chronological drift limit generalization. The paper's iid
certificate is not claimed for these chronological sessions. Capacity results
use a standard CP-SAT formulation and small exact-grid synthetic instances.

## Source data

Derived Westermo panels retain the source attribution and CC BY 4.0 license.
See data/ATTRIBUTION.md and data/provenance.json. Full reconstruction:

    git clone https://github.com/westermo/test-results-dataset /tmp/recordbatch-westermo
    git -C /tmp/recordbatch-westermo checkout 31ca0ab802fd2eecf3455c6622c2c18f5b3fe775
    .venv/bin/python experiments/run_westermo.py /tmp/recordbatch-westermo/data/test-results.zip

## License and scholarly responsibility

Source code is MIT licensed. Derived data is CC BY 4.0. The manuscript is
released under CC BY 4.0. Bundled Springer template files retain their own
notices. The manuscript credits the author's objectives, critical review and
revision direction and discloses substantive OpenAI Codex assistance, including
research reasoning, implementation, experiments and manuscript drafting.
No acceptance, patentability or universal priority claim is made.
