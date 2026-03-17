# Review Risks

These are the highest-probability self-inflicted review problems for the current
paper shape.

## Risk 1: overclaiming the paper type

Bad version:

- calling the paper a new agent framework or a new model contribution

Safer version:

- call it a controlled systems study of embodied-agent execution design in Isaac Sim

## Risk 2: stale asset mismatch

Bad version:

- quoting numbers from `results/processed/block_a_final_closure/` while showing figures from `results/processed/block_a_master_summary/paper_figures/` as if they matched

Safer version:

- treat the master-summary package as layout history only and regenerate final manuscript assets from the correct freeze

## Risk 3: overselling generalization

Bad version:

- implying the results cover all embodied agents, all backends, or real robots

Safer version:

- keep all claims tied to the current tested setup and task families

## Risk 4: hiding limitations

Bad version:

- burying the facts that the study is controlled, simulator-based, and Block A-only

Safer version:

- state those limitations explicitly and early enough that reviewers cannot frame them as omissions

## Risk 5: using package bookkeeping as the main result

Bad version:

- building the story around the merged `146` runs and overall `0.815068` success rate

Safer version:

- build the story around the slice-level causal comparisons and stable ordering
