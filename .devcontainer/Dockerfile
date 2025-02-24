FROM ubuntu

# use this Dockerfile to install additional tools you might need, e.g.
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        python3 `# for Dagster` \
        python3-pip `# for installing dependencies` \
        python3.12-venv `# for running the application in a virtual environment ` \
        build-essential `# For compiling native extensions, often needed.` \  
        git `# Essential for Gitpod` \              
        curl `# Useful for downloading resources/scripts.` \
        && rm -rf /var/lib/apt/lists/*

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install \
        libglib2.0-0t64 \
        libnss3 \
        libnspr4 \
        libdbus-1-3 \
        libatk1.0-0t64 \
        libatk-bridge2.0-0t64 \
        libatspi2.0-0t64 \
        libx11-6 \
        libxcomposite1 \
        libxdamage1 \
        libxext6 \
        libxfixes3 \
        libxrandr2 \
        libgbm1 \
        libxcb1 \
        libxkbcommon0 \
        libasound2t64 \
        && rm -rf /var/lib/apt/lists/*

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install \
        libcups2t64 \
        libpango-1.0-0 \
        libcairo2 \
        && rm -rf /var/lib/apt/lists/*        

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install \
        libxcursor1 \
        libgtk-3-0t64 \
        libpangocairo-1.0-0 \
        libcairo-gobject2 \
        libgdk-pixbuf-2.0-0 \
        && rm -rf /var/lib/apt/lists/*              

# Consider a non-root user if security is a concern (recommended)
RUN useradd -ms /bin/bash gitpoduser
USER gitpoduser
WORKDIR /workspace

ENV VIRTUAL_ENV=/workspace/.venv
RUN python3.12 -m venv $VIRTUAL_ENV
