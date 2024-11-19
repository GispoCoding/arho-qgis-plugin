output "db_postgres_version" {
  description = "The exact PostgreSQL version of the main db."
  value       = aws_db_instance.main_db.engine_version_actual
}

output "lambda_db_manager" {
  description = "Name of the db_manager Lambda function."
  value       = aws_lambda_function.db_manager.function_name
}

output "lambda_koodistot_loader" {
  description = "Name of the koodistot_loader Lambda function."
  value       = aws_lambda_function.koodistot_loader.function_name
}

output "lambda_ryhti_client" {
  description = "Name of the ryhti_loader Lambda function."
  value       = aws_lambda_function.ryhti_client.function_name
}

output "lambda_update_user" {
  description = "Name of the lambda function update user."
  value       = aws_iam_user.lambda_update_user.name
}

output "bastion_address" {
  description = "SSH tunneling server public address"
  value       = aws_route53_record.bastion[0].name
}

output "xroad_fqdn" {
  description = "X-Road Security Server fully qualified domain name"
  value       = local.xroad_dns_record
}

output "xroad_ip_address" {
  description = "X-Road Security Server public IP address"
  value       = aws_eip.eip.public_ip
}
