resource "aws_efs_file_system" "x-road_configuration_volume" {
  encrypted = true

  tags = merge(var.default_tags, {Name = "${var.prefix}-x-road_configuration_volume"})
}

resource "aws_efs_mount_target" "x-road_configuration_volume" {
  # both subnets will need their own mount target!
  count = var.private-subnet-count
  file_system_id = aws_efs_file_system.x-road_configuration_volume.id
  subnet_id      = var.private_subnet_ids[count.index]
  security_groups = [aws_security_group.x-road.id]
}

resource "aws_efs_file_system" "x-road_archive_volume" {
  encrypted = true
  # TODO: add backups!!

  tags = merge(var.default_tags, {Name = "${var.prefix}-x-road_archive_volume"})
}

resource "aws_efs_mount_target" "x-road_archive_volume" {
  # both subnets will need their own mount target!
  count = var.private-subnet-count
  file_system_id = aws_efs_file_system.x-road_archive_volume.id
  subnet_id      = var.private_subnet_ids[count.index]
  security_groups = [aws_security_group.x-road.id]
}
