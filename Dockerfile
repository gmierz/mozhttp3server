# build ns-3 (from https://github.com/marten-seemann/quic-network-simulator/blob/master/sim/Dockerfile)
FROM ubuntu:20.04 AS builder

RUN apt-get update && \
  DEBIAN_FRONTEND=noninteractive apt-get install -y python3 build-essential cmake wget

RUN wget https://www.nsnam.org/release/ns-allinone-3.30.1.tar.bz2 && \
  tar xjf ns-allinone-3.30.1.tar.bz2 && \
  rm ns-allinone-3.30.1.tar.bz2

WORKDIR /ns-allinone-3.30.1/ns-3.30.1

RUN mkdir out/
RUN ./waf configure --build-profile=optimized --out=out/
RUN ./waf build

# make including of the QuicNetworkSimulatorHelper class possible
COPY wscript.patch .
RUN patch < wscript.patch

RUN rm -r scratch/subdir scratch/scratch-simulator.cc
COPY throttling scratch/

# compile all the scenarios
RUN ./waf build  && \
  cd out/lib && du -sh . && strip -v * && du -sh . && cd ../.. && \
  cd out/scratch && rm -r subdir helper scratch-simulator*

# http/3 app + network throttler
FROM ubuntu:bionic 

USER root
SHELL [ "/bin/bash", "-c" ]

RUN apt update && \
    apt install -yq apt-utils software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt update && \
    apt upgrade -yq

RUN apt install -yq \
        libssl-dev \
        dumb-init \
        python3.8 \
        python3.8-dev \
        python3.8-venv \
        python3-distutils \
        sudo 

# grabbing ns3 from the previous build
WORKDIR /ns3
COPY --from=builder /ns-allinone-3.30.1/ns-3.30.1/out/lib/ /ns3/lib
COPY --from=builder /ns-allinone-3.30.1/ns-3.30.1/out/src/fd-net-device/*optimized /ns-allinone-3.30.1/ns-3.30.1/out/src/fd-net-device/*debug /ns3/src/fd-net-device/
COPY --from=builder /ns-allinone-3.30.1/ns-3.30.1/out/scratch/*/* /ns3/scratch/

RUN find /ns3

# setting up a docker user
RUN useradd -m docker && \
    usermod -aG sudo docker && \
    echo '%sudo ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers && \
    cp /root/.bashrc /home/docker/ && \
    mkdir /home/docker/data && \
    chown -R --from=root docker /home/docker

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

WORKDIR /home/docker/data
ENV HOME /home/docker
ENV USER docker
USER docker
RUN touch $HOME/.sudo_as_admin_successful

COPY setup.py /home/docker/data/
COPY mozhttp3server /home/docker/data/mozhttp3server

RUN python3.8 -m venv /home/docker/data
RUN bin/python setup.py develop

COPY launcher.py /home/docker/data
ENTRYPOINT ["python3.8", "/home/docker/data/launcher.py"]
CMD [ "server" ]
