FROM python:3.7.13-alpine3.16

LABEL maintainer="verybadsoldier"
LABEL description="Gather statistics from iptables and ipset and publish via MQTT"
LABEL vcs-url="https://github.com/verybadsoldier/docker-iptables_stats"


RUN apk add build-base && \
    apk add libc6-compat && \
    apk add iptables && \
    apk add iptables-dev && \
    apk add ipset && \
    pip install iptables_stats==0.9.13 && \
    apk del build-base && \
    rm -rf /var/cache/apk/*

# some vars to also support loading correct dynamic libraries
ENV XTABLES_LIBDIR=/usr/lib/xtables
ENV PYTHON_IPTABLES_XTABLES_VERSION=12
ENV IPTABLES_LIBDIR=/usr/lib

CMD iptables_stats
