from troposphere import GetAtt, Join, Output, Parameter, Ref, Template, Tags, Export
from troposphere.ec2 import SecurityGroup, SecurityGroupEgress, SecurityGroupIngress

def addIngress(self,name,app,env,cidr,from_port,to_port,protocol,resource):
    ingress=SecurityGroupIngress(
        "ingress"+name+app+env,
        CidrIp=cidr,
        Description="Ingress number ",
        GroupId=Ref(resource),
        IpProtocol=protocol,
        DependsOn="SecurityGroup"+name+app+env,
        FromPort=from_port,
        ToPort=to_port,
    )
    return (ingress)
def addIngressCidr(self,name,app,env,cidr,from_port,to_port,protocol,resource):
    ingress=SecurityGroupIngress(
        "ingress"+name+app+env,
        CidrIp=cidr,
        Description="Ingress number ",
        GroupId=Ref(resource),
        IpProtocol=protocol,
        DependsOn="SecurityGroup"+name+app+env,
        FromPort=from_port,
        ToPort=to_port,
    )
    return (ingress)
def addIngressSG(self,name,app,env,sg,from_port,to_port,protocol,resource):
    ingress=SecurityGroupIngress(
        "ingressSG"+name+app+env,
        SourceSecurityGroupId=sg,
        Description="Ingress number ",
        GroupId=Ref(resource),
        IpProtocol=protocol,
        DependsOn="SecurityGroup"+name+app+env,
        FromPort=from_port,
        ToPort=to_port,
    )
    return (ingress)
def add_output(self,name,app,env,resource,export):
    output=Output(
        "SecurityGroupID"+name+app+env,
        Description="Security Group ID",
        Value=Ref(resource)
    )
    return (output)
    