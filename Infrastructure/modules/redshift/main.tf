resource "aws_security_group" "redshift_sg" {
  name        = "${var.project_name}-redshift-sg"
  description = "Egress-only security group for Redshift Serverless"
  vpc_id      = var.vpc_id

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-redshift-sg"
  }
}

resource "aws_redshiftserverless_namespace" "this" {
  namespace_name = var.namespace_name
  admin_username = var.admin_username
  admin_user_password = var.admin_password
  db_name = var.db_name

  iam_roles = [var.iam_role_arn]
}

resource "aws_redshiftserverless_workgroup" "this" {
  workgroup_name = var.workgroup_name
  namespace_name = aws_redshiftserverless_namespace.this.namespace_name
  base_capacity  = var.base_capacity

  publicly_accessible = false
  subnet_ids          = var.subnet_ids
  security_group_ids  = [aws_security_group.redshift_sg.id]
}