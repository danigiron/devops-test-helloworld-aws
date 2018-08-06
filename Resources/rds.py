from troposphere import GetAtt, Join, Output, Ref, Template, ImportValue, Tags, Export
from troposphere.ec2 import SecurityGroup,SecurityGroupRule
from troposphere.rds import DBInstance, DBSubnetGroup

def databaseTemplate(name,app,env,engine,version,storageSize,instanceSize,DBPassword,port,officeIP,dbAdmin,nameSubnetGroup,dbApp):
    
    template =  Template()

    sg = template.add_resource(SecurityGroup(
        "SecurityGroup"+name+app+env,
        GroupDescription="Security group for "+name+"-"+app+"-"+env,
        VpcId=ImportValue("VPC"+env),
        SecurityGroupIngress = [
            SecurityGroupRule(
                IpProtocol="tcp",
                FromPort=port,
                ToPort=port,
                CidrIp=officeIP,
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
            Name="sg-"+name+"-"+app+"-"+env,
            app=app,
        ),
    ))

    instance = template.add_resource(DBInstance(
        "DB"+name+app+env,
        DBName=dbApp,
        AllocatedStorage=storageSize,
        DBInstanceClass=instanceSize,
        Engine=engine,
        EngineVersion=version,
        MasterUsername=dbAdmin,
        PubliclyAccessible="true",
        MasterUserPassword=DBPassword,
        DBSubnetGroupName=ImportValue(nameSubnetGroup+env),
        VPCSecurityGroups=[Ref(sg)],
    ))

    template.add_output(Output(
        "DatabaseOutputApplication"+name+app+env,
        Description="JDBC connection string for database",
        Value=Join("", [
            "jdbc:"+engine+"://",
            GetAtt(instance, "Endpoint.Address"),
            ":",
            GetAtt(instance, "Endpoint.Port"),
        ])
    ))

    template.add_output(Output(
        "DatabaseHost"+name+app+env,
        Description="Host Database Endpoint",
        Value=GetAtt(instance,"Endpoint.Address")
    ))

    template.add_output(Output(
        "OutputSecurityGroup"+name+app+env,
        Description="SG of RDS"+name+"-"+app+"-"+env,
        Value=Ref(sg),
        Export=Export(
            "SG-"+name+"-"+app+"-"+env
        )
    ))

    return (template.to_json())
