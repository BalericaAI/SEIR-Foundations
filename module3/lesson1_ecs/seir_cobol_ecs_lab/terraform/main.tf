# SEIR Foundations — Module 3 / Lab 01 (Terraform option)
# Provisions the same resources, with the same names, as deploy.sh.
# Choose ONE provisioning path per account: deploy.sh OR Terraform.
# Running both collides on the IAM role, security group, ECR repo, and cluster names.

data "aws_caller_identity" "current" {}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_security_group" "no_ingress" {
  name        = "seir-cobol-no-ingress"
  description = "SEIR COBOL lab outbound only"
  vpc_id      = data.aws_vpc.default.id

  # No ingress blocks: the batch task never listens on a port.
  egress {
    description = "Outbound for ECR image pull and CloudWatch Logs"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_iam_role" "task_execution" {
  name = "seir-ecs-task-execution-lab"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "task_execution" {
  role       = aws_iam_role.task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_ecr_repository" "cobol" {
  name = "seir-cobol-finance"

  image_scanning_configuration {
    scan_on_push = true
  }

  # Lab convenience: terraform destroy removes the repo even if images remain.
  # Do not carry this setting into production registries.
  force_delete = true
}

resource "aws_ecs_cluster" "lab" {
  name = "seir-module3"
}

resource "aws_cloudwatch_log_group" "batch" {
  name              = "/ecs/seir-cobol-batch"
  retention_in_days = var.log_retention_days
}

resource "aws_ecs_task_definition" "batch" {
  family                   = "seir-cobol-batch"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.task_execution.arn

  runtime_platform {
    cpu_architecture        = "X86_64"
    operating_system_family = "LINUX"
  }

  container_definitions = jsonencode([
    {
      name                   = "cobol"
      image                  = "${aws_ecr_repository.cobol.repository_url}:${var.image_tag}"
      essential              = true
      readonlyRootFilesystem = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.batch.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])

  depends_on = [aws_iam_role_policy_attachment.task_execution]
}
