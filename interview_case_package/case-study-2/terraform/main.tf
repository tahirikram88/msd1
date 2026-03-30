terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/s3-lifecycle-enforcer"
  retention_in_days = 14
}

resource "aws_iam_role" "lambda_role" {
  name = "s3-lifecycle-enforcer-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_lambda_function" "enforcer" {
  function_name    = "s3-lifecycle-enforcer"
  role             = aws_iam_role.lambda_role.arn
  handler          = "main.lambda_handler"
  runtime          = "python3.11"
  timeout          = 300
  filename         = var.lambda_zip_path
  source_code_hash = filebase64sha256(var.lambda_zip_path)

  environment {
    variables = {
      DRY_RUN           = "true"
      LOG_TIMEZONE      = var.timezone
      SIZE_THRESHOLD_GB = "100"
    }
  }

  depends_on = [aws_cloudwatch_log_group.lambda]
}

resource "aws_scheduler_schedule" "nightly" {
  name                         = "s3-lifecycle-enforcer-nightly"
  group_name                   = "default"
  schedule_expression          = "cron(0 2 * * ? *)"
  schedule_expression_timezone = var.timezone
  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = aws_lambda_function.enforcer.arn
    role_arn = aws_iam_role.scheduler_role.arn
    input    = jsonencode({ source = "eventbridge-scheduler" })
  }
}

resource "aws_iam_role" "scheduler_role" {
  name = "s3-lifecycle-enforcer-scheduler-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = { Service = "scheduler.amazonaws.com" },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "scheduler_invoke_lambda" {
  name = "scheduler-invoke-lambda"
  role = aws_iam_role.scheduler_role.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = ["lambda:InvokeFunction"],
      Resource = aws_lambda_function.enforcer.arn
    }]
  })
}
