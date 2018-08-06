from troposphere import GetAtt, Output, Ref, Template, Export
from troposphere.rds import DBSubnetGroup

def subnetGroupTemplate(name,app,env,subnetsIdsList):

    template = Template()

    subnetgroup = template.add_resource(DBSubnetGroup(
        "DBSubnetGroup"+name+app+env,
        DBSubnetGroupDescription="Subnet Group for"+env,
        SubnetIds=subnetsIdsList
    ))

    template.add_output(Output(
        "SubnetGroup"+name+env,
        Description="SubnetGroup"+env,
        Value=Ref(subnetgroup),
        Export=Export(
            name+env
        )
    ))

    return(template.to_json())
