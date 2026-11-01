# Pipeline configuration — Terraform checks with GitHub Actions

This lab ships a starter CI pipeline in [`.github/workflows/terraform-checks.yml`](../../../.github/workflows/terraform-checks.yml) at the repository root. It runs **simple Terraform checks only** — formatting, initialization, and validation. No cloud credentials are required, nothing is deployed, and no AWS charges are possible from this pipeline. A Snyk security-scanning stage will be added later in the course; a commented placeholder in the workflow marks where it goes.

## Coming from Jenkins

Most of you already run Jenkins pipelines. The concepts map almost one-to-one; the main differences are that GitHub Actions has no controller or agents to administer (GitHub provides ephemeral runners), and the pipeline definition lives in `.github/workflows/` instead of a `Jenkinsfile`.

| Jenkins | GitHub Actions equivalent in this pipeline |
|---|---|
| `Jenkinsfile` (declarative pipeline) | `.github/workflows/terraform-checks.yml` |
| `pipeline { }` block | The workflow file itself (`name: terraform-checks`) |
| `agent { label 'linux' }` | `runs-on: ubuntu-latest` (ephemeral GitHub-hosted runner) |
| Webhook / SCM polling triggers | `on:` block — `pull_request`, `push`, `workflow_dispatch` |
| `stage('Validate')` | A `job` (here: `terraform-checks`); its `steps` are the equivalent of stage steps |
| `steps { sh 'terraform fmt' }` | `- run: terraform fmt -check -recursive -diff` |
| Global Tool Configuration (Terraform installer) | `hashicorp/setup-terraform@v3` action with a pinned `terraform_version` |
| `dir('terraform') { ... }` | `defaults.run.working-directory` |
| `environment { }` / `credentials()` | `env:` / `${{ secrets.NAME }}` (none needed yet — that arrives with Snyk) |
| `post { always { ... } }` | A step with `if: always()` |
| Shared libraries | Marketplace actions and reusable workflows |
| Blue Ocean / console output | The repository's **Actions** tab |
| "Build Now" button | `workflow_dispatch` (Run workflow button in the Actions tab) |

## What the pipeline does

```text
Trigger: PR or push to main that touches the lab's terraform/ directory
         (or the workflow file itself), plus manual runs
  └─ Job: terraform-checks  (ubuntu-latest runner)
     ├─ actions/checkout@v4          clone the repository
     ├─ hashicorp/setup-terraform@v3 install Terraform 1.9.8
     ├─ terraform fmt -check         fail on unformatted code (shows the diff)
     ├─ terraform init -backend=false download providers; skip state backend
     └─ terraform validate           type-check the configuration
```

Step-by-step:

1. **Triggers (`on:`).** The pipeline runs on pull requests and on pushes to `main`, but **only** when files under `module3/lesson1_ecs/seir_cobol_ecs_lab/terraform/` (or the workflow itself) change — the `paths:` filter is the Actions equivalent of "poll SCM with an include pattern". `workflow_dispatch` adds a manual run button.
2. **Least privilege (`permissions:`).** `contents: read` is all this pipeline needs. Start restrictive and widen only when a step demands it — the same discipline you apply to Jenkins credentials.
3. **`terraform fmt -check -recursive -diff`.** Fails the build if any `.tf` file is not canonically formatted and prints the diff. Fix locally with `terraform fmt -recursive` and push again.
4. **`terraform init -backend=false -input=false`.** Downloads the AWS provider pinned by `.terraform.lock.hcl`. `-backend=false` skips state configuration, so the runner needs **no AWS credentials** — this is a static check, not a deployment.
5. **`terraform validate`.** Confirms the configuration is internally consistent: resource arguments exist, references resolve, types match. It does not contact AWS and cannot catch account-level problems (missing default VPC, IAM permissions) — those surface at `terraform plan`/`apply` time, which stays on your workstation in this lab.

## Reconfiguring the sample

You will adapt this file in later labs; it is deliberately small. Common edits:

- **Point it at your own repository layout:** change the two `paths:` entries and `defaults.run.working-directory` if your Terraform lives elsewhere. If you are working from the lab zip bundle, the sample is included as `github_workflows/terraform-checks.yml`; copy it to `.github/workflows/` in your **repository root** — GitHub does not discover workflows anywhere else.
- **Add a plan stage (optional, later):** a `terraform plan` step requires AWS credentials. Use GitHub's OpenID Connect integration with a scoped IAM role rather than long-lived keys in secrets; this is covered when the course moves deployment into the pipeline.
- **Add the Snyk stage (later in the course):** it will be a second `job` under `jobs:`, authenticated with a `SNYK_TOKEN` repository secret (**Settings → Secrets and variables → Actions**). The commented placeholder at the bottom of the workflow marks the spot. Do not add it yet.
- **Branch protection (instructor-recommended):** in **Settings → Branches**, require the `Terraform format and validate` check to pass before merging to `main`. This is the Actions equivalent of a Jenkins merge gate.

## Watching it run

1. Open the repository's **Actions** tab and select **terraform-checks**.
2. Each run shows the job, its steps, and per-step console output — the same information you read in a Jenkins build console, already split by step.
3. A red ✗ on `terraform fmt` is the most common failure: run `terraform fmt -recursive` in `module3/lesson1_ecs/seir_cobol_ecs_lab/terraform/` locally, commit, and push.

## Failure exercises

- Break the formatting (indent a line in `main.tf` with a tab), push to a branch, open a PR, and read the `fmt` diff in the failed check. Revert.
- Introduce a typo in a resource argument (`familyy = ...`) and observe `terraform validate` fail with the exact file and line. Revert.
- Note what this pipeline **cannot** catch: it validated happily while your AWS account had no default VPC. Static checks complement, never replace, a reviewed `terraform plan`.
