#!/bin/bash
source /home/fastapiuser/anaconda3/etc/profile.d/conda.sh
conda activate netl-mwu-api-env && \
celery --app=primo_executor.primo_queue_manager.QUEUE_APP worker \
--concurrency=1 --loglevel=info --max-tasks-per-child 1
# PR 131 https://github.com/NEMRI-org/primo-ui-web-api/pull/131
# max tasks per child is set to 1 to prevent memory bloating from the copy-on-write OS and python reference count updates
# see https://docs.celeryq.dev/en/stable/userguide/optimizing.html#:~:text=Keep%20in%20mind,and%20worker_max_memory_per_child%20settings. 
