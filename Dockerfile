FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive

COPY sources.list /etc/apt/sources.list

RUN apt update; \
    apt install -y build-essential wget libfontconfig1; \
    wget https://mirrors.tuna.tsinghua.edu.cn/CTAN/systems/texlive/tlnet/install-tl-unx.tar.gz; \
    mkdir /install-tl-unx; \
    tar -xvf install-tl-unx.tar.gz -C /install-tl-unx --strip-components=1; \
    echo "selected_scheme scheme-basic" >> /install-tl-unx/texlive.profile; \
    /install-tl-unx/install-tl -profile /install-tl-unx/texlive.profile; \
    rm -r /install-tl-unx install-tl-unx.tar.gz;

ENV PATH="/usr/local/texlive/2020/bin/x86_64-linux:${PATH}"

RUN tlmgr install xetex ctex
