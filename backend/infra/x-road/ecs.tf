# Cluster is a collection of compute resources that can run tasks and services (docker containers in the end)
resource "aws_ecs_cluster" "x-road_securityserver" {
  name = "${var.prefix}-x-road_securityserver"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = merge(var.default_tags, {Name = "${var.prefix}-cluster"})
}

# Task definition is a description of parameters given to docker daemon, in order to run a container
resource "aws_ecs_task_definition" "x-road_securityserver" {
  family                   = "${var.prefix}-x-road_securityserver"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  # This is the IAM role that the docker daemon will use, e.g. for pulling the image from ECR (AWS's own docker repository)
  execution_role_arn       = var.docker_execution_role_arn
  # If the containers in the task definition need to access AWS services, we'd specify a role via task_role_arn.
  # task_role_arn = ...
  cpu                      = var.x-road_securityserver_cpu
  memory                   = var.x-road_securityserver_memory
  container_definitions    = jsonencode(
  [
    {
      name         = "x-road_securityserver-from-dockerhub"
      image        = var.x-road_securityserver_image
      cpu          = var.x-road_securityserver_cpu
      memory       = var.x-road_securityserver_memory
      # try out AWS EFS volume for storing x-road configuration!
      mountPoints  = [
        {
          "sourceVolume": "configuration-volume",
          "containerPath": "/etc/xroad"
        },
        {
          "sourceVolume": "archive-volume",
          "containerPath": "/var/lib/xroad"
        }
      ]
      volumesFrom  = []
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group = "/aws/ecs/${var.prefix}-x-road_securityserver"
          awslogs-region = var.AWS_REGION_NAME
          awslogs-stream-prefix = "ecs"
        }
      }
      essential    = true
      portMappings = [
        {
          # admin UI
          hostPort = 4000
          containerPort = 4000
          protocol      = "tcp"
        },
        {
          # health check
          hostPort = 5588
          containerPort = 5588
          protocol      = "tcp"
        },
        {
          # consumer HTTP
          hostPort = 8080
          containerPort = 8080
          protocol      = "tcp"
        },
        # These are not needed if we don't provide X-road services
        # {
        #   # message exchange between security servers
        #   hostPort = 5500
        #   containerPort = 5500
        #   protocol = "tcp"
        # },
        # {
        #   # OCSP responses between security servers
        #   hostPort = 5577
        #   containerPort = 5577
        #   protocol = "tcp"
        # }
      ]
      # With Fargate, we use awsvpc networking, which will reserve a ENI (Elastic Network Interface) and attach it to
      # our VPC
      networkMode  = "awsvpc"
      environment  = [
        {
          name = "XROAD_ADMIN_USER"
          value = var.x-road_secrets.admin_user
        },
        {
          name = "XROAD_ADMIN_PASSWORD"
          value = var.x-road_secrets.admin_password
        },
        {
          name = "XROAD_DB_HOST"
          value = aws_db_instance.xroad_db.address
        },
        {
          name = "XROAD_DB_PORT"
          value = "5432"
        },
        {
          name = "XROAD_DB_PWD"
          value = var.x-road_db_password
        },
        {
          name = "XROAD_TOKEN_PIN"
          value = var.x-road_token_pin
        }
      ]
    }
  ])

  volume {
  name = "configuration-volume"
    efs_volume_configuration {
      file_system_id          = aws_efs_file_system.x-road_configuration_volume.id
      transit_encryption      = "ENABLED"
      # authorization_config {
      #   access_point_id = aws_efs_access_point.test.id
      #   iam             = "ENABLED"
      # }
    }
  }

  volume {
  name = "archive-volume"
    efs_volume_configuration {
      file_system_id          = aws_efs_file_system.x-road_archive_volume.id
      transit_encryption      = "ENABLED"
      # authorization_config {
      #   access_point_id = aws_efs_access_point.test.id
      #   iam             = "ENABLED"
      # }
    }
  }

  tags = merge(var.default_tags, {Name = "${var.prefix}-x-road_securityserver-definition"})
}

resource "aws_ecs_service" "x-road_securityserver" {
  name            = "${var.prefix}-x-road_securityserver"
  cluster         = aws_ecs_cluster.x-road_securityserver.id
  task_definition = aws_ecs_task_definition.x-road_securityserver.arn
  desired_count   = 1

  # We run containers with the Fargate launch type. The other alternative is EC2, in which case we'd provision EC2
  # instances and attach them to the cluster.
  launch_type = "FARGATE"

  # We need to get the private ip of the container somehow out of terraform, so we cannot
  # quit terraform until the container has reached steady state:
  # https://stackoverflow.com/questions/75856201/how-to-retrieve-the-public-ip-address-of-an-aws-ecs-contrainer-using-terraform
  enable_ecs_managed_tags = true
  propagate_tags = "TASK_DEFINITION"
  wait_for_steady_state = true

  network_configuration {
    # Fargate uses awspvc networking, we tell here into what subnets to attach the service
    # Security server does not need to be publicly accessible if it's only client
    subnets          = var.private_subnet_ids
    # Ditto for security groups
    security_groups  = [aws_security_group.x-road.id]
    assign_public_ip = false
  }

  service_registries {
    registry_arn   = aws_service_discovery_service.x-road_securityserver.arn
  }

  tags = merge(var.default_tags, {Name = "${var.prefix}_-x-road_securityserver"})
}
