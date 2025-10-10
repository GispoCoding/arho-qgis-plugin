resource "aws_security_group_rule" "rds-x-road" {
  description       = "Rds allow traffic from vpc"
  type              = "ingress"

  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  # Cannot specify both cidr block and source security group
  #cidr_blocks       = ["10.0.0.0/16"]
  source_security_group_id = aws_security_group.x-road.id
  security_group_id = var.rds_security_group_id
}


# Allow traffic from x-road server to internet, file system and database
resource "aws_security_group" "x-road" {
  name        = "${var.prefix} X-road security server"
  description = "${var.prefix} X-road security server security group"
  vpc_id      = var.vpc_id

# To X-road central server and OCSP service
  egress {
    from_port   = 0
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 4001
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

# To remote X-road security server
  egress {
    from_port   = 0
    to_port     = 5500
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 5577
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

# To file system
  egress {
    from_port   = 0
    to_port     = 2049
    protocol    = "tcp"
    self        = true
  }

# To database
  egress {
    from_port   = 0
    to_port     = 5432
    protocol    = "tcp"
    security_groups = [var.rds_security_group_id]
  }

  tags = merge(var.default_tags, {
    Name = "${var.prefix}-x-road_securityserver-sg"
  })
}

# Allow traffic from lambda to x-road server consumer port
resource "aws_security_group_rule" "lambda-x-road" {
  description       = "X-road allow traffic from lambda"
  type              = "ingress"

  from_port         = 8080
  to_port           = 8080
  protocol          = "tcp"

  source_security_group_id = var.lambda_security_group_id
  security_group_id = aws_security_group.x-road.id
}

# Allow traffic from bastion to x-road server admin port
resource "aws_security_group_rule" "bastion-x-road" {
  description       = "X-road allow traffic from bastion"
  type              = "ingress"

  from_port         = 4000
  to_port           = 4000
  protocol          = "tcp"

  source_security_group_id = var.bastion_security_group_id
  security_group_id = aws_security_group.x-road.id
}

# Allow traffic inside the x-road security group to EFS
resource "aws_security_group_rule" "x-road-filesystem" {
  description       = "X-road allow traffic to EFS file system"
  type              = "ingress"
  from_port         = 2049
  to_port           = 2049
  protocol          = "tcp"

  self              = true
  security_group_id = aws_security_group.x-road.id
}
