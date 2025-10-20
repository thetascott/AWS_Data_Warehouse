locals {
  bronze_arn = "arn:aws:s3:::${var.bronze_bucket}"
  silver_arn = "arn:aws:s3:::${var.silver_bucket}"
  scripts_arn = "arn:aws:s3:::${var.scripts_bucket}"
}

##############################
# Glue Role
##############################
resource "aws_iam_role" "glue" {
  name               = "glue-data-lake-role"
  assume_role_policy = data.aws_iam_policy_document.glue_assume_role.json
}

data "aws_iam_policy_document" "glue_assume_role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["glue.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_policy" "glue_s3_policy" {
  name        = "glue-s3-access"
  description = "Allow Glue to read bronze and write silver"
  policy      = data.aws_iam_policy_document.glue_s3.json
}

data "aws_iam_policy_document" "glue_s3" {
  statement {
    actions   = ["s3:GetObject", "s3:ListBucket"]
    resources = [local.bronze_arn, "${local.bronze_arn}/*"]
  }

  statement {
    actions = [
    "s3:ListBucket",
    "s3:GetObject",
    "s3:PutObject",
    "s3:DeleteObject"
    ]
    resources = [local.silver_arn, "${local.silver_arn}/*"]
  }

  statement {
    actions = [
    "s3:ListBucket",
    "s3:GetObject"
    ]
    resources = [local.scripts_arn, "${local.scripts_arn}/*"]
  }

  statement {
    actions   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy_attachment" "glue_s3_attach" {
  role       = aws_iam_role.glue.name
  policy_arn = aws_iam_policy.glue_s3_policy.arn
}

resource "aws_iam_role_policy" "glue_catalog_access" {
  name = "glue-catalog-access"
  role = aws_iam_role.glue.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "glue:GetDatabase",
          "glue:GetDatabases",
          "glue:CreateTable",
          "glue:GetTable",
          "glue:GetTables",
          "glue:UpdateTable",
          "glue:DeleteTable",
          "glue:GetPartition",
          "glue:GetPartitions",
          "glue:CreatePartition",
          "glue:UpdatePartition",
          "glue:DeletePartition"
        ]
        Resource = "*"
      }
    ]
  })
}

##############################
# Redshift Role
##############################
resource "aws_iam_role" "redshift" {
  name               = "redshift-data-lake-role"
  assume_role_policy = data.aws_iam_policy_document.redshift_assume_role.json
}

data "aws_iam_policy_document" "redshift_assume_role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["redshift.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_policy" "redshift_serverless_policy" {
  name        = "redshift-serverless-access"
  description = "Allow Redshift serverless access"
  policy      = data.aws_iam_policy_document.redshift_serverless.json
}

data "aws_iam_policy_document" "redshift_serverless" {
  statement {
    actions   = [
      "s3:GetObject",
      "s3:ListBucket"
    ]
    resources = [local.silver_arn, "${local.silver_arn}/*"]
  }

  statement {
    actions = [
      "glue:GetDatabase",
      "glue:GetDatabases",
      "glue:GetTable",
      "glue:GetTables",
      "glue:GetPartition",
      "glue:GetPartitions"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy_attachment" "redshift_s3_attach" {
  role       = aws_iam_role.redshift.name
  policy_arn = aws_iam_policy.redshift_serverless_policy.arn
}

##############################
# Lambda Role
##############################
resource "aws_iam_role" "lambda" {
  name               = "lambda-data-lake-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_policy" "lambda_s3_policy" {
  name        = "lambda-s3-access"
  description = "Allow Lambda to read/write bronze and silver"
  policy      = data.aws_iam_policy_document.lambda_s3.json
}

data "aws_iam_policy_document" "lambda_s3" {
  statement {
    actions   = ["s3:GetObject", "s3:ListBucket", "s3:PutObject"]
    resources = [
      local.bronze_arn, "${local.bronze_arn}/*",
      local.silver_arn, "${local.silver_arn}/*"
    ]
  }

  statement {
    actions   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy_attachment" "lambda_s3_attach" {
  role       = aws_iam_role.lambda.name
  policy_arn = aws_iam_policy.lambda_s3_policy.arn
}