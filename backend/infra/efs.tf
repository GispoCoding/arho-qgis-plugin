resource "aws_efs_file_system" "x-road_configuration_volume" {
  encrypted = true
  kms_key_id = aws/elasticfilesystem

  tags = merge(local.default_tags, {Name = "${var.prefix}-x-road_configuration_volume"})
}
