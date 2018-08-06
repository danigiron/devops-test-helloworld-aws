import boto3, psycopg2, random 
import argparse, os, json, time, yaml, getpass
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from subprocess import call
from troposphere import Template, Ref, GetAtt, Join, Output
from Resources.s3 import S3BucketTemplate
from Resources.vpc import vpcTemplate
from Resources.rds import databaseTemplate
from Resources.subnetgroup import subnetGroupTemplate
from Resources.roles import roleTemplate
from Resources.elb_asg_lc import elb_asg_lc_template
from Functions import getConfig, searchStacks, deployStack, awsClient, generatePassword, existsObject, getAmi, deleteStack
from simplecrypt import encrypt, decrypt

accessKey = os.environ.get('AWS_ACCESS_KEY_ID')
secretKey = os.environ.get('AWS_SECRET_ACCESS_KEY')

def ArtifactBucket(env,action):

    config = getConfig(env,"s3Artifact")
    globalConfig = getConfig(env,"Global")
    name = config['name']
    app = globalConfig['app']

    if action == 'create':
        s3Result = S3BucketTemplate(name,app,env)
        deployStack(name,app,env,s3Result)
    elif action == 'delete':
        deleteStack(name,app,env)
        

#    outputS3ArtifactEndpoint = searchStacks(name,app,env)
#
#    getS3ArtifactEndpoint = outputS3ArtifactEndpoint["Stacks"][0]["Outputs"][0]["OutputValue"]
#
#    return (getS3ArtifactEndpoint)

def roles (env,action):

    globalConfig = getConfig(env,"Global")
    app = globalConfig['app']
    configS3 = getConfig(env,"s3Artifact")
    config = getConfig(env,"role")
    name = config["name"]
    nameS3 = configS3['name']

    if action == 'create':
        roleResult = roleTemplate(app,env,nameS3)
        deployStack(name,app,env,roleResult)
    elif action == 'delete':
        deleteStack(name,app,env)

def buildapp (env,action):

    if action == 'delete':
        return None

    globalConfig = getConfig(env,"Global")
    config = getConfig(env,"Application")
    configS3 = getConfig(env,"s3Artifact")
    configRDS = getConfig(env,"Database")
    app = globalConfig['app']

    infoS3 = searchStacks(configS3['name'],app,env)
    infoDB = searchStacks(configRDS['name'],app,env)
    ArtifactEndpoint = infoS3["Stacks"][0]["Outputs"][0]["OutputValue"]
    EncryptPassword = getpass.getpass('Encrypt Password:')

    for output in infoDB['Stacks'][0]['Outputs']:
        if output['OutputKey'] == "DatabaseHostdbhelloWorldprod":
            hostDB = output['OutputValue'] 

    if existsObject(ArtifactEndpoint,"database/secret.txt"):
        connect = awsClient('s3')
        s3 = boto3.resource('s3')
        object = s3.Object(ArtifactEndpoint,"database/secret.txt")
        test = object.get()['Body'].read()
        plainSecret = decrypt(EncryptPassword,test)
    else:
        print("Error. The secret doesn't exist. Build first the database function")
        exit
    
    result = call([
        "docker",
        "build",
        "--no-cache",
        "--build-arg",
        "AWS_ACCESS_KEY_ID="+accessKey,
        "--build-arg",
        "AWS_SECRET_ACCESS_KEY="+secretKey,
        "--build-arg",
        "ENV="+env,
        "--build-arg",
        "S3BUCKET="+ArtifactEndpoint,
        "--build-arg",
        "DBPASSWORD="+plainSecret,
        "--build-arg",
        "DBHOST="+hostDB,
        "--build-arg",  
        "DBUSER="+configRDS['dbUser'],
        "--build-arg",
        "DBNAME="+configRDS['dbApp'],
        "./Docker/build"
    ])

    if result != 0:
        print ("ERROR building the application. See the output")
        exit
    else:
        print ("Build application succeeded")

def buildAmi (env, action):

    if action == 'delete':
        return None

    globalConfig = getConfig(env,"Global")
    configS3 = getConfig(env,"s3Artifact")
    app = globalConfig['app']
    infoS3 = searchStacks(configS3['name'],app,env)
    ArtifactEndpoint = infoS3["Stacks"][0]["Outputs"][0]["OutputValue"]
    configRole = getConfig(env,"role")
    roleName = configRole["name"]
    action = 'create'

    roleOutput = searchStacks(roleName,app,env)

    result = call([
        "docker",
        "build",
        "--no-cache",
        "--build-arg",
        "AWS_ACCESS_KEY_ID="+accessKey,
        "--build-arg",
        "AWS_SECRET_ACCESS_KEY="+secretKey,
        "--build-arg",
        "ENV="+env,
        "--build-arg",
        "S3ENDPOINT="+ArtifactEndpoint,
        "--build-arg",
        "APP="+app,
        "./Docker/amis"
    ])

    if result != 0:
        print ("ERROR building the application. See the output")
        exit
    else:
        print ("Build application succeeded")

def buildNetwork(env,action):

    globalConfig = getConfig(env,"Global")
    config = getConfig(env,"Network")
    name = config['name']
    app = globalConfig['app']
    cidrBlock = config['cidrBlock']
    publicSubnets = config['Public']
    privateSubnets = config['Private']

    if action == 'create':

        vpcResult = vpcTemplate(name,app,env,cidrBlock,publicSubnets,privateSubnets)
        deployStack(name,app,env,vpcResult)
    
    elif action == 'delete':
        deleteStack(name,app,env)


