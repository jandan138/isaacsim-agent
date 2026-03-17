# CoRL-Style Outline

This outline is a style adaptation plan, not a claim about official CoRL formatting
rules. The goal is to preserve the same evidence while allowing a somewhat broader
empirical discussion of embodied decision-making and runtime design axes.

## Style direction

- keep the science identical to the neutral version unless new evidence is added later
- allow more space for empirical framing and interpretation than RA-L
- foreground prompt/interface structure and runtime validation as embodied execution design axes
- keep the paper away from unsupported `new model` or `general agent` framing

## 1. Introduction

### 1.1 Embodied decision-making motivation

- motivate decision failures at the interface between planner outputs and runtime execution

### 1.2 Why a controlled study matters

- position the paper as an empirical study of design choices rather than a larger benchmark

### 1.3 Scope and findings preview

- state the Block A scope and the stable ordering

## 2. Related Empirical Context

### 2.1 Embodied-agent evaluation and system studies

- keep this tightly tied to the paper's role

### 2.2 Runtime and execution reliability

- motivate recovery and validation as empirical axes

## 3. Problem Setting and Execution Interface

### 3.1 Task families and simulator setting

- navigation and manipulation in Isaac Sim

### 3.2 Prompt/interface variants

- `P0`, `P1`, `P2`

### 3.3 Runtime variants

- `R0`, `R1`

### 3.4 Metrics

- success, invalid actions, retries, planner calls, tool calls

## 4. Controlled Study Design

### 4.1 Main factorial study

- prompt x runtime matrix

### 4.2 Focused ablations

- runtime-only
- prompt-only

### 4.3 Cross-family and harder-slice checks

- what counts as family consistency and harder-task robustness in the current evidence

## 5. Results

### 5.1 Main ordering across conditions

- same core content as neutral and RA-L

### 5.2 Runtime recovers fragile runs

- emphasize recovery on invalid-action probes

### 5.3 Structured interfaces remove invalid actions

- emphasize invalid-action reduction and clean execution

### 5.4 Self-check and execution efficiency

- emphasize `P2` cost reduction relative to `P1`

### 5.5 Cross-family and harder-task consistency

- unify the current robustness evidence

## 6. Discussion

### 6.1 What the study suggests about embodied execution design

- interface structure and runtime support as complementary axes

### 6.2 What the study does not show

- no generalization beyond the tested setup
- no broader roadmap claims

### 6.3 How to reuse the shared manuscript core

- keep results and setup largely shared from the neutral version
- rewrite introduction, related work, and discussion to fit the more empirical CoRL style

## 7. Conclusion

- short empirical takeaway paragraph

## CoRL rewrite focus

Rewrite first if branching here:

1. title
2. abstract
3. introduction
4. discussion

Keep mostly shared:

1. setup
2. design-axis definitions
3. results
4. limitations
