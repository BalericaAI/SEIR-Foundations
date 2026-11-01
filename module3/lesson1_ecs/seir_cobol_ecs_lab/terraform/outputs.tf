output "ecr_repository_url" {
  description = "Push the lab image here."
  value       = aws_ecr_repository.cobol.repository_url
}

output "cluster_name" {
  description = "ECS cluster that runs the batch task."
  value       = aws_ecs_cluster.lab.name
}

output "task_definition_family" {
  description = "Task definition family registered for the batch job."
  value       = aws_ecs_task_definition.batch.family
}

output "subnet_id" {
  description = "Default-VPC subnet used when running the task."
  value       = data.aws_subnets.default.ids[0]
}

output "security_group_id" {
  description = "No-ingress security group for the task."
  value       = aws_security_group.no_ingress.id
}

output "docker_push_commands" {
  description = "Build and push the image after terraform apply."
  value       = <<-EOT
    aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com
    docker build --platform linux/amd64 -t ${aws_ecr_repository.cobol.repository_url}:${var.image_tag} ..
    docker push ${aws_ecr_repository.cobol.repository_url}:${var.image_tag}
  EOT
}

output "run_task_command" {
  description = "Run the one-shot batch task after the image is pushed."
  value       = <<-EOT
    aws ecs run-task \
      --cluster ${aws_ecs_cluster.lab.name} \
      --launch-type FARGATE \
      --task-definition ${aws_ecs_task_definition.batch.family} \
      --count 1 \
      --network-configuration "awsvpcConfiguration={subnets=[${data.aws_subnets.default.ids[0]}],securityGroups=[${aws_security_group.no_ingress.id}],assignPublicIp=ENABLED}" \
      --region ${var.aws_region}
  EOT
}
