FROM lsstsqre/centos:7-stack-lsst_distrib-w_2021_04

MAINTAINER Kenny Lo <kennylo@slac.stanford.edu>

# Add user for docker build/test/publish in jenkins
USER root
ARG USERNAME=jenkins
ARG UID=48435
ARG GID=202
RUN groupadd -g $GID -o $USERNAME
RUN useradd -m -u $UID -g $GID -o -s /bin/bash $USERNAME

# install JRE for sodalint
RUN yum -y install java-11-openjdk

# install redis
RUN yum -y install epel-release
RUN yum -y install redis

# Setup Dependencies
RUN /bin/bash -c 'source /opt/lsst/software/stack/loadLSST.bash; \
    LDFLAGS=-fno-lto conda install uwsgi'

# switch to lsst user
USER lsst
WORKDIR /app

COPY requirements.txt .
RUN /bin/bash -c 'source /opt/lsst/software/stack/loadLSST.bash; \
   pip install --no-cache-dir --user -r requirements.txt'

WORKDIR /src
ADD https://github.com/lsst-sqre/lsst-soda-service/archive/v0.0.3.tar.gz .


USER root
RUN /bin/bash -c 'tar zxvf v0.0.3.tar.gz'
RUN ln -s lsst-soda-service-0.0.3 lsst-soda-service
RUN ls
WORKDIR /src/lsst-soda-service

RUN /bin/bash -c 'source /opt/lsst/software/stack/loadLSST.bash; \
   setup lsst_distrib; \
   setup -k -r .; \
   scons'

USER lsst
WORKDIR /app

# Add the code in
COPY . /app
# Add /etc
COPY /rootfs /

RUN /bin/bash -c 'source /opt/lsst/software/stack/loadLSST.bash; \
   setup lsst_distrib; \
   setup -k -r /src/lsst-soda-service; \
   pip install --no-cache-dir --user .'

USER root
# remove unneeded stuff
RUN rm -rf /app/kube /app/integration /app/doc /app/Dockerfile

# run imgserv as lsst user
USER lsst

ENV UWSGI_THREADS=40
ENV UWSGI_PROCESSES=1
ENV UWSGI_OFFLOAD_THREADS=10
ENV UWSGI_WSGI_FILE=/app/bin/imageServer.py
ENV UWSGI_CALLABLE=app

# Start up the services
CMD ./bin/run_imgserv.sh
