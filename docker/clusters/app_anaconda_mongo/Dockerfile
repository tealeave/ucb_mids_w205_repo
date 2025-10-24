FROM mcr.microsoft.com/vscode/devcontainers/universal:latest

# Set DEBIAN_FRONTEND to noninteractive to avoid prompts during apt-get install
ENV DEBIAN_FRONTEND=noninteractive

# Section 1: Create non-root user w205, install sudo, and core development tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        sudo \
        git \
        curl \
        build-essential \
        libssl-dev \
        zlib1g-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        llvm \
        libncurses5-dev \
        libncursesw5-dev \
        xz-utils \
        tk-dev \
    # Create group and user (check if group exists first)
    && (getent group 1001 > /dev/null || groupadd -g 1001 mids) \
    # Set home directory to /home/w205 for user w205
    && useradd -m -u 1001 -g 1001 -s /bin/bash w205 \
    # Setup sudo for w205
    && echo "w205 ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/w205 \
    && chmod 0440 /etc/sudoers.d/w205 \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Section 2: Install VS Code CLI from Microsoft repository
RUN apt-get update \
    # Install prerequisites for adding new repositories
    && apt-get install -y --no-install-recommends \
        wget \
        gpg \
        apt-transport-https \
    # Add Microsoft GPG key
    && wget -qO- https://packages.microsoft.com/keys/microsoft.asc \
        | gpg --dearmor > /usr/share/keyrings/packages.microsoft.gpg \
    # Add VS Code repository
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" \
        > /etc/apt/sources.list.d/vscode.list \
    # Update package list again after adding new repo
    && apt-get update \
    # Install VS Code CLI
    && apt-get install -y --no-install-recommends code \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    # Optional: remove the prerequisite packages if no longer needed
    && apt-get purge -y --auto-remove wget apt-transport-https gpg \
    && rm -rf /var/lib/apt/lists/*

# Reset DEBIAN_FRONTEND if necessary
# ENV DEBIAN_FRONTEND=

# Section 3: Configure NVM Ownership
USER root
# Ensure the w205 user owns the NVM directory for managing Node.js versions.
RUN if [ -d /usr/local/share/nvm ]; then \
        chown -R w205:1001 /usr/local/share/nvm; \
    fi

# Section 4: Install MongoDB client and SSH client utilities
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        wget \
        gnupg \
        openssh-client \
    # Add MongoDB repository
    && wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add - \
    && echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" > /etc/apt/sources.list.d/mongodb-org-6.0.list \
    # Update package list after adding MongoDB repo
    && apt-get update \
    # Install MongoDB client tools
    && apt-get install -y --no-install-recommends \
        mongodb-mongosh \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get purge -y --auto-remove wget gnupg

# Section 5: Setup Zsh, Oh My Zsh, Powerlevel10k, and plugins for user w205
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        zsh \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    # Set Zsh as default shell for the w205 user
    && chsh -s $(which zsh) w205

# Switch to w205 user for user-specific setup
USER w205
RUN \
    # Install Oh My Zsh
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended && \
    \
    # Install Powerlevel10k theme
    git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${HOME}/.oh-my-zsh/custom/themes/powerlevel10k && \
    \
    # Install zsh-autosuggestions plugin
    git clone https://github.com/zsh-users/zsh-autosuggestions ${HOME}/.oh-my-zsh/custom/plugins/zsh-autosuggestions && \
    \
    # --- Configure .zshrc ---
    sed -i 's|^ZSH_THEME=.*|ZSH_THEME="powerlevel10k/powerlevel10k"|' ${HOME}/.zshrc && \
    sed -i 's|^plugins=(.*)|plugins=(git zsh-autosuggestions)|' ${HOME}/.zshrc && \
    echo '\n# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.' >> ${HOME}/.zshrc && \
    echo '[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh' >> ${HOME}/.zshrc

# Section 6: Set environment variables for services
ENV ANACONDA_HOST=anaconda \
    ANACONDA_PORT=8888 \
    MONGO_HOST=mongo \
    MONGO_PORT=27017

# Section 7: Final default user
USER w205