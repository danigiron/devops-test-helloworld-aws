import yaml, boto3, time, botocore,json
import string,random



def getConfig (env,section):

    fileConfig = env+".yml"
    data=""
    
    with open(fileConfig, 'r') as config:
        data = yaml.load(config)
        config.close()

    return(data['Variables'][section])


def awsClient(resource):
    
    client = boto3.client(resource, region_name='eu-west-1')

    return client


def searchStacks (name,app,env):

    stack = awsClient('cloudformation')

    searchStack = stack.describe_stacks(
        StackName = name+"-"+app+"-"+env
    )

    return searchStack

def stackExists (nameStack):

    connect = awsClient('cloudformation')
    stacks = connect.list_stacks()['StackSummaries']
    for stack in stacks:
        if stack['StackStatus'] == 'DELETE_COMPLETE':
            continue
        if nameStack == stack['StackName']:
            return True
    return False

def deleteStack(name,app,env):

    stack = awsClient('cloudformation')

    if stackExists(name+"-"+app+"-"+env):
        if name == 'artifacts':
            print ("Removing all content of bucket")
            s3 = boto3.resource('s3')
            infoS3 = searchStacks(name,app,env)
            bucket = s3.Bucket(infoS3["Stacks"][0]["Outputs"][0]["OutputValue"])
            bucket.objects.all().delete()
        print("Removing stack "+name+"-"+app+"-"+env)
        stack.delete_stack(
            StackName = name+"-"+app+"-"+env,
        )
        waiter = stack.get_waiter('stack_delete_complete')
        print("...waiting for stack to be deleted...")
        waiter.wait(StackName=name+"-"+app+"-"+env)
    else:
        print ("Stack "+name+"-"+app+"-"+env+" doesn't exist")


def deployStack(name,app,env,jsonTemplate):

    stack = awsClient('cloudformation')
    try:
        if stackExists(name+"-"+app+"-"+env):
            print("Updating Stack "+name+"-"+app+"-"+env)
            stack_result = stack.update_stack(
                StackName = name+"-"+app+"-"+env,
                TemplateBody = jsonTemplate,
                Capabilities = [
                    'CAPABILITY_NAMED_IAM',
                ]
            )
            waiter = stack.get_waiter('stack_update_complete')
        else:
            print ("Creating stack: "+name+"-"+app+"-"+env )
            stack_result = stack.create_stack(
                StackName = name+"-"+app+"-"+env,
                TemplateBody = jsonTemplate,
                Capabilities = [
                    'CAPABILITY_NAMED_IAM',
                ]
            )
            waiter = stack.get_waiter('stack_create_complete')
        print("...waiting for stack to be ready...")
        waiter.wait(StackName=name+"-"+app+"-"+env)
    except botocore.exceptions.ClientError as ex:
        error_message = ex.response['Error']['Message']
        if error_message == 'No updates are to be performed.':
            print("No changes")
        else:
            raise

def generatePassword(size=10,chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for i in range(size))

def existsObject(BucketName,path):

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(BucketName)
    objs = list(bucket.objects.filter(Prefix=path))

    if len(objs) > 0 and objs[0].key == path:
        return True
    else:
        return False

def getAmi(name):

    connect = awsClient('ec2')

    listImages = connect.describe_images(
        Filters = [
            {'Name': 'name', 'Values': [name+'*']},
            {'Name': 'state', 'Values': ['available']}
        ]
    )

    amis = sorted(
        listImages['Images'],key=lambda x: x['CreationDate'],
        reverse=True
        )
    return amis[0]['ImageId']
