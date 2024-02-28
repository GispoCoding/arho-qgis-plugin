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

output "lambda_update_user" {
  description = "Name of the lambda function update user."
  value       = aws_iam_user.lambda_update_user.name
}

output "bastion_ip" {
  description = "EC2 server public IP."
  value       = aws_instance.bastion-ec2-instance.public_ip
}
