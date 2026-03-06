#!/bin/bash
source /home/fastapiuser/anaconda3/etc/profile.d/conda.sh
conda activate netl-mwu-api-env && \
gunicorn --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:9090 \
-w 2 main:app --log-level debug