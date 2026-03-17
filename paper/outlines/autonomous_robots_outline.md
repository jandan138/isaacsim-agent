# Autonomous Robots-Style Outline

This outline is a style adaptation plan for a more system-oriented journal version.
It does not assume any specific current formatting rule. The goal is to preserve the
Block A evidence while allowing fuller method description, clearer experimental
explanation, and a more explicit limitations section.

## Style direction

- emphasize engineering clarity and system description
- keep the central identity as a controlled systems study
- allow more detail on execution pipeline, experiment construction, and limitations
- do not widen the evidence beyond Block A

## 1. Introduction

### 1.1 Problem and motivation

- embodied-agent execution depends on interface and runtime design, not only planner strength

### 1.2 Paper role

- a controlled Isaac Sim systems study rather than a benchmark race

### 1.3 Contributions and findings preview

- reuse the shared contribution bullets with journal-style prose

## 2. Related Systems Context

### 2.1 Embodied-agent systems and evaluation

- concise positioning only

### 2.2 Runtime execution reliability

- connect the present runtime layer to broader robotics execution concerns

## 3. System and Execution Pipeline

### 3.1 Planner-to-runtime interface

- typed outputs and action/tool contract

### 3.2 Runtime validation and retry path

- how `R0` and `R1` differ

### 3.3 Logging and measured artifacts

- success, invalid actions, retries, planner calls, tool calls

This section can be more detailed than the RA-L version.

## 4. Experimental Setup

### 4.1 Simulator environment and task families

- navigation and manipulation

### 4.2 Easy and harder slices

- what is varied and what remains controlled

### 4.3 Study matrix

- `P0/P1/P2` x `R0/R1`

## 5. Results

### 5.1 Main prompt x runtime pattern

- stable ordering

### 5.2 Runtime-only ablation

- independent recovery value

### 5.3 Prompt-only ablation

- independent interface-structure value

### 5.4 Cross-family consistency

- navigation and manipulation alignment within the covered setup

### 5.5 Harder-task workload amplification

- workload up, ordering unchanged in current harder slices

## 6. Discussion

### 6.1 System-design lessons

- what the study implies for embodied-agent runtime design

### 6.2 Engineering clarity and reproducibility

- explain the value of controlled contracts and explicit runtime handling

### 6.3 Boundaries and non-claims

- keep the limitations explicit and journal-grade

## 7. Limitations

- controlled simulator setting
- limited task and backend scope
- no M7+ axes
- no inferential statistics

This section should likely be more explicit than in RA-L.

## 8. Conclusion

- concise restatement of the controlled-study takeaways

## Journal rewrite focus

Rewrite first if branching here:

1. system/pipeline description
2. experimental setup detail
3. discussion and limitations

Keep mostly shared:

1. result statements
2. variant definitions
3. metric definitions
