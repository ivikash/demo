# Use the official Python 3.11 slim image as the base
FROM python:3.11-slim

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Set environment variables for Poetry configuration
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Install Poetry
RUN pip install poetry==1.8.3

# Install build dependencies and other utilities
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    curl \
    docker \
    git \
    htop \
    libssl-dev \
    lsof \
    make \
    neovim \
    tree \
    zsh \
    && rm -rf /var/lib/apt/lists/*

# Setup git secrets
RUN git clone https://github.com/awslabs/git-secrets
RUN cd git-secrets && make install

# Setup development environment if STAGE is set to "development"
ARG STAGE
RUN if [ "$STAGE" = "development" ]; then \
    # Install Lefthook for Git hooks management
    curl -1sLf 'https://dl.cloudsmith.io/public/evilmartians/lefthook/setup.deb.sh' | bash && \
    apt install lefthook -y && \
    # Install Antigen for managing Zsh plugins
    curl -L git.io/antigen > ~/antigen.zsh && \
    # Clone Zsh Autosuggestions plugin
    git clone https://github.com/zsh-users/zsh-autosuggestions $HOME/.zsh/zsh-autosuggestions && \
    # Configure Zsh with Antigen and various plugins
    printf "source ~/antigen.zsh \n \
    antigen use oh-my-zsh \n \
    antigen bundle git \n \
    antigen bundle pip \n \
    antigen bundle command-not-found \n \
    antigen bundle zsh-users/zsh-syntax-highlighting \n \
    antigen bundle zsh-users/zsh-autosuggestions \n \
    source ~/.zsh/zsh-autosuggestions/zsh-autosuggestions.zsh \n \
    antigen theme https://github.com/denysdovhan/spaceship-prompt spaceship \n \
    antigen apply" > /root/.zshrc; \
    fi

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Poetry Install
RUN poetry install --no-interaction --no-root
