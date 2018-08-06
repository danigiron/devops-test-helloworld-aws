from troposphere import Template, Ref, Join, ImportValue, Output, Export
from troposphere.iam import Role, InstanceProfile, Policy

def roleTemplate(app,env,nameBucket):

        template = Template()

        Ec2Role = template.add_resource(Role(
            "Ec2Role",
            RoleName="ec2-role",
            AssumeRolePolicyDocument={"Statement": [{
                "Effect": "Allow",
                "Principal": {
                    "Service": [ "ec2.amazonaws.com" ]
                },
                "Action": [ "sts:AssumeRole" ]
            }]},
            Policies=[Policy(
                PolicyName="ec2-policy",
                PolicyDocument={
                    "Statement": [
                        {
                            "Action": [
                                "ec2:*",
                            ],
                            "Effect": "Allow",
                            "Resource": ["*"]
                        }
                    ]
                }
            ),
            Policy(
                PolicyName="s3List",
                PolicyDocument={
                    "Statement": [
                        {
                            "Action": ["s3:ListBucket"],
                            "Resource":[Join("",["arn:aws:s3:::",ImportValue("Bucket"+nameBucket+app+env)])],
                            "Effect": "Allow"
                        }
                    ]
                }
            ),
            Policy(
                PolicyName="s3Permissions",
                PolicyDocument={
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": [
                                "s3:PutObject",
                                "s3:GetObject",
                                "s3:DeleteObject"
                            ],
                            "Resource": [Join("",["arn:aws:s3:::",ImportValue("Bucket"+nameBucket+app+env),"/*"])]
                        }
                    ]
                }
            )
            ]
        )
        )



        profile = template.add_resource(InstanceProfile(
            "InstanceProfile",
            Roles=[Ref(Ec2Role)]
        ))

        output = template.add_output(Output(
            "iamRole"+app+env,
            Description="IAM Role",
            Value=Ref(profile),
            Export=Export("Role-"+app+"-"+env)
        ))

        return (template.to_json())
