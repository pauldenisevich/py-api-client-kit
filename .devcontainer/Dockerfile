# syntax=docker/dockerfile:1

FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ENV DEBIAN_FRONTEND=noninteractive \
    UV_LINK_MODE=copy \
    UV_NO_WARNINGS=1

USER root

# The upstream devcontainer Python image may include a Yarn APT source.
# This project does not need Yarn/Node, and the Yarn repository key can break
# apt-get update, so remove Yarn sources before installing system packages.
RUN rm -f /etc/apt/sources.list.d/yarn.list \
          /etc/apt/sources.list.d/yarn*.list \
          /etc/apt/trusted.gpg.d/yarn*.gpg \
          /usr/share/keyrings/yarn*.gpg \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        bash-completion \
        build-essential \
        ca-certificates \
        curl \
        git \
        gnupg \
        less \
        make \
        nano \
        openssh-client \
        pkg-config \
        shellcheck \
        vim-tiny \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh \
    && chmod +x /usr/local/bin/uv \
    && uv --version

USER vscode

WORKDIR /workspaces
