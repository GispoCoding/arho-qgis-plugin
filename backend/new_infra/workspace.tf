# Every deployment is a workspace, e.g. test or prod, and the workspace name is the
# environment name used in resource names and labels. There is no separate variable for it,
# so the two cannot disagree.
locals {
  environment = terraform.workspace
}

# Stops a plan before it changes anything when the workspace cannot be an environment:
# - the default workspace: its state would sit outside arho/<workspace>/, and it would name
#   resources arho-default-*.
# - a name that is not valid in UpCloud resource names and labels.
resource "terraform_data" "workspace_guard" {
  lifecycle {
    precondition {
      condition     = terraform.workspace != "default"
      error_message = "Select a deployment workspace first: make tf-init ws=<environment> backend=<name>."
    }
    precondition {
      condition     = can(regex("^[a-z][a-z0-9-]*$", terraform.workspace))
      error_message = "The workspace name \"${terraform.workspace}\" is used as the environment name. Use lowercase letters, digits and hyphens."
    }
  }
}
