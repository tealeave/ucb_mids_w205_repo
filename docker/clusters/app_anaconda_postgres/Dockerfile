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

# Reset DEBIAN_FRONTEND if necessary, though for subsequent non-interactive steps it's often fine to leave it
# ENV DEBIAN_FRONTEND=

# Section 3: Configure NVM Ownership
USER root
# Ensure the w205 user owns the NVM directory for managing Node.js versions.
# The GID 1001 corresponds to the 'mids' group for the w205 user.
# This command assumes /usr/local/share/nvm exists in the base image.
RUN if [ -d /usr/local/share/nvm ]; then \
        chown -R w205:1001 /usr/local/share/nvm; \
    fi

# Section 4: Install PostgreSQL and SSH client utilities
# These commands are run as root (implicitly, following the 'USER root' in Section 3).
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        openssh-client \
    # Clean up apt caches to reduce image size
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Section 5: Setup Zsh, Oh My Zsh, Powerlevel10k, and plugins for user w205

# Install Zsh and set it as default shell for w205
# Prerequisites: git and curl should be installed from Section 1 or base image.
# Note: fonts-powerline has been removed. For Powerlevel10k to render all symbols correctly,
# ensure a Nerd Font is installed and configured in your host terminal application.
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        zsh \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    # Set Zsh as default shell for the w205 user (moved after cleanup)
    && chsh -s $(which zsh) w205

# Switch to w205 user for user-specific setup
USER w205
RUN \
    # Install Oh My Zsh (non-interactively)
    # This script will also create/modify $HOME/.zshrc
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended && \
    \
    # Install Powerlevel10k theme for Oh My Zsh
    # Oh My Zsh's installer should create the .oh-my-zsh/custom directory.
    git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${HOME}/.oh-my-zsh/custom/themes/powerlevel10k && \
    \
    # Install zsh-autosuggestions plugin for Oh My Zsh
    git clone https://github.com/zsh-users/zsh-autosuggestions ${HOME}/.oh-my-zsh/custom/plugins/zsh-autosuggestions && \
    \
    # --- Configure .zshrc ---
    # Set ZSH_THEME to Powerlevel10k. The Oh My Zsh installer usually sets a default.
    sed -i 's|^ZSH_THEME=.*|ZSH_THEME="powerlevel10k/powerlevel10k"|' ${HOME}/.zshrc && \
    \
    # Set desired plugins. Oh My Zsh installer typically sets 'plugins=(git)'.
    # This replaces the entire plugins line to ensure a specific set.
    sed -i 's|^plugins=(.*)|plugins=(git zsh-autosuggestions)|' ${HOME}/.zshrc && \
    \
    # Add Powerlevel10k instant prompt initialization to .zshrc
    # (This is often recommended by Powerlevel10k itself for speed)
    echo '\n# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.' >> ${HOME}/.zshrc && \
    echo '[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh' >> ${HOME}/.zshrc

# Section 6: Set environment variables for services
ENV ANACONDA_HOST=anaconda \
    ANACONDA_PORT=8888 \
    POSTGRES_HOST=postgres \
    POSTGRES_PORT=5432

# Section 7: Final default user
USER w205
