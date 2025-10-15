output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.this.id
}

output "public_subnets" {
  value = { for k, s in aws_subnet.public : k => { id = s.id, cidr = s.cidr_block } }
}

output "private_subnets" {
  value = { for k, s in aws_subnet.private : k => { id = s.id, cidr = s.cidr_block } }
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = [for subnet in aws_subnet.private : subnet.id]
}