# Hame infra

- [Setup](#setup)
- [Multi-factor authentication (MFA)](#multi-factor-authentication-mfa)
- [Managing existing instances](#managing-existing-instances)
- [Configuring new instances](#configuring-new-instances)
- [Deploying instances](#deploying-instances)
   - [Configuring X-Road (Suomi.fi Palvelyväylä) access](#configuring-x-road-suomifi-palveluväylä-access)
- [Teardown of instances](#teardown-of-instances)
- [Manual interactions](#manual-interactions)

## Setup

Run these steps the first time.

1. Install [Terraform](https://terraform.io) and `aws cli`
2. Create an AWS access key and store it locally in a credentials file (
   see [AWS Configuration basics](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html#cli-configure-quickstart-config)
   and [Where are the configuration settings stored](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
   for more info)
3. To manage existing instances, install [sops](https://github.com/getsops/sops) to decrypt encrypted variable files in the repository.

### Multi-factor authentication (MFA)

For most AWS accounts, MFA is required. You will get 400 or 403 error when running terraform with
just the right access key. To set up MFA, install both AWS CLI and jq, and make sure you have `aws` and `jq` in path. Execute the `[get-mfa-vars.sh](https://gist.github.com/mvaaltola/0abced5790401f2454444fb2ffd4acc0)` script with the *AWS arn of your MFA device and current MFA access code*,
and finally run `. /tmp/aws-mfa-token` to temporarily set the correct MFA environment variables in your shell. By default, the MFA session token will last for 12 hours.

## Managing existing instances

To manage existing instances, decrypt `hame-dev.tfvars.enc.json` by running `sops -d hame-dev.tfvars.enc.json > hame-dev.tfvars.json`.

To make changes to instances, first check that your variables and current infra is up to date with terraform state:

```shell
terraform init
terraform plan --var-file hame-dev.tfvars.json
```

This should report that terraform state is up to date with infra and configuration. You may make changes to configuration or variables and run `terraform plan --var-file hame-dev.tfvars.json` again to check what your changes would mean to the infrastructure.

When you are sure that you want to change AWS infra, run

```shell
terraform apply --var-file hame-dev.tfvars.json
```

Please verify that the reported changes are desired, and respond `yes` to apply the changes to infrastructure.

## Configuring new instances

1. To create a new instance of hame-ryhti, copy [hame.tfvars.sample.json](hame.tfvars.sample.json) to a new file called `hame-your-deployment.tfvars.json`.
2. Create an IAM user for CI/CD and take down the username and credentials. This can be used to configure CD deployment from Github. If CD is already configured, fill in existing user in `AWS_LAMBDA_USER` part in `hame-your-deployment.tfvars.json`. Fill credentials in Github secrets `AWS_LAMBDA_UPLOAD_ACCESS_KEY_ID` and `AWS_LAMBDA_UPLOAD_SECRET_ACCESS_KEY`.
3. Change the values in `hame-your-deployment.tfvars.json` as required
4. Create zip packages for the lambda functions by running `make build-lambda -C ..` (this
   has to be done only once since github actions can be configured to update functions).

## Deploying instances

To launch new instances, run the following commands:

```shell
terraform init
terraform apply --var-file hame-your-deployment.tfvars.json
```

Note: Setting up the instances takes a couple of minutes.

### Configuring X-Road (Suomi.fi Palveluväylä) access

A simple X-Road security server sidecar container is included in the Terraform configuration. If you need to connect your Hame-Ryhti instance to Suomi.fi Palveluväylä to transfer official Maakuntakaava data to Ryhti, manual configuration is required. After going through the steps below, the configuration is saved in your AWS Elastic File System, and it is reused when you boot or update the X-Road security server container.

This is because you need to apply for a separate permit for your subsystem to be connected to the Suomi.fi Palveluväylä. Follow the steps below:

1. You must apply for permission to join the Palveluväylä test environment first: [Liittyminen kehitysympäristöön](https://palveluhallinta.suomi.fi/fi/sivut/palveluvayla/kayttoonotto/liittyminen-kehitysymparistoon). For the permission application, you will need
   - the public IP address in your AWS, which you will find as `hame-your-deployment-eip` under AWS EC2 Elastic IPs in the AWS EC2 console Network & Security settings.
   - a client name for your new client, which Palveluväylä requires to be of the form servicename-organization-client. So in our case `ryhti-<your_organization>-client`, e.g. `ryhti-vsl-client`.
When your application is accepted, you are provided with the configuration anchor file needed later.
2. Create an SSH key and add the public key to `bastion_ec2_tunnel_public_keys` in `hame-your-deployment.tfvars.json`.
3. Fill in the desired admin username and password in `x-road_secrets` in `hame-your-deployment.tfvars.json`.
4. Apply the variables to AWS with `terraform apply --var-file hame-your-deployment.tfvars.json`.
5. Check the private IP address of your `hame-your-deployment-x-road_securityserver` service task under your AWS Elastic Container Service `hame-your-deployment-x-road_securityserver` cluster in your AWS web console.
6. Open an SSH tunnel to the X-Road server admin interface (e.g. `ssh -N -L4001:<private-ip>:4000 -i "~/.ssh/hame-ec2-tunnel.pem" ec2-user@hame-your-deployment.<bastion_subdomain>.<aws_hosted_domain>`, where `hame-ec2-tunnel.pem` contains your SSH key created in step 2, and `bastion_subdomain` and `aws_hosted_domain` are the settings in your `hame-your-deployment.tfvars.json`).
7. Point your web browser to [https://localhost:4001](https://localhost:4001). The connection
must be HTTPS, and you must ignore the warning about invalid SSL certificate: the hostname is localhost instead of the server IP because of the SSH tunneling, and the certificate does not know that.
8. Log in to the [https://localhost:4001](https://localhost:4001) admin interface with your x-road secrets that you selected in step 3.
9. Configure your X-Road server following the general [X-Road security server installation guide](https://github.com/nordic-institute/X-Road/blob/master/doc/Manuals/ig-ss_x-road_v6_security_server_installation_guide.md#33-configuration) Chapter 3.3 (Configuration). Here, you will need the configuration anchor file provided when registering in step 1.

...
10. Apply for permission for your new client to connect to Ryhti following the instructions at
[Uuden alijärjestelmän liittäminen liityntäpalvelimeen ja sen poistaminen](https://palveluhallinta.suomi.fi/fi/tuki/artikkelit/591ac1e314bbb10001966f9c), and follow the instructions for adding the client in your admin interface.

## Teardown of instances

Shut down and destroy the instances with `terraform destroy --var-file hame-your-deployment.tfvars.json`

## Manual interactions

You can interact with the lambda functions using the [Makefile](./Makefile).

> For example migrate the database with `make migrate-db`
