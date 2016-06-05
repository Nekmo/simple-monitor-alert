FROM ubuntu:12.04
RUN apt-get update
RUN apt-get install -y python python-pip git sudo
COPY tests.sh /tmp/tests.sh
CMD bash /tmp/tests.sh
