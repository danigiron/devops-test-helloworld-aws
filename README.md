# Introduction
This project creates and infrastructure in AWS and all stuff in order to deploy an HelloWorld Application.

# Prerequisits

Before to start, install the pip packages in order to deploy this project

`pip install -r requirements.txt`

# What do you need?

In order to use this project, you need define the following environemnt variables:

- AWS_ACCESS_KEY_ID: `export AWS_ACCESS_KEY_ID=<ACCESS_KEY>`
- AWS_SECRET_ACCESS_KEY: `export AWS_SECRET_ACCESS_KEY=<SECRET_KEY>`

Also, you need two passwords, one in order to assign the administrator user of Postgres and another one to encrypt the password of the database user for the application.

Modify the file `prod.yml` located in the root directory of this project and change the string `<IP>` with your public IP.

Add your public SSH key inside the folder `<projectFolder>/Docker/amis/Packer/ansible/files/` with name `<youruser>.pub` and add your user in the playbook located in `<projectFolder>/Docker/amis/Packer/ansible/playbook.yml` as follows:

```
- hosts: localhost
  connection: local
  vars:
    users:
    - dgiron
    - <youruser>
    logs:
    - app.log
    - access.log
```

# How to use it?

Once we have all the previous step explained above, we can run the application.

The script in order to create the stack and deploy the application is `<project_folder>/deploy.py` and accept the following parameters with its values:

- --deploy=[all | deploy | database | network]
    - all: Create all cloudformation stacks and build/deploy the application.
    - deploy: Build and deploy the application and do the changes in ASG and LC.
    - database: Build the database stack. Due the dependencies, this value build a Networks stack
    - network: Create a network stack.
- --action=[delete | create]
    - create: Create the specific stacks
    - delete: Delete ALL stacks
- --env=[prod]
    - prod: environment prod

# Examples

The following command create all resources listed bellow:

```
deploy.py --env=prod --resource=all --action=create
```

- VPC
- S3 Bucket 
- Subnet groups
- RDS
- Generate .jar and stored in the S3 Bucket
- IAM Roles
- AMI with jar application
- ELB, AutoScalingGroup and LaunchConfiguration

The following command remove all resources:

```
deploy.py --env=prod --resource=database --action=delete
```
> Note: When `--action=delete` the resource is ignored and allways remove all resources

The next command generate do the following steps:

```
deploy.py --env=prod --resource=deploy --action=create
```
- Create .jar and tored in the S3 Bucket
- Generate an AMI with the new .jar
- Update stack with ELB, AutoScaling and LaunchConfiguration (In this step, the stack generate a new AutoScaling and LaunchConfiguration and do rollout 1 instance by 1 instance replacing the older instances)


