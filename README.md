# Introduction
This project creates an infrastructure in AWS and all stuff in order to deploy a HelloWorld Application.

# Prerequisits

Packages installed

- Python 2.7
- pip
- Docker

Before starting, install the pip packages in order to deploy this project

```
pip install -r requirements.txt
```

# What do you need?

In order to use this project, you need to define the following environment variables:

- AWS_ACCESS_KEY_ID: 
```
export AWS_ACCESS_KEY_ID=<ACCESS_KEY>
```
- AWS_SECRET_ACCESS_KEY: 
```
export AWS_SECRET_ACCESS_KEY=<SECRET_KEY>
```

Also, you need two passwords, one in order to assign the administrator user of Postgres and another one to encrypt the password of the database user for the application.

Modify the file `pro.yml` located in the root directory of this project and change the string `<IP>` with your public IP.

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

# Architecture

![alt text](https://raw.githubusercontent.com/danigiron/devops-test-helloworld-aws/master/images/architecture.png)

# How to use it?

Once you have done all the things explained above, you can run the application.

The script file in order to create the stack and deploy the application is `<project_folder>/deploy.py` and accept the following parameters with its values:

- --resource=[all | deploy | database | network]
    - all: Create all cloudformation stacks and build/deploy the application. 
    - deploy: Build and deploy the application and do the changes in ASG and LC.
    - database: Build the database stack. Due the dependencies, this value build a Networks stack
    - network: Create a network stack.
- --action=[delete | create]
    - create: Create the specific stacks
    - delete: Delete ALL stacks
- --env=[prod]
    - prod: environment prod

> When you deploy all resources or only the database(`--resource=all` | `--resource=database`), the script request you the password to access as administrator in the database and the password in order to encrypt the password for the user of the application.

> When you deploy the application (`--resource=deploy`), the script request you the password to desencrypt the database password for the user of the application

If you want create a new environment, you should create a file `<env>.yml` filled with all parameters, see the file `pro.yml` as sample.

# Examples

The following command create all resources listed bellow:

```
deploy.py --env=pro --resource=all --action=create
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
deploy.py --env=pro --resource=database --action=delete
```
> Note: When `--action=delete` the resource is ignored and always remove all resources

The next command do the following steps:

```
deploy.py --env=pro --resource=deploy --action=create
```
- Create .jar and stored in the S3 Bucket
- Generate an AMI with the new .jar
- Update stack with ELB, AutoScaling and LaunchConfiguration (In this step, the stack generates a new AutoScaling and LaunchConfiguration and do rollout 1 instance by 1 instance replacing the older instances)



