#FROM hashicorp/packer:light
FROM ubuntu
ARG ENV
ARG S3ENDPOINT
ARG APP
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY


RUN apt-get update && apt-get install -y wget unzip && \
    wget https://releases.hashicorp.com/packer/1.2.5/packer_1.2.5_linux_amd64.zip && \
    unzip packer_1.2.5_linux_amd64.zip

ADD "./" /tmp/

RUN ./packer build -var "app=${APP}" -var "env=${ENV}" /tmp/Packer/gen-amis.json
