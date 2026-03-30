variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "lambda_zip_path" {
  type = string
}

variable "timezone" {
  type    = string
  default = "America/New_York"
}
