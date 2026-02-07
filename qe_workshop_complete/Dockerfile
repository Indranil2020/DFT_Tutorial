# =============================================================================
# Quantum ESPRESSO Workshop Docker Image
# =============================================================================
# This Dockerfile creates a complete environment for DFT calculations with
# Quantum ESPRESSO 7.5 compiled from source (bug-free) and Python tools.
#
# Build: docker build -t qe-workshop .
# Run:   docker run -p 8888:8888 -v $(pwd):/workspace qe-workshop
# =============================================================================

FROM ubuntu:22.04

LABEL maintainer="DFT Workshop"
LABEL description="Quantum ESPRESSO 7.5 Workshop Environment with Python Tools"

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# =============================================================================
# System packages and build dependencies
# =============================================================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build essentials
    build-essential \
    gfortran \
    # MPI for parallel calculations
    openmpi-bin \
    libopenmpi-dev \
    # Scientific libraries for QE
    liblapack-dev \
    libblas-dev \
    libopenblas-dev \
    libfftw3-dev \
    libscalapack-mpi-dev \
    # Python
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    # Utilities
    wget \
    curl \
    git \
    vim \
    less \
    ca-certificates \
    # For visualization/plotting
    libgl1-mesa-glx \
    libxrender1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# =============================================================================
# Compile Quantum ESPRESSO 7.5 from source
# =============================================================================
ENV QE_VERSION=7.5
ENV QE_DIR=/opt/qe

RUN cd /tmp && \
    wget https://github.com/QEF/q-e/archive/qe-${QE_VERSION}.tar.gz && \
    tar xzf qe-${QE_VERSION}.tar.gz && \
    cd q-e-qe-${QE_VERSION} && \
    ./configure --enable-parallel --with-scalapack && \
    make -j$(nproc) pw pp ph && \
    mkdir -p ${QE_DIR}/bin && \
    cp bin/* ${QE_DIR}/bin/ && \
    cd / && rm -rf /tmp/q-e-* /tmp/qe-*.tar.gz

# Add QE to PATH
ENV PATH="${QE_DIR}/bin:${PATH}"

# =============================================================================
# Python packages for computational materials science
# =============================================================================
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r /tmp/requirements.txt

# =============================================================================
# Additional packages that need special handling
# =============================================================================
# ALAMODE build dependencies + BoltzTraP2 (needs cmake for spglib wheel)
RUN apt-get update && apt-get install -y --no-install-recommends \
    cmake \
    libboost-all-dev \
    libeigen3-dev \
    libsymspg-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Build and install ALAMODE (alm, anphon)
RUN git clone --depth 1 https://github.com/ttadano/alamode.git /opt/alamode && \
    mkdir -p /opt/alamode/_build && \
    cd /opt/alamode/_build && \
    cmake -DSPGLIB_ROOT=/usr .. && \
    make -j$(nproc) && \
    cp /opt/alamode/_build/alm/alm /usr/local/bin/alm && \
    cp /opt/alamode/_build/anphon/anphon /usr/local/bin/anphon

# =============================================================================
# Set up working environment
# =============================================================================
WORKDIR /workspace

# Create directories for QE
RUN mkdir -p /workspace/tmp /workspace/pseudopotentials

# Environment variables for QE
ENV ESPRESSO_PSEUDO=/workspace/pseudopotentials
ENV OMP_NUM_THREADS=1

# Expose Jupyter port
EXPOSE 8888

# =============================================================================
# Default command: Start Jupyter Lab
# =============================================================================
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", \
     "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
