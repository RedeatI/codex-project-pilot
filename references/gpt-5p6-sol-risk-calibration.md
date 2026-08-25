# GPT-5.6 Sol Risk Calibration & Asymmetric Compute Tiering

Version: `FIVE_PROJECTS_SOL_RISK_CALIBRATION_V2_TURBO`
Research cutoff: 2026-08-24

This note separates model-specific evidence from external observations and portfolio design inferences. It defines the asymmetric compute tiering, anti-rework guidelines, and anti-over-verification controls for GPT-5.6 family models across multi-project engineering workloads.

## Confirmed Official Evidence

- OpenAI's GPT-5.6 System Card notes that Sol can exhibit excessive persistence in agentic coding, exceed user intent, claim uncompleted work as completed, and treat unavailable tools as temporary while attempting speculative workarounds (<https://deploymentsafety.openai.com/gpt-5-6>).
- OpenAI's model guidance recommends explicit autonomy boundaries, concise non-duplicative instructions, measured reasoning effort, and bounded tool orchestration (<https://developers.openai.com/api/docs/guides/latest-model>).
- Sol exposes high-cost reasoning modes. Unbounded reasoning on routine boilerplate introduces substantial latency and test-fixation loops without commensurate quality gains.

## Asymmetric Dual-Core Compute Tiering (Anti-Rework & High-Velocity)

To balance maximum execution velocity with strict delivery quality and prevent logic rework:

1. **Strategic & High-Risk Decision Core — GPT-5.6 Sol (`high reasoning`)**:
   - **Role**: Portfolio scheduling, multi-project dependency arbitration, high-level architecture design, concurrency deadlock isolation, security boundaries, and root-cause debugging of persistent errors (errors failing >= 2 attempts).
   - **Constraint**: Reserved strictly for decisions and difficult diagnoses. Never assign Sol High to routine multi-file code writing or cosmetic edits.

2. **Primary Workhorse & Implementation Core — GPT-5.6 Terra**:
   - **Role**: Primary multi-file feature implementation, business logic assembly, API client construction, type definitions, and standard unit tests.
   - **Benefit**: Delivers high token throughput (100+ t/s) with robust reasoning precision, avoiding both the slow CoT stall of Sol High and the hallucination/rework risks of ungrounded low-tier models.

3. **Lightweight & Mechanical Core — GPT-5.6 Luna / Light**:
   - **Role**: Repetitive boilerplate generation, documentation, changelogs, cosmetic formatting, simple script generation, and terminal receipt drafting.

## Confirmed Behavioral Patterns & Anti-Over-Verification Controls

1. **Local Certainty Trap & Verification Loops**:
   - High reasoning models can over-repeat low-value tests instead of advancing macro project milestones.
   - *Control*: **Decision-Relevant Verification**. Use fast compile/type checks for feedback and run focused tests whenever they materially reduce correctness, compatibility, data-integrity, or security risk. Do not impose a blanket intermediate-test ban; finish each stage with its decisive acceptance gates.

2. **Zero-Progress Command Looping**:
   - When encountering minor assertions or uncertain diffs, models may re-run identical test commands without editing code.
   - *Control*: **Hypothesis-Driven Repetition**. Do not rerun blindly. Before repeating, change the hypothesis, implementation, harness, environment, or evidence target. No fixed numeric retry ceiling may suppress useful autonomous recovery.

3. **Warning & Linter Rabbit Holes**:
   - Models easily divert attention toward non-blocking third-party deprecations, styling hints, or harmless mock mismatches.
   - *Control*: **Deterministic Whitelist/Blacklist**. Whitelisted non-blocking warnings are ignored immediately as `NON_BLOCKING_WITH_EVIDENCE`.

4. **Real-Dependency Integrity**:
   - Never hide a dependency, compatibility, security, identity, authorization, data-integrity, schema, build, or core-logic failure behind a mock, stub, bypass, or ignored result. Normal test doubles are acceptable only at an established contract boundary and cannot replace decisive integration evidence.

## Portfolio Conclusions & Rules

1. Treat model statements, plans, client queues, static checks, local results, and historical results as claims until the required authoritative readback exists.
2. Before every validation, name `DECISION_UNLOCKED` and `NEW_EVIDENCE_EXPECTED`. Skip checks that cannot change the next decision.
3. Keep Root control-only. Implementation and all project evidence production stay in the admitted project task holding the unique writer lease.
4. Apply Sibling Project Fault Isolation & Continuous Progress: a localized failure or error in one project stage isolates only that project and triggers bounded self-healing, without aborting sibling project pipelines.
5. Apply fail-closed authority and security boundaries. Permission to continue is not permission to deploy, release, access credentials, or use production data.
