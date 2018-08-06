from troposphere import Tags, Ref, Output, Template, Join, Export,GetAtt
from troposphere.ec2 import PortRange, NetworkAcl, Route, \
    VPCGatewayAttachment, SubnetRouteTableAssociation, Subnet, RouteTable, \
    VPC, NetworkInterfaceProperty, NetworkAclEntry, \
    SubnetNetworkAclAssociation, EIP, InternetGateway, \
    SecurityGroupRule, SecurityGroup, NatGateway


def vpcTemplate(name,app,env,cidrBlock,publicSubnets,privateSubnets):

    template = Template()
    vpc = template.add_resource(VPC(
        "VPC"+name+app+env,
        CidrBlock=cidrBlock,
        EnableDnsSupport=True,
        EnableDnsHostnames=True,
        Tags = Tags(
            Env=env,
            Name=name+"-"+env,
        ),
    ))

    internetGateway = template.add_resource(InternetGateway(
        "InternetGateway"+name+app+env,
        Tags=Tags(
            Env=env,
            Name="igw-"+env,
        ),
    ))

    gatewayAttachment = template.add_resource(VPCGatewayAttachment(
        "InternetGatewayAttachment"+name+app+env,
        InternetGatewayId=Ref(internetGateway),
        VpcId=Ref(vpc),
        DependsOn="VPC"+name+app+env
    ))

    publicRouteTable = template.add_resource(RouteTable(
        "PublicRouteTable",
        VpcId=Ref(vpc),
        Tags=Tags(
            Name="rt-public"+env,
            Env=env,
        ),
    ))

    internetGWRoute = template.add_resource(Route(
        "RouteToIGW",
        RouteTableId=Ref(publicRouteTable),
        DestinationCidrBlock='0.0.0.0/0',
        GatewayId=Ref(internetGateway)
    ))

    privateNetworkAcl = template.add_resource(NetworkAcl(
        "PrivateNetworkAcl",
        VpcId=Ref(vpc),
        Tags=Tags(
            Name="PrivateNetworkAcl"+env,
        ),
    ))
    zones=["a","b","c"]

    for index,subnet in enumerate(privateSubnets):

        template.add_resource(Subnet(
            "PrivateSubnet"+zones[index],
            CidrBlock=subnet,
            AvailabilityZone=Join("", [Ref("AWS::Region"), zones[index]]),
            MapPublicIpOnLaunch=False,
            Tags=Tags(
                Env=env,
                Name="Private-Subnet-"+zones[index]
            ),
            VpcId=Ref(vpc),
            DependsOn="VPC"+name+app+env
        ))

        template.add_resource(RouteTable(
            "PrivateRouteTable"+zones[index],
            VpcId=Ref(vpc),
            Tags=Tags(
                Name="rt-private"+env+"-"+zones[index],
                Env=env,
            ),
            DependsOn="VPC"+name+app+env
        ))

        template.add_resource(EIP(
            "EIP"+zones[index],
        ))
        template.add_resource(NatGateway(
            "NatGWZone"+zones[index],
            AllocationId=GetAtt("EIP"+zones[index], 'AllocationId'),
            SubnetId=Ref("PublicSubnet"+zones[index]),
            DependsOn="PublicSubnet"+zones[index]
        ))
        template.add_resource(Route(
            'NatRoute'+zones[index],
            RouteTableId=Ref("PrivateRouteTable"+zones[index]),
            DestinationCidrBlock='0.0.0.0/0',
            NatGatewayId=Ref("NatGWZone"+zones[index]),
            DependsOn="PrivateRouteTable"+zones[index]
        ))

        template.add_resource(SubnetRouteTableAssociation(
            "PrivateSubnetRouteTable"+zones[index],
            RouteTableId=Ref("PrivateRouteTable"+zones[index]),
            SubnetId=Ref("PrivateSubnet"+zones[index]),
            DependsOn="PrivateRouteTable"+zones[index]
        ))

        template.add_resource(SubnetNetworkAclAssociation(
            "PrivateNetworkAclAss"+zones[index],
            SubnetId=Ref("PrivateSubnet"+zones[index]),
            NetworkAclId=Ref(privateNetworkAcl),
            DependsOn="PrivateNetworkAcl"
        ))
    for index,subnet in enumerate(publicSubnets):

        template.add_resource(Subnet(
            "PublicSubnet"+zones[index],
            CidrBlock=subnet,
            AvailabilityZone=Join("", [Ref("AWS::Region"), zones[index]]),
            MapPublicIpOnLaunch=True,
            Tags=Tags(
                Env=env,
                Name="Public-Subnet-"+zones[index]
            ),
            VpcId=Ref(vpc),
            DependsOn="VPC"+name+app+env
        ))

        template.add_resource(SubnetRouteTableAssociation(
            "PublicSubnetRouteTable"+zones[index],
            RouteTableId=Ref(publicRouteTable),
            SubnetId=Ref("PublicSubnet"+zones[index]),
            DependsOn="VPC"+name+app+env
        ))
    
    template.add_resource(NetworkAclEntry(
        "PrivateNetworkAclEntryIngress"+env,
        CidrBlock=cidrBlock,
        Egress=False,
        NetworkAclId=Ref(privateNetworkAcl),
        Protocol=-1,
        RuleAction="allow",
        RuleNumber=200,
        DependsOn="PrivateNetworkAcl"
    ))

    template.add_resource(NetworkAclEntry(
        "PrivateNetworkAclEntryEgress"+env,
        CidrBlock=cidrBlock,
        Egress=True,
        NetworkAclId=Ref(privateNetworkAcl),
        Protocol=-1,
        RuleAction="allow",
        RuleNumber=200,
        DependsOn="PrivateNetworkAcl"
    ))

    for zone in zones:
        template.add_output(Output(
            "PublicSubnetOutput"+zone,
            Value=Ref("PublicSubnet"+zone),
            Export=Export(
                "PublicSubnet"+env+zone
            ),
        ))
        template.add_output(Output(
            "PrivateSubnetOutput"+zone,
            Value=Ref("PrivateSubnet"+zone),
            Export=Export(
                "PrivateSubnet"+env+zone
            )
        ))

    template.add_output(Output(
        "VPCOutput"+env,
        Value=Ref(vpc),
        Export=Export(
            "VPC"+env
        )
    ))

    return (template.to_json())



        






        
        



    