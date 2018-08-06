FROM openjdk:8

RUN apt-get update && \
    apt-get install -y groff

RUN git clone https://github.com/scm-spain/devops-test-helloworld-app.git && \
    curl --silent https://bootstrap.pypa.io/get-pip.py | python && \
    pip install awscli

ARG ENV
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG S3BUCKET
ARG DBPASSWORD
ARG DBHOST
ARG DBUSER
ARG DBNAME

WORKDIR ./devops-test-helloworld-app
ADD "./build.sh" /tmp/build.sh
RUN chmod +x /tmp/build.sh && \
    /tmp/build.sh
