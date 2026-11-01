# Terraform option — COBOL on ECS Fargate lab

This directory provisions the same AWS resources as `../deploy.sh`, with the same names, so the console verification steps in the lab readme apply unchanged:

- ECR repository `seir-cobol-finance` (scan on push)
- ECS cluster `seir-module3`
- Task execution IAM role `seir-ecs-task-execution-lab` with `AmazonECSTaskExecutionRolePolicy`
- CloudWatch log group `/ecs/seir-cobol-batch` (7-day retention)
- Security group `seir-cobol-no-ingress` (no inbound rules, outbound only)
- Fargate task definition `seir-cobol-batch` (256 CPU / 512 MiB, x86-64, read-only root filesystem)

**Choose one provisioning path per account: `deploy.sh` or Terraform, not both.** They create resources with identical names, so whichever runs second fails on the IAM role, security group, ECR repository, and cluster. If you already ran `deploy.sh`, clean up first (lab readme section 7, plus the role and security group) before using Terraform.

## Prerequisites

Everything in the lab readme, plus [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.5. The configuration expects a default VPC in the target Region, same as the script.

## 1. Provision

```bash
cd terraform
terraform init
terraform plan -var aws_region=us-east-1   # Change to your classroom Region
terraform apply -var aws_region=us-east-1
```

Review the plan before approving. State is stored locally in this directory (fine for a single-student lab; use remote state for shared work).

## 2. Build and push the image

The task definition references an image tag that does not exist yet. Push it using the commands Terraform prints:

```bash
terraform output -raw docker_push_commands
```

Run those three commands from this directory (the `docker build` step points at `..`, the lab root).

## 3. Run the batch task

```bash
terraform output -raw run_task_command
```

Run the printed command, then follow the task in the console (ECS → Clusters → `seir-module3` → Tasks, include stopped tasks) or from the CLI:

```bash
aws ecs wait tasks-stopped --cluster seir-module3 --tasks <task-arn> --region us-east-1
aws ecs describe-tasks --cluster seir-module3 --tasks <task-arn> \
  --query 'tasks[0].containers[0].exitCode' --output text --region us-east-1
aws logs tail /ecs/seir-cobol-batch --since 20m --region us-east-1
```

A successful run exits `0` and logs `FINANCIAL INVARIANT PASSED`.

## 4. Clean up

```bash
terraform destroy -var aws_region=us-east-1
```

Unlike the script's manual cleanup, `terraform destroy` also removes the IAM role and the security group it created. The ECR repository is destroyed even if it still contains images (`force_delete = true`, a lab-only convenience). The default VPC is never touched — it is read as a data source, not managed.
