# RA-L Title Candidates

These options keep the paper framed as a controlled systems study of embodied-agent
execution in Isaac Sim. They are grouped by how aggressively they state the result.

## A. Most conservative: controlled-study framing

| Title | Pros | Risks | Likely reviewer impression |
| --- | --- | --- | --- |
| A Controlled Study of Prompt Interface Structure and Runtime Validation for Embodied-Agent Execution in Isaac Sim | Very explicit about scope, axes, and setting; hard to misread as a model paper. | Slightly long and method-like. | Careful, evidence-bounded, system-study oriented. |
| Prompt Interface Structure and Runtime Validation in Isaac Sim: A Controlled Study of Embodied-Agent Execution | Keeps the two design axes first while still reading like a systems paper. | Slightly more generic than the first option. | Clear, sober, and easy to map to the experimental matrix. |
| Controlled Design Effects of Prompt Interface Structure and Runtime Validation in Isaac Sim Embodied-Agent Execution | Emphasizes design effects rather than a new architecture. | The phrasing is a bit dense and less natural. | Technically precise, but somewhat dry. |

## B. Slightly stronger: finding-forward framing

| Title | Pros | Risks | Likely reviewer impression |
| --- | --- | --- | --- |
| Structured Interfaces and Lightweight Runtime Validation Improve Embodied-Agent Execution in Isaac Sim | Communicates the main result quickly and cleanly. | "Improve" is stronger than "study" and invites tighter scrutiny on scope. | Strong but still reasonable if the abstract immediately states the controlled setting. |
| Prompt Interface Structure and Runtime Validation Shape Reliability and Cost in Isaac Sim Embodied-Agent Execution | Captures both success and overhead, which matches the evidence well. | "Cost" may sound broader than planner/tool overhead unless defined early. | Results-driven and systems-relevant. |

## C. Slightly more robotics-systems oriented

| Title | Pros | Risks | Likely reviewer impression |
| --- | --- | --- | --- |
| System Design for Embodied-Agent Execution in Isaac Sim: Prompt Interfaces, Runtime Validation, and Recovery | Reads like a robotics systems paper and foregrounds recovery. | "System Design" can drift toward a broader framework reading if the abstract is not disciplined. | Robotics-systems relevant, with an execution focus rather than a benchmark focus. |
| Reliable Embodied-Agent Execution in Isaac Sim Through Structured Interfaces and Lightweight Runtime Checks | Compact and practical; highlights the execution-reliability angle. | "Reliable" can sound stronger than the evidence if not bounded to the tested setup. | Applied and readable, but slightly more claim-forward. |

## Current recommendation

The safest two candidates for this draft branch are:

1. `A Controlled Study of Prompt Interface Structure and Runtime Validation for Embodied-Agent Execution in Isaac Sim`
2. `Prompt Interface Structure and Runtime Validation in Isaac Sim: A Controlled Study of Embodied-Agent Execution`
