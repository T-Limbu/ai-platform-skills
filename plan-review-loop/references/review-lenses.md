# Review lenses

Each pass uses one lens: a kind of evidence, plus the questions to ask of it. Pick the lens that opens a source no earlier pass used. Skip questions that don't apply to the plan.

## 1. Repo

**Sources:** source code, CI workflow files, build and test scripts, package manifests, test folders, the repo's `docs/` and `AGENTS.md`.

- What tests exist, per suite (unit, integration, e2e, rules, backend)? Which run in CI, which only by hand, which never?
- Does each suite still start? Run it once: stale ports, paths and configs are common.
- How many times does each check run per change? Look for build scripts that run the tests again.
- What does the deploy workflow do after it triggers the deploy? Does anything wait for the deploy, or check the result?
- What is tracked in git that a test run rewrites?
- Where is the largest untested code, and what does it do?

**Typical findings:** suites that never run, tests run several times, e2e broken by a port change, no check after a deploy.

## 2. Platform

**Sources:** current vendor docs (fetched, not recalled), plan and tier pages, the Git host's API responses.

- Can the controls the plan relies on actually be enabled on this plan or tier (branch protection, required checks, environment reviewers)? Call the API and read the error.
- What does the hosting platform build and run itself, versus what CI builds? Which artifact really ships?
- Which variables, statuses and endpoints does the platform document (for example a commit SHA at build time, deploy status values)? Quote the doc and its URL.
- Do free tiers sleep, throttle or cap anything the plan depends on?
- Is the runtime version pinned anywhere, and is it the same in CI and on the host?

**Typical findings:** a gate that can't be enforced on the current plan; the CI artifact isn't what ships; unpinned runtimes.

## 3. Live config

**Sources:** hosting service settings (API or dashboard, read-only), the project's cloud config, secrets lists (names only), the issue tracker.

- Do the live settings match the repo's config files (branch, build command, environment, region)?
- Is the service actually managed by the repo's infra-as-code file, or was it created by hand?
- Which manual paths exist (deploy buttons, console edits) that skip the pipeline? Can they be disabled?
- Do qa and prod share anything they shouldn't (database, auth project, storage, quotas, keys)?
- Which environments, secrets and variables exist, compared with what the plan assumes?

**Typical findings:** a service tracking a stale branch; config files nobody syncs; a manual deploy that skips every gate; qa and prod sharing data.

## 4. Flow

**Sources:** the plan itself, read against the facts verified so far, plus the other repos the plan touches.

- Which steps depend on others? Can a later phase actually start, or is it blocked by an earlier fix (for example a runner bug blocking a browser test)?
- Which shared components (reusable workflows, packages, shared config) affect other apps? Release them as new versions instead of changing existing ones in place.
- Does any step change something another open ticket or pull request also changes? Link it, don't duplicate it.
- Is each phase small enough for one session and one pull request?

**Typical findings:** hidden order between phases, cross-app impact, overlap with existing tickets.

## 5. Failure and bypass

**Sources:** the plan's gates and checks, each traced end to end.

- If this check fails, what stops? If it's skipped or times out, what then?
- Can two runs overlap and record a result against the wrong version?
- Is there an emergency override, who can use it, and is its use recorded?
- Will flaky checks be hidden by retries, or reported?
- What does a check depend on that could change under it (selectors, CSS classes, test data, network)?
- Does the check run where users actually are (real phones, the real sign-in path), or only where it's easy?

**Typical findings:** no concurrency control, no override, hidden flakiness, fragile selectors, checks that can't see phone-only behaviour.

## Final: critical and high only

**Sources:** a fresh-context reviewer, given the plan and the ledger but no conversation, plus one more look at live config.

- Report only critical and high findings (SKILL.md, Severity). Anything else goes to the build.
- Re-check the assumption the whole plan depends on most (usually "this gate really blocks").
- An empty result is a valid outcome. Say so, and stop.
