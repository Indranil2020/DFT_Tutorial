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
    libsymspg-dev\
    autoconf \
    automake \
    libtool \
    libtool-bin \
    libltdl-dev \
    # Python
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    # Utilities
    wget \
    curl \
    unzip \
    git \
    vim \
    less \
    ca-certificates \
    # For visualization/plotting
    libgl1-mesa-glx \
    libxrender1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
# 2. Manually install CMake 3.30 (Binary) to /usr/local
# This ensures we have a real binary (not a python wrapper) that is version > 3.25
RUN wget -qO- https://github.com/Kitware/CMake/releases/download/v3.30.0/cmake-3.30.0-linux-x86_64.tar.gz | \
    tar --strip-components=1 -xz -C /usr/local
# =============================================================================
# Build libxc from source
# =============================================================================
ENV LIBXC_VERSION=6.2.2
ENV LIBXC_ROOT=/usr/local

RUN cd /tmp && \
    wget https://gitlab.com/libxc/libxc/-/archive/${LIBXC_VERSION}/libxc-${LIBXC_VERSION}.tar.gz && \
    tar xzf libxc-${LIBXC_VERSION}.tar.gz && \
    cd libxc-${LIBXC_VERSION} && \
    autoreconf -i && \
    ./configure --prefix=${LIBXC_ROOT} --enable-shared --enable-static && \
    make -j$(nproc) && \
    make install && \
    ldconfig && \
    rm -rf /tmp/libxc-*

# =============================================================================

# =============================================================================
# Compile Quantum ESPRESSO 7.5 from source
# =============================================================================
ENV QE_VERSION=7.5
ENV QE_DIR=/opt/qe

RUN cd /tmp && \
    wget https://github.com/QEF/q-e/archive/qe-${QE_VERSION}.tar.gz && \
    tar xzf qe-${QE_VERSION}.tar.gz && \
    cd q-e-qe-${QE_VERSION} && \
    ./configure \
        --prefix=${QE_DIR} \
        --enable-parallel \
        --with-scalapack=yes \
        --with-libxc=yes \
        --with-libxc-prefix=${LIBXC_ROOT} \
        FC=mpif90 \
        CC=gcc \
        FFLAGS="-O2 -D_FORTIFY_SOURCE=2 -I${LIBXC_ROOT}/include -fallow-argument-mismatch" \
        CFLAGS="-O2 -D_FORTIFY_SOURCE=2 -I${LIBXC_ROOT}/include" && \ 
    make -j$(nproc) pw pp ph && \
    make install && \
    ldconfig && \
    cp bin/* ${QE_DIR}/bin/ && \
    cd / && rm -rf /tmp/q-e-* /tmp/qe-*.tar.gz

# Add QE to PATH
ENV PATH="${QE_DIR}/bin:${PATH}"

# =============================================================================
# Python packages for computational materials science
# =============================================================================
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir --upgrade pip && \
    # Install modern CMake via pip (provides version > 3.25)
    # pip3 install --no-cache-dir "cmake>=3.26" && \
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
