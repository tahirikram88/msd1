# Case Study 2 — Live Demo Script

## Opening
"This automation is a self-healing nightly control. It finds oversized buckets without lifecycle policy, respects an exemption tag, and safely applies a standard policy."

## Code walkthrough
"The first thing I want to show is that this is not a toy script. It handles existing lifecycle configurations, missing tags, missing CloudWatch metric datapoints, DRY_RUN mode, and bucket-by-bucket exception handling."

## Scale point
"At moderate scale, one Lambda is fine. If we start approaching Lambda duration limits, I would split inventory and fan out with Step Functions or SQS plus worker Lambdas."

## IAM point
"I also avoided broad policies like AmazonS3FullAccess. The role has only the list, get-tagging, get-lifecycle, put-lifecycle, CloudWatch read, and log write permissions it actually needs."
