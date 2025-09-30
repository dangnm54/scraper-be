FROM python:3.10-slim


# Set working directory -> create directory in container to store all code
WORKDIR /app


# Define specific versions for Edge and its driver for a reliable build
    # find edge version: search "microsoft-edge-stable debian version" or "https://packages.microsoft.com/repos/edge/pool/main/m/microsoft-edge-stable/"
    # find driver version: search "msedgedriver linux64 version" or "https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/?form=MA13LH"
ARG EDGE_VERSION="140.0.3485.81-1"
ARG DRIVER_VERSION="140.0.3485.81"


# Install system dependencies, a specific version of Edge, and the matching driver
RUN apt-get update && apt-get install -y \
    ca-certificates \
    wget \
    gnupg \
    curl \
    unzip \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    # Add Microsoft Edge repository
    && wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.gpg \
    && echo "deb [arch=amd64] https://packages.microsoft.com/repos/edge stable main" > /etc/apt/sources.list.d/microsoft-edge.list \
    # Install the pinned version of Edge
    && apt-get update \
    && apt-get install -y microsoft-edge-stable=${EDGE_VERSION} \
    # Download and install the pinned version of EdgeDriver
    && DRIVER_URL="https://msedgedriver.microsoft.com/${DRIVER_VERSION}/edgedriver_linux64.zip" \
    && echo "Downloading Edge Driver from: ${DRIVER_URL}" \
    && wget -O /tmp/edgedriver.zip "${DRIVER_URL}" \
    && unzip /tmp/edgedriver.zip -d /usr/local/bin/ \
    && rm /tmp/edgedriver.zip \
    # Clean up apt cache to reduce image size
    && rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/microsoft-edge.list


# Set display port to avoid crash
ENV DISPLAY=:99


# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Copy your code
COPY . .


# Command to run your app, main file is app.py
    # sh -> shell command
    # -c -> execute the command
    # uvicorn app:app --host 0.0.0.0 --port $PORT -> run the app
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port $PORT"]



# command --------------------------------------------

# docker build -t scraper-be .  ->  build or update image
# docker run --rm -p 8000:8000 --env-file .env.docker scraper-be  ->  run container from image, auto remove after stop
# docker container prune  ->  remove all old containers


# untrack file from git | remove file from git repo and untrack file