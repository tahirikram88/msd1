resource "aws_iam_role_policy" "lambda_policy" {
  name = "s3-lifecycle-enforcer-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid    = "S3ListBuckets",
        Effect = "Allow",
        Action = [
          "s3:ListAllMyBuckets"
        ],
        Resource = "*"
      },
      {
        Sid    = "S3BucketInspectionAndLifecycle",
        Effect = "Allow",
        Action = [
          "s3:GetBucketTagging",
          "s3:GetLifecycleConfiguration",
          "s3:PutLifecycleConfiguration"
        ],
        Resource = "arn:aws:s3:::*"
      },
      {
        Sid    = "CloudWatchReadBucketMetrics",
        Effect = "Allow",
        Action = [
          "cloudwatch:GetMetricStatistics"
        ],
        Resource = "*"
      },
      {
        Sid    = "WriteLambdaLogs",
        Effect = "Allow",
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "${aws_cloudwatch_log_group.lambda.arn}:*"
      }
    ]
  })
}
