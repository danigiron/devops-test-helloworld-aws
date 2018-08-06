import argparse, os, json, time, getpass, yaml, getpass
from __init__ import ArtifactBucket, roles, buildapp, buildAmi, buildNetwork, elb_asg_lc, database, subnetgroup

accessKey = os.environ.get('AWS_ACCESS_KEY_ID')
secretKey = os.environ.get('AWS_SECRET_ACCESS_KEY')

def get_args():
    """Parameters"""
    parser = argparse.ArgumentParser(
        description="Arguments to modify Json file"

    )
    parser.add_argument('--action',
                        required=True,
                        action='store',
                        help='Enter the action (create or delete)'),
    parser.add_argument('--resource',
                        required=True,
                        action='store',
                        help='Enter the resource to build (all | deploy | database | network)'),
    parser.add_argument('--env',
                        required=True,
                        action='store',
                        help='Enter environment (prod)')

    args = parser.parse_args()

    return args

def deploy(env, action):

    buildapp(env,action)
    buildAmi(env,action)
    roles(env,action)
    elb_asg_lc(env,action)

def removeAllResources(env,action):
    elb_asg_lc(env,action)
    buildAmi(env,action)
    buildapp(env,action)
    roles(env,action)
    database(env,action)
    subnetgroup(env,action)
    ArtifactBucket(env,action)
    buildNetwork(env,action)

def allResources(env,action):
    
    buildNetwork(env,action)
    ArtifactBucket(env,action)
    subnetgroup(env,action)
    database(env,action)
    buildapp(env,action)
    roles(env,action)
    buildAmi(env,action)
    elb_asg_lc(env,action)

def network(env,action):

    buildNetwork(env,action)

def databases(env,action):

    network(env,action)
    ArtifactBucket(env,action)
    subnetgroup(env,action)
    database(env,action)

def switcher (env,action,resources):

    if action == 'delete':
        removeAllResources(env,action)
    elif action == 'create':
        if resources == 'all':
            allResources(env,action)
        elif resources == 'deploy':
            deploy(env,action)
        elif resources == 'database':
            databases(env,action)
        elif resources == 'network':
            network(env,action)

    
def checkparams (env,action,resources):

    if not os.path.isfile(env+".yml"):
        print("File "+env+".yml doesn't exists")
        exit
    if action != 'delete' and action != 'create':
        print("Action "+action+" not allowed. Only allowed as actions delete or create")
        exit
    if resources != 'database' and resources != 'all' and resources != 'deploy' and resources != 'network':
        print ("Resource "+resources+" not allowed. Resources allowed: all, database")
        exit

def main():

    args = get_args()

    checkparams(args.env,args.action,args.resource)

    switcher(args.env,args.action,args.resource)

if __name__ == '__main__':
    main()
