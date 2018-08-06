from troposphere import Output, Ref, Template, Join, GetAtt, Export
from troposphere.s3 import Bucket, PublicRead, BucketPolicy

def S3BucketTemplate(name,app,env):
    template=Template()

    s3Bucket = template.add_resource(Bucket(
        "S3Bucket"+name+app+env,
    ))
    output = template.add_output(Output(
    "Bucket"+name+app+env,
    Value=Ref("S3Bucket"+name+app+env),
    Export=Export("Bucket"+name+app+env)
    ))

    return(template.to_json())



