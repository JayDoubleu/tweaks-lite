FROM ubuntu:latest

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-gi \
    python3-gi-cairo \
    python3-dbus \
    gir1.2-gtk-4.0 \
    libadwaita-1-0 \
    gir1.2-adw-1 \
    libadwaita-1-dev \
    dbus-x11 \
    libdbus-1-dev \
    libglib2.0-dev \
    python3-dev \
    python3-gi \
    libcairo2-dev \
    cmake \
    libgirepository1.0-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://github.com/astral-sh/uv/releases/download/0.1.24/uv-installer.sh | sh

# Create and activate virtual environment
ENV VIRTUAL_ENV=/app/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies using uv with full path
RUN /root/.cargo/bin/uv pip install pygobject && \
    /root/.cargo/bin/uv pip install -r tests/requirements-test.txt

# Command to run tests
CMD ["dbus-run-session", "--", "pytest", "tests/", "--cov=tweakslite", "--cov-report=xml:./coverage.xml"]
