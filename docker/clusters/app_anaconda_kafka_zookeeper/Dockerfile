# Dev‑container base (same as your existing app image)
FROM mcr.microsoft.com/vscode/devcontainers/universal:latest

ENV DEBIAN_FRONTEND=noninteractive

# ─────────── 1. core tools + user ───────────
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        sudo git curl build-essential \
        libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
        libsqlite3-dev llvm libncurses5-dev libncursesw5-dev \
        xz-utils tk-dev && \
    groupadd -g 1001 mids || true && \
    useradd -m -u 1001 -g 1001 -s /bin/bash w205 && \
    echo "w205 ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/w205 && \
    chmod 0440 /etc/sudoers.d/w205 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ─────────── 2. VS Code CLI ───────────
RUN apt-get update && \
    apt-get install -y --no-install-recommends wget gpg apt-transport-https && \
    wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/packages.microsoft.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" \
      > /etc/apt/sources.list.d/vscode.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends code && \
    apt-get purge -y --auto-remove wget gpg apt-transport-https && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ─────────── 3. optional extras ───────────
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        postgresql-client openssh-client zsh && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    chsh -s $(which zsh) w205

USER w205

# Oh‑My‑Zsh, Powerlevel10k, plugins
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended && \
    git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ~/.oh-my-zsh/custom/themes/powerlevel10k && \
    git clone https://github.com/zsh-users/zsh-autosuggestions ~/.oh-my-zsh/custom/plugins/zsh-autosuggestions && \
    sed -i 's/^ZSH_THEME=.*/ZSH_THEME="powerlevel10k\/powerlevel10k"/' ~/.zshrc && \
    sed -i 's/^plugins=(.*)/plugins=(git zsh-autosuggestions)/' ~/.zshrc && \
    echo '\n[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh' >> ~/.zshrc

# ─────────── 4. helpful env vars ───────────
ENV ANACONDA_HOST=anaconda \
    ANACONDA_PORT=8888 \
    KAFKA_HOST=kafka \
    KAFKA_PORT=29092 \
    ZOOKEEPER_HOST=zookeeper \
    ZOOKEEPER_PORT=32181

# Default to non‑root user
CMD ["sleep", "infinity"]
