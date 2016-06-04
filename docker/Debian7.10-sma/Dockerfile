FROM debian:7.10
RUN apt-get update
RUN apt-get install -y python python-pip
RUN apt-get install -y git
COPY tests.sh /tmp/tests.sh
CMD bash /tmp/tests.sh
