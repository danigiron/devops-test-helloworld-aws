#!/bin/bash

sudo sed -i "s/%BUCKETNAME%/${S3ENDPOINT}/g" /etc/td-agent/td-agent.conf

artifact=`aws s3 ls s3://${S3ENDPOINT}/app/ | sort | tail -n1 | awk '{print $NF}'`

aws s3 cp s3://${S3ENDPOINT}/app/$artifact /tmp/helloworld.jar

sudo cp /tmp/helloworld.jar /var/app/

sudo chmod +x /var/app/helloworld.jar

rm -f /tmp/helloworld.jar



