
from troposphere import Base64, Join, ImportValue, Tags, GetAZs
from troposphere import Parameter, Ref, Template
from troposphere import cloudformation, autoscaling
from troposphere.autoscaling import AutoScalingGroup, Tag
from troposphere.autoscaling import LaunchConfiguration
from troposphere.elasticloadbalancing import LoadBalancer,AccessLoggingPolicy
from troposphere.policies import (
    AutoScalingReplacingUpdate, AutoScalingRollingUpdate, UpdatePolicy
)
from troposphere.s3 import BucketPolicy
from troposphere import ec2
from troposphere.ec2 import SecurityGroup, SecurityGroupEgress, SecurityGroupIngress, SecurityGroupRule
import troposphere.elasticloadbalancing as elb


def elb_asg_lc_template(app,env,nameSGRDS,rdsPort,instanceType,ami,subnets,elbPort,elbCidrBlock,ec2Port,desiredCapacity,minSize,maxSize,region,nameBucket, officeIP):

    template = Template()

    sgELB = template.add_resource(SecurityGroup(
        "SecurityGroupELB"+app+env,
        GroupDescription="Security group for "+app+"-"+env,
        VpcId=ImportValue("VPC"+env),
        SecurityGroupIngress = [
            SecurityGroupRule(
                IpProtocol="tcp",
                FromPort=elbPort,
                ToPort=elbPort,
                CidrIp=elbCidrBlock,
            )
        ],
        SecurityGroupEgress = [
            SecurityGroupRule(
                IpProtocol="-1",
                ToPort=0,
                FromPort=65535,
                CidrIp="0.0.0.0/0"
            )
        ],
        Tags=Tags(
            env=env,
            Name="sg-ELB"+app+"-"+env,
            app=app,
        ),
    ))
    sgEC2 = template.add_resource(SecurityGroup(
        "SecurityGroupEC2"+app+env,
        GroupDescription="Security group for EC2 "+app+"-"+env,
        VpcId=ImportValue("VPC"+env),
        DependsOn="SecurityGroupELB"+app+env,
        SecurityGroupIngress = [
            SecurityGroupRule(
                IpProtocol="tcp",
                FromPort=ec2Port,
                ToPort=ec2Port,
                SourceSecurityGroupId=Ref(sgELB),
                
            ),
            SecurityGroupRule(
                IpProtocol="tcp",
                FromPort=22,
                ToPort=22,
                CidrIp=officeIP,
                
            ),
        ],
        SecurityGroupEgress = [
            SecurityGroupRule(
                IpProtocol="-1",
                ToPort=0,
                FromPort=65535,
                CidrIp="0.0.0.0/0"
            )
        ],
        Tags=Tags(
            env=env,
            Name="sg-EC2-"+app+"-"+env,
            app=app,
        ),
    ))
    addIngressRDS = template.add_resource(
        SecurityGroupIngress(
            "ingressSGRDS"+app+env,
            SourceSecurityGroupId=Ref(sgEC2),
            Description="From EC2 instances",
            GroupId=ImportValue("SG-"+nameSGRDS+"-"+app+"-"+env),
            IpProtocol="tcp",
            FromPort=rdsPort,
            ToPort=rdsPort,
            DependsOn="SecurityGroupEC2"+app+env,
        )
    )

    launchConfig = template.add_resource(LaunchConfiguration(
        "LaunchConfiguration"+app+env,
        InstanceType=instanceType,
        ImageId=ami,
        SecurityGroups=[Ref(sgEC2)],
        IamInstanceProfile=ImportValue("Role-"+app+"-"+env)
    ))

    bucketPolicy = template.add_resource(BucketPolicy(
        "BucketPolicy"+nameBucket+app+env,
        Bucket = ImportValue("Bucket"+nameBucket+app+env),
        PolicyDocument = {
            "Version": "2012-10-17",
            "Statement": [{
                "Action": ["s3:PutObject"],
                "Effect": "Allow",
                "Resource": Join("", ["arn:aws:s3:::",ImportValue("Bucket"+nameBucket+app+env),"/AWSLogs/",Ref("AWS::AccountId"),"/*"]),
                "Principal": {
                    "AWS": ["156460612806"]
                }
            }
            ]
        }
        )
    )

    lb = template.add_resource(LoadBalancer(
        "LoadBalancer"+app+env,
        ConnectionDrainingPolicy=elb.ConnectionDrainingPolicy(
            Enabled=True,
            Timeout=120,
        ),
        Subnets=subnets,
        HealthCheck=elb.HealthCheck(
            "HealthCheck",
            Target="TCP:"+str(ec2Port),
            HealthyThreshold="5",
            UnhealthyThreshold="5",
            Interval="30",
            Timeout="15",
        ),
        Listeners=[
            elb.Listener(
                LoadBalancerPort=elbPort,
                InstancePort=ec2Port,
                Protocol="HTTP",
                InstanceProtocol="HTTP",
            ),
        ],
        CrossZone=True,
        SecurityGroups=[Ref(sgELB)],
        LoadBalancerName="lb-"+app+"-"+env,
        Scheme="internet-facing",
        AccessLoggingPolicy = AccessLoggingPolicy(
            "LoggingELB"+app+env,
            EmitInterval=5,
            Enabled=True,
            S3BucketName=ImportValue("Bucket"+nameBucket+app+env),
        )
    ))

    asg = template.add_resource(AutoScalingGroup(
        "AutoscalingGroup"+app+env,
        DesiredCapacity=desiredCapacity,
        Tags=[
            Tag("Environment", env, True)
        ],
        LaunchConfigurationName=Ref(launchConfig),
        MinSize=minSize,
        MaxSize=maxSize,
        LoadBalancerNames=[Ref(lb)],
        AvailabilityZones=GetAZs(region),
        VPCZoneIdentifier=subnets,
        HealthCheckType="ELB",
        HealthCheckGracePeriod= 300,
        UpdatePolicy=UpdatePolicy(
            AutoScalingReplacingUpdate=AutoScalingReplacingUpdate(
                WillReplace=True,
            ),
            AutoScalingRollingUpdate=AutoScalingRollingUpdate(
                PauseTime='PT5M',
                MinInstancesInService="1",
                MaxBatchSize='1',
                WaitOnResourceSignals=True,
            )
        )
    ))

    return(template.to_json())
