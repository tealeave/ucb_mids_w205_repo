FROM mcr.microsoft.com/vscode/devcontainers/universal:latest

# 1) create group & user
RUN groupadd -g 1001 mids \
  && useradd -m -u 1001 -g 1001 -s /bin/bash w205 \
  \
  # 2) install sudo and allow passwordless sudo
  && apt-get update \
  && apt-get install -y sudo \
  && echo "w205 ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/w205 \
  && chmod 0440 /etc/sudoers.d/w205 \
  \
  # 3) give w205 ownership of the NVM install
  && chown -R w205:1001 /usr/local/share/nvm