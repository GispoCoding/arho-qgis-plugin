data "aws_availability_zones" "available" {
  state = "available"
}

# Create common VPC for bastion, lambdas, rds, efs and ecs
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  enable_dns_hostnames = true

  tags = merge(local.default_tags, { "Name" : "${var.prefix}-vpc" })
}

resource "aws_subnet" "public" {
  # will have subnets the same # as availability zones
  # by default, we have eu-central-1a and eu-central-1b
  count                   = var.public-subnet-count
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  cidr_block              = "10.0.${count.index}.0/24"
  map_public_ip_on_launch = true
  vpc_id                  = aws_vpc.main.id

  tags = merge(local.default_tags, {
    Name       = "${var.prefix}-public-subnet-${count.index}"
    SubnetType = "public"
  })
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(local.default_tags, {
    Name = "${var.prefix}-igw"
  })
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  tags = merge(local.default_tags, {
    Name = "${var.prefix}-public-route-table"
  })
}

resource "aws_route" "public" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.main.id
}

resource "aws_route_table_association" "public" {
  count          = var.public-subnet-count
  route_table_id = aws_route_table.public.id
  subnet_id      = aws_subnet.public[count.index].id
}

resource "aws_subnet" "private" {
  # private subnet for the database instance, lambdas and ecs
  count                   = var.private-subnet-count
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  # what block should we use for the private subnets? is this alright?
  cidr_block              = "10.0.${count.index + 128}.0/24"
  map_public_ip_on_launch = false
  vpc_id                  = aws_vpc.main.id

  tags = merge(local.default_tags, {
    Name       = "${var.prefix}-private-subnet-${count.index}"
    SubnetType = "private"
  })
}

data "aws_subnets" "private"{
    filter {
        name   = "vpc-id"
        values = [aws_vpc.main.id]
    }

    tags = {
        SubnetType = "private"
    }
}

# Give lambdas and X-road security server access to Internet
resource "aws_eip" "eip" {
  domain        = "vpc"
  depends_on = [aws_internet_gateway.main]

  tags = merge(local.default_tags, {
    Name = "${var.prefix}-eip"
  })
}

# Use only one nat gateway for now (outbound traffic not that critical)
resource "aws_nat_gateway" "nat_gateway" {
  allocation_id = aws_eip.eip.id
  subnet_id     = aws_subnet.public[0].id

  tags = merge(local.default_tags, {
    Name = "${var.prefix}-nat-gateway"
  })
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat_gateway.id
  }

  tags = merge(local.default_tags, {
    Name = "${var.prefix}-route-table-private"
  })
}

resource "aws_route_table_association" "private" {
  count          = var.private-subnet-count
  route_table_id = aws_route_table.private.id
  subnet_id      = aws_subnet.private[count.index].id
}

resource "aws_db_subnet_group" "db" {
  name       = "${var.prefix}-db"
  # only list private subnets in the db subnet group
  subnet_ids = data.aws_subnets.private.ids

  tags = merge(local.default_tags, {
    Name = "${var.prefix}-db"
  })
}

# Allows traffic to db and wherever lambdas need
resource "aws_security_group" "lambda" {
  name        = "${var.prefix} lambda"
  description = "${var.prefix} lambda security group"
  vpc_id      = aws_vpc.main.id

  ingress {
    # allow traffic from the same security group
    protocol  = -1
    self      = true
    from_port = 0
    to_port   = 0
  }

  egress {
    # allow all outbound traffic
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.default_tags, {
    Name = "${var.prefix}-lambda-sg"
  })
}

# Allow traffic from bastion and lambdas to db
resource "aws_security_group" "rds" {
  name        = "${var.prefix} database"
  description = "${var.prefix} database security group"
  vpc_id      = aws_vpc.main.id

  tags = merge(local.default_tags, {
    Name = "${var.prefix}-rds-sg"
  })
}


resource "aws_security_group_rule" "rds-lambda" {
  description       = "Rds allow traffic from vpc"
  type              = "ingress"

  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  # Cannot specify both cidr block and source security group
  #cidr_blocks       = ["10.0.0.0/16"]
  source_security_group_id = aws_security_group.lambda.id
  security_group_id = aws_security_group.rds.id
}



# Allow traffic to bastion from the Internet
resource "aws_security_group" "bastion" {
  name   = "${var.prefix} bastion"
  description  = "${var.prefix} bastion security group"
  vpc_id      = aws_vpc.main.id

  tags = merge(local.default_tags, {
    Name = "${var.prefix}-bastion-sg"
  })
}

resource "aws_security_group_rule" "bastion-self" {
  description       = "Allow traffic from the same security group to e.g. vpc endpoints"
  security_group_id = aws_security_group.bastion.id
  protocol          = -1
  self              = true
  from_port         = 0
  to_port           = 0
  type              = "ingress"
}

resource "aws_security_group_rule" "internet-bastion" {
  description       = "Allow developers to access the bastion"
  security_group_id = aws_security_group.bastion.id
  cidr_blocks       = ["0.0.0.0/0"]
  from_port         = 22
  protocol          = "tcp"
  to_port           = 22
  type              = "ingress"
}

resource "aws_security_group_rule" "bastion-internet" {
  description       = "Allow bastion to access world (e.g. for installing postgresql client etc)"
  security_group_id = aws_security_group.bastion.id
  cidr_blocks       = ["0.0.0.0/0"]
  from_port         = 0
  protocol          = -1
  to_port           = 0
  type              = "egress"
}

resource "aws_security_group_rule" "rds-bastion" {
  description       = "Rds allow traffic from bastion"
  type              = "ingress"

  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  # Cannot specify both cidr block and source security group
  # cidr_blocks       = ["10.0.0.0/16"]
  source_security_group_id = aws_security_group.bastion.id
  security_group_id = aws_security_group.rds.id
}

# Add API gateway to bastion security group only

# Apparently this is an existing endpoint service we don't need to configure:
data "aws_vpc_endpoint_service" "execute-api" {
  service = "execute-api"
}

resource "aws_vpc_endpoint" "lambda_api" {
  vpc_id              = aws_vpc.main.id
  service_name        = data.aws_vpc_endpoint_service.execute-api.service_name
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true

  subnet_ids = [aws_subnet.private[0].id, aws_subnet.private[1].id]
  security_group_ids = [aws_security_group.bastion.id]

  tags = merge(local.default_tags, {
    Name = "${var.prefix}-lambda-api-endpoint"
  })
}
