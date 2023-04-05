FROM ubuntu:22.04
RUN /bin/sh -c set -xe \ 
    && echo '#!/bin/sh' > /usr/sbin/policy-rc.d \
    && echo 'exit 101' >> /usr/sbin/policy-rc.d \
    && chmod +x /usr/sbin/policy-rc.d \
    && dpkg-divert --local --rename --add /sbin/initctl \
    && cp -a /usr/sbin/policy-rc.d /sbin/initctl \
    && sed -i 's/^exit.*/exit 0/' /sbin/initctl \		
    && echo 'force-unsafe-io' > /etc/dpkg/dpkg.cfg.d/docker-apt-speedup \
    && echo 'DPkg::Post-Invoke { "rm -f /var/cache/apt/archives/*.deb /var/cache/apt/archives/partial/*.deb /var/cache/apt/*.bin || true"; };' > /etc/apt/apt.conf.d/docker-clean \
    && echo 'APT::Update::Post-Invoke { "rm -f /var/cache/apt/archives/*.deb /var/cache/apt/archives/partial/*.deb /var/cache/apt/*.bin || true"; };' >> /etc/apt/apt.conf.d/docker-clean \	
    && echo 'Dir::Cache::pkgcache ""; Dir::Cache::srcpkgcache "";' >> /etc/apt/apt.conf.d/docker-clean 	\
    && echo 'Acquire::Languages "none";' > /etc/apt/apt.conf.d/docker-no-languages 	\
    && echo 'Acquire::GzipIndexes "true"; Acquire::CompressionTypes::Order:: "gz";' > /etc/apt/apt.conf.d/docker-gzip-indexes \
    && echo 'Apt::AutoRemove::SuggestsImportant "false";' > /etc/apt/apt.conf.d/docker-autoremove-suggests
RUN rm -rf /var/lib/apt/lists/*
RUN mkdir -p /run/systemd && echo 'docker' > /run/systemd/container
RUN  apt-get update --fix-missing \
     && apt-get install -y git \
     && apt-get install -y build-essential gfortran \
     && apt-get install -y ssh time 
RUN cd /home/ && wget https://www2.mmm.ucar.edu/people/bryan/cm1/cm1r20.3.tar.gz \
    && tar xvf cm1r20.3.tar.gz
RUN cd /home/ && git clone https://github.com/raijenki/hpc-tests.git \
    && cp /home/hpc-tests/cm1/Makefile /home/cm1r20.3/src/. \
    && cd /home/cm1r20.3/src && make -j \
    && cp /home/cm1r20.3/run/cm1.exe /home/

FROM alpine:latest  
RUN apk --no-cache add ca-certificates
RUN apk add git
WORKDIR /home/
RUN git clone http://github.com/raijenki/hpc-tests.git
COPY --from=0 /home/cm1.exe ./hpc-tests/cm1/
CMD mkdir -p /var/run/sshd; /usr/sbin/sshd;
