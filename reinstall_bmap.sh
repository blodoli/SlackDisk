#!/bin/sh

rm -r /opt/bmap && cp -r bmap-1.0.20 /opt/bmap && cd /opt/bmap && make && make install
pip3 install -U cmd2