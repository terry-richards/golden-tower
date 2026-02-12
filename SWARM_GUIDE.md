# How to Launch the Golden Tower Agent Swarm

## Swarm Entry Prompt

When entering Claude swarm mode, use this prompt:

---

```
You are the orchestrator of a zero-human autonomous design shop building the
"Golden Tower" — a modular, 3D-printable hydroponic grow tower where planting
pockets spiral upward following the golden angle (137.508°).

Read these files IN ORDER before doing anything else:
1. .copilot-instructions.md — Full product spec, constraints, and protocols
2. AGENTS.md — Agent roles, handoff protocol, and iteration flow
3. tower_params.py — Current parametric dimensions (single source of truth)
4. CHANGELOG.md — Iteration history and current state
5. reports/iteration_summary.md — Current scores and open issues

You have 5 agents: orchestrator (you), architect, engineer, printer, aesthetician.

KEY DESIGN DECISIONS already made — do not revisit:
- The central supply tube is INTEGRATED into each segment (no separate tube part)
- Each segment has an INTEGRATED drip tray / catch plate for overflow
- The 3 pockets per segment spiral UPWARD at different heights (not a flat ring)
- Segment height:width ratio ≥ 1.0 (currently 1.25) for visible upward sweep
- The outer body between pockets is CLEAN — no accessory notches or grip features
- Pocket protrusions extending beyond the outer cylinder are expected and integral
- The architect has hydroponic systems expertise (NFT, root zone, drainage, etc.)

Begin Iteration 1: hand off to the architect to generate the first complete
parametric geometry for all components (standard segment with integrated tube
and drip tray, top cap, bottom segment with QD fitting, interlock mechanism)
using build123d. The architect should study the reference STL
(3-Way_Planting_Module_custom.stl) to understand the integrated tube and drip
tray geometry before designing.

After geometry exists, run the engineering, print, and aesthetic reviews in
parallel, then score and decide whether to iterate or promote.

Work autonomously. Do not ask for human input. Iterate until the weighted score
reaches 7.5/10 with no category below 6, or until you hit 12 iterations.
Commit and push to GitHub after every iteration.

The workspace is at /home/tmr/src/learn/golden-tower/ with build123d installed
in ./venv/. Run `source venv/bin/activate` before any Python commands.
The GitHub repo is https://github.com/terry-richards/golden-tower (remote: origin).
```

---

## How the Instructions Are Structured (Design Rationale)

### Layered information architecture

The instructions use a **top-down** structure that mirrors how an agent (or a
new engineer) would onboard:

| Layer | File | Purpose |
|-------|------|---------|
| **Mission** | `.copilot-instructions.md` §1 | Why we exist — one paragraph |
| **What to build** | `.copilot-instructions.md` §2 | Product spec with exact numbers |
| **How to build it** | `.copilot-instructions.md` §3, §9 | Tech stack and code patterns |
| **Who does what** | `AGENTS.md` | Role definitions with clear boundaries |
| **How to iterate** | `.copilot-instructions.md` §6 | Cycle, rules, scoring rubric |
| **When to stop** | `.copilot-instructions.md` §7 | Promotion criteria and deliverables |
| **Current state** | `CHANGELOG.md`, `reports/` | Living documents updated each iteration |

### Why this structure works for agent swarms

1. **Single source of truth**: `tower_params.py` is the only place dimensions
   live. Agents can't drift out of sync because they all import from one file.

2. **Explicit scoring rubric**: Agents need unambiguous success criteria. The
   weighted rubric (§6.3) with a hard promotion threshold (7.5/10, no category
   below 6) gives the orchestrator a mechanical decision process — no judgment
   calls needed.

3. **File-based communication**: Agents communicate through the repository, not
   through conversation. This makes the state inspectable, versionable, and
   recoverable if any agent fails mid-iteration.

4. **Bounded autonomy**: Maximum 12 iterations prevents runaway loops. Each
   agent has a clear scope (architect doesn't review prints; printer doesn't
   redesign geometry). The orchestrator is the only one that makes cross-cutting
   decisions.

5. **Automated quality gates**: The pytest test suite catches parametric
   violations immediately. An agent can't break the golden angle or exceed the
   build volume without tests failing.

6. **Stub architecture**: Every component file exists with `NotImplementedError`
   stubs. The architect knows exactly what functions to implement and what the
   expected interface is. No ambiguity about file locations or function signatures.

### Key prompt engineering patterns used

- **Persona + scope**: Each agent instruction starts with "You are the X Agent"
  and explicitly lists responsibilities and non-responsibilities.
- **Concrete over abstract**: Instead of "make it printable," the instructions
  say "overhangs ≤ 55° from vertical, bridges ≤ 40mm."
- **Severity taxonomy**: BLOCKER / MAJOR / MINOR gives agents a shared language
  for prioritization without requiring nuanced judgment.
- **Exit conditions**: "Score ≥ 7.5 with no category below 6" is a bright line,
  not a fuzzy guideline.
- **Recovery procedures**: §11 tells agents what to do when things break,
  rather than leaving them stuck.

## Tips for Running the Swarm

1. **Repo is ready**: The repo is initialized and connected to GitHub at
   https://github.com/terry-richards/golden-tower. The swarm pushes
   after every iteration commit: `git push origin main`.

2. **Monitor the changelog**: `CHANGELOG.md` is the human-readable audit trail.
   Check it to see what the swarm decided at each iteration.

3. **Intervene via reports**: If you want to nudge the swarm, edit
   `reports/iteration_summary.md` and add a BLOCKER issue. The orchestrator
   will route it to the appropriate agent.

4. **Adjust parameters**: If the swarm converges on something you don't like,
   modify `tower_params.py` directly and reset the iteration counter.

5. **Scale up**: To add more agents (e.g., a "botanist" that optimizes pocket
   angles for specific plants), add a new section to `AGENTS.md` and reference
   it from the orchestrator's handoff list.
