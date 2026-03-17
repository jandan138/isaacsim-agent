# Limitations

This paper should state its boundaries plainly. These are not optional caveats.

## Study scope limitations

- The study is simulator-based and controlled. Its evidence comes from the current Isaac Sim Block A setup, not from real-robot execution.
- The paper covers Block A only. It does not cover the later roadmap items in `plan.md`.
- The paper studies two design axes only: prompt/interface structure and lightweight runtime validation.
- The paper covers two task families only: navigation and tabletop manipulation.
- Difficulty coverage is limited to the current easy/shared slices plus the present harder navigation and harder manipulation slices.

## Experimental limitations

- The focused prompt-only, runtime-only, and harder-manipulation slices are intentionally small and should be treated as directional evidence rather than large-scale inferential studies.
- The current processed outputs do not provide confidence intervals, significance tests, or multi-seed robustness claims.
- Backend coverage is uneven across slices. Some navigation evidence includes minimal Isaac-backed runs, while the newer focused ablations are toy-backed.
- The runtime-only ablation is built around recoverable invalid-first-action probes, so it isolates recovery value but does not prove a broader runtime taxonomy.

## Framing limitations

- This is not a state-of-the-art agent paper.
- This is not a new-model paper.
- This is not a full-framework paper covering memory, context management, tool abstraction, or domain randomization.
- The paper should argue for design principles under controlled conditions, not for general embodied intelligence.

## Paper-asset limitations

- Existing packaged figures and tables under `results/processed/block_a_master_summary/` are legacy templates, not the final frozen evidence package.
- A future writing task still needs to regenerate final paper figures/tables from the correct final-closure sources.

## Safe conclusion wording

The safest conclusion is:

Within the current controlled Isaac Sim study, structured interfaces, lightweight
runtime validation, and a brief self-check meaningfully affect reliability and
execution overhead.
