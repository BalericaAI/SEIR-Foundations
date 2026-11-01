# SEIR Foundations — Module 3 / Lab 01
## Install and run COBOL on Amazon ECS Fargate

**Objective:** Move a COBOL batch program from the Module 1 EC2 model to a containerized ECS task. This introductory lab deliberately does **not** require FastAPI, RDS, an Application Load Balancer, or AI agents.

### Architecture

```text
Student laptop / AWS CloudShell with Docker-capable build host
  └─ Docker build (GnuCOBOL compiled in image)
     └─ Amazon ECR: seir-cobol-finance:lab1
        └─ Amazon ECS cluster: seir-module3
           └─ On-demand Fargate task (private process, no listening port)
              └─ stdout → CloudWatch Logs (/ecs/seir-cobol-batch)
```

**EC2 comparison:** On EC2, COBOL executes in an instance OS you administer. On ECS Fargate, AWS provisions the task runtime and runs your **container image**. An ECS *task definition* describes how to launch it; a *task* is an individual execution. This batch job exits when done, so it should **not** be an always-running ECS service (which would continually restart it). Later, a FastAPI/COBOL HTTP adapter can run as a long-lived ECS service.

### Prerequisites

- AWS account with permission to manage ECR, ECS, IAM roles, EC2 security groups, and CloudWatch Logs. Prefer a dedicated classroom sandbox and instructor-provided scoped permissions.
- AWS CLI v2 authenticated (`aws sts get-caller-identity`), Docker with Linux container support, Bash, and outbound network access.
- For Apple Silicon Macs, Docker must support `linux/amd64` cross-platform builds. The sample explicitly builds x86-64 to match the ECS task definition.
- **A default VPC in the target Region**, with a usable internet-routed subnet. The script uses the default VPC for a fast introductory lab, not as a production recommendation.
- AWS charges may apply for Fargate runtime, public IPv4 address, ECR storage, and CloudWatch Logs. Set a budget alert. Do not use real financial/customer data.

### Files

- `hello.cbl` — deterministic sample financial calculation; synthetic figures only.
- `Dockerfile` — multi-stage compilation with GnuCOBOL; unprivileged runtime user.
- `deploy.sh` — creates lab resources, builds/pushes the image, registers a task definition, runs it, and collects results.

Replace `hello.cbl` with the **tested Module 1 source** once the sample works. If Module 1 depended on local files, CICS, a particular COBOL dialect, copybooks, or a database, identify and adapt those dependencies first; a container does not automatically provide them.

### 1. Extract the bundle and check the tools

```bash
unzip seir_cobol_ecs_lab.zip
cd seir_cobol_ecs_lab
aws --version
docker --version
aws sts get-caller-identity
aws ec2 describe-vpcs --filters Name=isDefault,Values=true --query 'Vpcs[0].VpcId' --output text
```

The final command must return a VPC ID, not `None`. Windows users should use WSL2 with Docker Desktop integration, or a prepared Linux build host. AWS CloudShell does not universally provide a suitable running Docker daemon; do not assume it does.

### 2. Test locally before deploying

```bash
docker build --platform linux/amd64 -t seir-cobol-finance:lab1 .
docker run --rm --platform linux/amd64 seir-cobol-finance:lab1
```

Expected lines include:

```text
SEIR COBOL FINANCIAL BATCH v1
Opening: USD 0012500.00
Debit:   USD 0000250.00
Closing: USD 0012250.00
FINANCIAL INVARIANT PASSED
```

The process exit code must be `0`. If it exits nonzero, **do not deploy**. This is an illustrative fixed-value calculation, not yet a transaction processing system.

### 3. Deploy to ECS

Two provisioning options create the same AWS resources with the same names. **Pick one per account — they collide if you run both.**

- **Option A — script (this section):** `deploy.sh` provisions, builds, pushes, runs the task, and collects results in one pass.
- **Option B — Terraform:** the [`terraform/`](terraform/README.md) directory provisions the same infrastructure declaratively, with `terraform destroy` as a complete cleanup. The image build/push and `run-task` steps stay on the CLI; Terraform prints the exact commands as outputs.

