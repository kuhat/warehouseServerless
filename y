version = 0.1
[default]
[default.deploy]
[default.deploy.parameters]
stack_name = "warehouse-api"
s3_bucket = "aws-sam-cli-managed-default-samclisourcebucket-1vm9uv79kjjeb"
s3_prefix = "warehouse-api"
region = "us-east-1"
confirm_changeset = true
capabilities = "CAPABILITY_IAM"
disable_rollback = true
image_repositories = []
