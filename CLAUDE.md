# CLAUDE.md — isaacsim-agent

## Project Overview

Paper title: **"A Controlled Study of Planner-to-Executor Contract Design and Runtime Validation for Embodied-Agent Execution in Isaac Sim"**

Target venue: **IEEE RA-L (Robotics and Automation Letters)**

Current stage: **论文润色 (paper polishing only — no new experiments)**

## Paper Location

- LaTeX entry point: `paper/versions/ral/main.tex`
- Sections: `paper/versions/ral/sections/*.tex`
- Bibliography: `paper/versions/ral/refs/references.bib`
- Figures: `paper/versions/ral/figures/`
- Tables: `paper/versions/ral/tables/`
- Compiled PDF: `paper/versions/ral/main.pdf`
- Conference variant: `paper/versions/ral/reviewer_submission/`

## Key Context Files

- Core claim boundary: `paper/shared/core_claim.md`
- Evidence ledger: `paper/shared/findings.md`
- Contributions: `paper/shared/contributions.md`
- Limitations: `paper/shared/limitations.md`
- Terminology: `paper/shared/terminology.md`

## Compile Command

```bash
cd paper/versions/ral && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

## Important Notes

- All experiments are complete. Do NOT run or propose new experiments.
- Figures and tables are frozen — data CSVs are final.
- The `results/processed/` directory is not in the repo; all evidence is materialized in `paper/versions/ral/figures/` and `tables/` as `.csv` + `.tex` pairs.
- See `AGENTS.md` for repo conventions and `STATUS.md` for current project state.

## Pipeline Status

stage: paper-polishing
next: run /auto-paper-improvement-loop paper/versions/ral
