output "redshift_sg_id" {
  description = "Security group ID for Redshift"
  value       = aws_security_group.redshift_sg.id
}

output "namespace_name" {
  value = aws_redshiftserverless_namespace.this.namespace_name
}

output "workgroup_name" {
  value = aws_redshiftserverless_workgroup.this.workgroup_name
}

output "endpoint" {
  value = aws_redshiftserverless_workgroup.this.endpoint
}