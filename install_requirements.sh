#!/bin/sh

apt install -y gcc-multilib g++-multilib python3-pip && \
mkdir -p /opt && \
cp -r bmap-1.0.20 /opt/bmap && \
cd /opt/bmap && \
make && make install && \
pip3 install -U cmd2