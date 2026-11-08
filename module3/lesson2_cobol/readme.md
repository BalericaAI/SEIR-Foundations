# Module 3 — Lesson 2: From one-shot batch task to an always-on COBOL service

Lab 02 ([`seir_lab02_cobol_ecs/`](seir_lab02_cobol_ecs/README.md)) turns the Lab 01 idea — run COBOL once as an ECS Fargate **task** — into a COBOL-backed HTTP application managed as an ECS **service**: two tasks in private subnets behind an Application Load Balancer.

It is easy to forget where Lab 01 left off, so use this checkpoint before starting.

## Checkpoint — what you should already have done in Lab 01

By the end of Module 3 / Lab 01 ([`../lesson1_ecs/seir_cobol_ecs_lab/`](../lesson1_ecs/seir_cobol_ecs_lab/readme.md)) you should have:

1. **Built and run the COBOL image locally.** `docker build --platform linux/amd64` succeeded, and `docker run` printed `FINANCIAL INVARIANT PASSED` with exit code `0`.
2. **Pushed the image to Amazon ECR** as `seir-cobol-finance:lab1`.
3. **Provisioned the lab infrastructure** with **one** of the two options:
   - Option A: `deploy.sh`, or
   - Option B: `terraform apply` in the lab's `terraform/` directory.
   Either way, that created the ECS cluster `seir-module3`, the task definition family `seir-cobol-batch`, the execution role `seir-ecs-task-execution-lab`, the no-ingress security group `seir-cobol-no-ingress`, and the log group `/ecs/seir-cobol-batch`.
4. **Ran the one-shot Fargate task** and confirmed an ECS container exit code of `0`.
5. **Read the result in CloudWatch Logs** (`/ecs/seir-cobol-batch`), including `FINANCIAL INVARIANT PASSED`.
6. **Cleaned up** (Lab 01 section 7, or `terraform destroy` for Option B).

If any of these steps is unfamiliar, go back and finish Lab 01 first — Lab 02 assumes you can already build, push, and launch a container on Fargate without guidance.

## Do Lab 01 resources need to still exist? No.

**Lab 02 does not reuse anything Lab 01 created in AWS.** It deploys its own CloudFormation stack with a new VPC, cluster, ECR repository, ALB, and IAM role. If you already cleaned up Lab 01, you are exactly where you should be. If you are not sure whether you cleaned up, check:

```bash
export AWS_REGION=us-east-1   # your classroom Region
aws ecs describe-clusters --clusters seir-module3 \
  --query 'clusters[0].status' --output text --region "$AWS_REGION"
aws ecr describe-repositories --repository-names seir-cobol-finance \
  --query 'repositories[0].repositoryName' --output text --region "$AWS_REGION"
```

`INACTIVE`, `None`, or a `RepositoryNotFoundException` means Lab 01 is cleaned up. If the cluster is still `ACTIVE` or the repository still exists, finish Lab 01 cleanup before continuing — leftover ECR images and logs are cheap but not free, and a tidy account makes Lab 02's new resources much easier to recognize.

## What does carry over from Lab 01

- **Your tools:** an authenticated AWS CLI v2 (`aws sts get-caller-identity`), Docker with `linux/amd64` build support, and Bash.
- **Your mental model:** a *task definition* describes how to launch a container; a *task* is one execution. Lab 01 used `run-task` because a batch job exits when done. Lab 02 introduces a *service*, which keeps a desired count of tasks running and replaces them when they fail — that contrast is the core lesson.
- **The COBOL-in-a-container pattern:** multi-stage GnuCOBOL compile, unprivileged user, read-only root filesystem, logs to CloudWatch.

Note that Lab 02 needs **more IAM permissions** than Lab 01 (CloudFormation, VPC networking, NAT gateway, ALB) and creates resources with ongoing hourly charges — read its cost warning before deploying.

## Start Lab 02

Continue to [`seir_lab02_cobol_ecs/README.md`](seir_lab02_cobol_ecs/README.md).