def elb_asg_lc(env,action, ami=None):

    globalConfig = getConfig(env,"Global")
    config = getConfig(env,"infra")
    configRDS = getConfig(env,"Database")
    configVPC = getConfig(env,"Network")
    configS3 = getConfig(env,"s3Artifact")
    nameVPC= configVPC['name']

    if action == 'create':

        getSubnets = searchStacks(nameVPC,globalConfig['app'],env)
        subnetsPubl = []
        for output in getSubnets['Stacks'][0]['Outputs']:
            if "Public" in output['OutputKey']:
                subnetsPubl.append(output['OutputValue'])

        if ami is None:
            ami = getAmi(globalConfig['app'])

        elbAsgLcResult = elb_asg_lc_template(
            globalConfig["app"],
            env,configRDS["name"],
            configRDS["port"],
            config["lc"]["instanceType"],
            ami,
            subnetsPubl,
            config['elb']['port'],
            config['elb']['cidrBlock'],
            config['asg']['port'],
            config['asg']['desiredCapacity'],
            config['asg']['minSize'],
            config['asg']['maxSize'],
            globalConfig['region'],
            configS3['name'],
            globalConfig['OfficeIP']
            )


        deployStack (config['name'],globalConfig["app"],env,elbAsgLcResult)

    elif action == 'delete':
        deleteStack(config['name'],globalConfig["app"],env)

def database(env,action):

    globalConfig = getConfig(env,"Global")
    config = getConfig(env,"Database")
    configVPC = getConfig(env,"Network")
    nameVPC= configVPC['name']
    configSubnetGroup = getConfig(env,"SubnetGroup")
    configS3 = getConfig(env,"s3Artifact")

    name = config['name']
    app = globalConfig['app']
    engine = config['engine']
    version = config['version']
    storageSize = config['storageSize']
    instanceSize = config['instanceSize']
    port = config['port']
    dbApp = config['dbApp']
    dbUser = config['dbUser']
    dbAdmin = config['dbAdmin']
    officeIP = globalConfig['OfficeIP']

    nameSubnetGroupPriv = configSubnetGroup['Private']['name']
    nameSubnetGroupPubl = configSubnetGroup['Public']['name']

    if action == 'create':
        password = getpass.getpass('Database Password:')
        EncryptPassword = getpass.getpass('Encrypt Password:')
        S3Connect = awsClient('s3')

        rdsResult = databaseTemplate(name,app,env,engine,version,storageSize,instanceSize,password,port,officeIP,dbAdmin,nameSubnetGroupPubl,dbApp)

        deployStack (name,app,env,rdsResult)

        infoDB = searchStacks(name,app,env)
        infoS3 = searchStacks(configS3['name'],app,env)

        ArtifactEndpoint = infoS3["Stacks"][0]["Outputs"][0]["OutputValue"]
        #print ArtifactEndpoint

        for output in infoDB['Stacks'][0]['Outputs']:
            if output['OutputKey'] == "DatabaseHostdbhelloWorldprod":
                hostDB = output['OutputValue']

        if existsObject(ArtifactEndpoint,"database/secret.txt"):
            print("User "+dbUser+" already exists")
        else:
            print("Creating user for app "+app)
            appPassword = generatePassword()
            ciphertext = encrypt(EncryptPassword, appPassword)
            dbConnect = psycopg2.connect(dbname='postgres',user=dbAdmin,password=password,host=hostDB)
            cur = dbConnect.cursor()
            dbConnect.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

            cur.execute("CREATE USER {dbUser} WITH PASSWORD '{appPassword}';".format(dbUser=dbUser,appPassword=appPassword))
            cur.execute("GRANT ALL PRIVILEGES ON DATABASE {dbApp} TO {dbUser};".format(dbApp=dbApp,dbUser=dbUser))

            S3Connect.put_object(
                Body=ciphertext,
                Bucket=ArtifactEndpoint,
                Key="database/secret.txt"
            )
    elif action == 'delete':
        deleteStack(name,app,env)


def subnetgroup(env,action):

    globalConfig = getConfig(env,"Global")
    config = getConfig(env,"SubnetGroup")
    configVPC = getConfig(env,"Network")
    nameVPC= configVPC['name']

    namePriv = config['Private']['name']
    namePubl = config['Public']['name']

    app = globalConfig['app']

    if action == 'create':
        getSubnets = searchStacks(nameVPC,app,env)
        subnetsPriv = []
        for output in getSubnets['Stacks'][0]['Outputs']:
            if "Private" in output['OutputKey']:
                subnetsPriv.append(output['OutputValue'])

        subnetsPubl = []
        for output in getSubnets['Stacks'][0]['Outputs']:
            if "Public" in output['OutputKey']:
                subnetsPubl.append(output['OutputValue'])

        subnetGroupResultPriv = subnetGroupTemplate(namePriv,app,env,subnetsPriv)
        subnetGroupResultPubl = subnetGroupTemplate(namePubl,app,env,subnetsPubl)

        deployStack (namePriv,app,env,subnetGroupResultPriv)
        deployStack (namePubl,app,env,subnetGroupResultPubl)
    elif action == 'delete':
        deleteStack (namePriv,app,env)
        deleteStack (namePubl,app,env)

