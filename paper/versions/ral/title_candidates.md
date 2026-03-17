# RA-L Title Candidates

These options keep the paper framed as a controlled robotics-systems study of
planner-to-executor contract design, action interfaces, and runtime validation in
Isaac Sim. They are grouped by how aggressively they state the result.

## A. Most conservative: controlled-study framing

| Title | Pros | Risks | Likely reviewer impression |
| --- | --- | --- | --- |
| A Controlled Study of Planner-to-Executor Contract Design and Runtime Validation for Embodied-Agent Execution in Isaac Sim | Very explicit about scope, axes, and setting; hard to misread as a model paper. | Slightly long and method-like. | Careful, evidence-bounded, robotics-systems oriented. |
| Action Interface Specification and Runtime Validation in Isaac Sim: A Controlled Study of Embodied-Agent Execution | Keeps the two design axes visible while sounding more like a systems paper than a prompt paper. | `Action interface specification` is slightly formal. | Clear, sober, and easy to map to the experimental matrix. |
| Planner-to-Executor Contracts for Embodied-Agent Execution in Isaac Sim: A Controlled Systems Study | Compact and architecture-forward. | Slightly less explicit about the runtime axis unless the abstract carries it. | Reviewer sees a systems paper first, not a prompt ablation. |

## B. Slightly stronger: finding-forward framing

| Title | Pros | Risks | Likely reviewer impression |
| --- | --- | --- | --- |
| Structured Action Interfaces and Lightweight Runtime Validation Improve Embodied-Agent Execution in Isaac Sim | Communicates the main result quickly and cleanly. | `Improve` is stronger than `study` and invites tighter scrutiny on scope. | Strong but still reasonable if the abstract immediately states the controlled setting. |
| Execution Contracts Shape Reliability and Planner/Tool Overhead in Isaac Sim Embodied-Agent Tasks | Captures both reliability and efficiency without sounding like a benchmark paper. | `Execution contracts` may need early definition. | Results-driven and systems-relevant. |

## C. Slightly more robotics-systems oriented

| Title | Pros | Risks | Likely reviewer impression |
| --- | --- | --- | --- |
| System Design for Embodied-Agent Execution in Isaac Sim: Contracts, Runtime Validation, and Recovery | Reads like a robotics systems paper and foregrounds recovery. | `System Design` can drift toward a broader framework reading if the abstract is not disciplined. | Robotics-systems relevant, with an execution focus rather than a benchmark focus. |
| Planner-to-Executor Contract Design for Reliable Embodied-Agent Execution in Isaac Sim | Very close to the paper's architectural lesson. | `Reliable` can sound stronger than the evidence if not bounded to the tested setup. | Applied and architecture-forward. |

## Current recommendation

The safest two candidates for this draft branch are:

1. `A Controlled Study of Planner-to-Executor Contract Design and Runtime Validation for Embodied-Agent Execution in Isaac Sim`
2. `Action Interface Specification and Runtime Validation in Isaac Sim: A Controlled Study of Embodied-Agent Execution`