The script creates/uses an ECR repository, an ECS cluster, an ECS task execution IAM role, a CloudWatch log group, and a security group with **no inbound permissions**. It selects a subnet in the default VPC and assigns a public IPv4 address **only for outbound image pull and logging in this beginner batch lab**; the container does not expose an inbound port. This is not the design for the later banking services.

```bash
export AWS_REGION=us-east-1   # Change to your classroom Region
chmod +x deploy.sh
./deploy.sh
```

The script will print the ECS task ARN, its exit code, the stopped reason, and recent CloudWatch logs. A successful run has an ECS container exit code of `0` and prints `FINANCIAL INVARIANT PASSED`.

**Important:** The script assumes a standard default VPC with working outbound routing. If the selected subnet lacks internet access, the task may fail to pull its image or send logs. In a production-style private subnet, use NAT and/or correctly configured VPC endpoints for ECR, S3, and CloudWatch Logs. If IAM role creation is restricted, the instructor should pre-create the role and attach `AmazonECSTaskExecutionRolePolicy`.

### 4. Verify in the AWS Console

1. **ECR → Private repositories → `seir-cobol-finance`**: confirm the `lab1` image.
2. **ECS → Clusters → `seir-module3` → Tasks**: include stopped tasks, inspect the task, exit code, and task definition.
3. **CloudWatch → Log groups → `/ecs/seir-cobol-batch`**: open the latest stream and inspect the calculation and invariant.
4. **EC2 → Security Groups → `seir-cobol-no-ingress`**: verify there are no inbound rules.

### 5. Failure exercises

- **Compile failure:** Introduce a COBOL syntax error; the Docker build must fail before any deployment.
- **Financial invariant failure:** Change the expected closing balance. The task must exit nonzero and reveal the failure in CloudWatch.
- **Bad image tag:** Register a task referencing a nonexistent ECR tag. Observe the pull failure and distinguish it from a COBOL runtime defect.
- **IAM or networking failure:** In an isolated instructor sandbox, remove the image-pull permission or outbound access, run the task, inspect its stopped reason, and restore the original configuration.

Use branches or isolated student environments for destructive tests. Never deliberately break shared infrastructure.

### 6. Next labs

1. Convert the batch logic into a callable COBOL financial service with a small HTTP adapter.
2. Run the adapter as a persistent **ECS service**, without public ingress.
3. Add a separate FastAPI ECS service and private service discovery.
4. Add PostgreSQL/RDS and implement atomic ledger transactions, idempotency and reconciliation.
5. Migrate the build and deployment steps into GitHub Actions with pull-request quality gates and Terraform-managed infrastructure (the [`terraform/`](terraform/README.md) option in this lab is the first step).
6. Add read-only AI investigation agents on ECS and compare with Bedrock AgentCore.

### 7. Cleanup

If you provisioned with Terraform (Option B), run `terraform destroy` from the `terraform/` directory instead of the commands below.

Only remove these resources when they belong exclusively to **your** lab. The commands below deliberately do **not** delete the IAM role or shared default VPC. Do not run them against shared class infrastructure.

```bash
export AWS_REGION=us-east-1
aws ecs delete-cluster --cluster seir-module3 --region "$AWS_REGION"
aws ecr delete-repository --repository-name seir-cobol-finance --force --region "$AWS_REGION"
aws logs delete-log-group --log-group-name /ecs/seir-cobol-batch --region "$AWS_REGION"
```

If the ECS cluster contains other tasks or services, **do not delete it**. For full teardown, inspect and remove the created security group and execution role only after verifying that neither is used elsewhere. Avoid broadly deleting IAM resources through automated classroom cleanup.

### Authoritative references

- [Amazon ECS — Creating a container image](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/create-container-image.html)
- [Amazon ECR — Image lifecycle](https://docs.aws.amazon.com/AmazonECR/latest/userguide/getting-started-cli.html)
- [Amazon ECS — Task execution IAM role](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_execution_IAM_role.html)
- [GnuCOBOL compiler reference](https://manpages.debian.org/unstable/gnucobol/cobc.1.en.html)
