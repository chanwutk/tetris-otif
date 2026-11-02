FROM nvidia/cuda:12.8.1-cudnn-devel-ubuntu22.04

RUN sed -i 's/#force_color_prompt=yes/force_color_prompt=yes/g' ~/.bashrc

# Set the working directory
WORKDIR /otif

ARG DEBIAN_FRONTEND=noninteractive

# Install Conda
RUN apt-get -qq update && apt-get -qq -y install curl bzip2 \
    && curl -sSL https://repo.continuum.io/miniconda/Miniconda3-py37_4.10.3-Linux-x86_64.sh -o /tmp/miniconda.sh \
    && bash /tmp/miniconda.sh -bfp /usr/local \
    && rm -rf /tmp/miniconda.sh \
    # && conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main \
    # && conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r \
    # && conda install -y python=3 \
    && conda update conda \
    && apt-get -qq -y remove curl bzip2 \
    && apt-get -qq -y autoremove --purge \
    && apt-get -qq -y autoclean \
    && rm -rf /var/lib/apt/lists/* /var/log/dpkg.log \
    && conda clean --all --yes

# Install dependencies
RUN apt-get -qq update -y && \
    apt-get -qq -y install --no-install-recommends \
    build-essential \
    git \
    golang \
    ffmpeg \
    curl \
    make && \
    rm -rf /var/lib/apt/lists/*

# Ensure full CUDA toolkit for darknet (for nvcc and build tools)
RUN apt-get update && apt-get install -y cuda-toolkit-12-8 && rm -rf /var/lib/apt/lists/*

ENV LD_LIBRARY_PATH="/usr/local/cuda-12.8/lib64:${LD_LIBRARY_PATH}"
RUN apt-get update && apt-get install -y libcudnn8 libcudnn8-dev && rm -rf /var/lib/apt/lists/*


# Set up environemnts
ENV PATH="/usr/local/cuda/bin:${PATH}"
ENV LD_LIBRARY_PATH="/usr/local/cuda/lib64:${LD_LIBRARY_PATH}"
ENV PYTHONPATH="/otif/python:${PYTHONPATH}"

RUN conda init bash

COPY ./environment.yml /otif/environment.yml
RUN conda env update --file /otif/environment.yml --prune --name base && \
    conda clean --all --yes

COPY ./environment-retina.yml /otif/environment-retina.yml
RUN conda env create -f /otif/environment-retina.yml && \
    conda clean --all --yes

COPY ./requirements.txt /otif/requirements.txt
RUN conda run -n retinanet pip install --no-build-isolation -r /otif/requirements.txt

ENV PATH="/opt/conda/bin:${PATH}"
ENV CONDA_DEFAULT_ENV=base

# COPY ./requirements.txt /otif/requirements.txt
# RUN pip install --no-build-isolation -r /otif/requirements.txt

# RUN echo "127.0.0.1 host.docker.internal" | tee -a /etc/hosts
