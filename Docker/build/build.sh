#!/bin/bash

if [[ -z ${ENV} ]]; then
    echo "Variable ENV doesn't exist" >&2
    exit 1
fi

if [[ ${ENV} -eq "prod" ]]; then
    sed -i "s/password\:/password\:\ "${DBPASSWORD}"/g" src/main/resources/application-pro.yml
    sed -i "s/helloworld.database.lan.*/"${DBHOST}"\:5432\/${DBNAME}\"/g" src/main/resources/application-pro.yml
    sed -i "s/username\:.*/username\:\ ${DBUSER}/g" src/main/resources/application-pro.yml
    ./gradlew build
    aws s3 cp build/libs/* s3://${S3BUCKET}/app/

fi
