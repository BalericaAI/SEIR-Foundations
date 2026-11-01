variable "aws_region" {
  description = "Classroom AWS Region."
  type        = string
  default     = "us-east-1"
}

variable "image_tag" {
  description = "Tag of the COBOL image pushed to ECR."
  type        = string
  default     = "lab1"
}

variable "log_retention_days" {
  description = "CloudWatch Logs retention for the lab log group."
  type        = number
  default     = 7
}
