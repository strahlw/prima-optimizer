# pull official base image
# tested successfully with version 24.5.11
FROM continuumio/miniconda3:latest

# set work directory
WORKDIR /usr/src/app

# set environment variables
# Ensure that output from python is written straight to stdout and stderr
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/usr/src/app

WORKDIR /usr/src/app/api_install_files
RUN conda install python=3.11
COPY requirements-dev.txt /usr/src/app/api_install_files
COPY requirements.txt /usr/src/app/api_install_files
RUN pip install -r requirements-dev.txt

WORKDIR /usr/src/app
COPY primo-optimizer /usr/src/app/primo-optimizer
# create the conda environment
RUN conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
RUN conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

RUN conda env update --name base --file primo-optimizer/conda-env.yml

# mount the app folder
RUN --mount=type=bind,source=.,target=/usr/src/app
