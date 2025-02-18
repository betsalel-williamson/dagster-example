FROM ubuntu

# use this Dockerfile to install additional tools you might need, e.g.
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        python3 `# for Dagster` \
        python3-pip `# for installing dependencies` \
        python3.12-venv `# for running the application in a virtual environment ` \
        build-essential `# For compiling native extensions, often needed.` \  
        git `# Essential for Gitpod` \              
        curl `# Useful for downloading resources/scripts.`

# Consider a non-root user if security is a concern (recommended)
RUN useradd -ms /bin/bash gitpoduser
USER gitpoduser
WORKDIR /workspace

ENV VIRTUAL_ENV=/workspace/.venv
RUN python3.12 -m venv $VIRTUAL_ENV
