#!/bin/bash

if [ $# -lt 1 ]; then 
    echo usage: FILE [region] [group] [instance] [owner]
    exit 1
fi

FILE=$(readlink -f $1)
REGION=${2:-eastus}
GROUP=${3:-onefuzz-bmc}
INSTANCE=${4:-onefuzz-bmc}
OWNER=${5:-bcaswell}

if [ ! -f ${FILE} ]; then 
    echo no such file: ${FILE}
    exit 1
fi

WORK_DIR=$(mktemp -d -p /tmp)
if [[ ! "$WORK_DIR" || ! -d "$WORK_DIR" ]]; then
    echo "Could not create temp dir"
    exit 1
fi

function cleanup {      
    echo "Deleted temp working directory $WORK_DIR"
    rm -r "$WORK_DIR"
}

trap "exit 1"           HUP INT PIPE QUIT TERM
trap cleanup EXIT

set -ex
cd ${WORK_DIR}
unzip ${FILE}
unzip onefuzz-deployment*.zip
python3 -m venv ${WORK_DIR}/venv
. ${WORK_DIR}/venv/bin/activate
pip install wheel
pip install -r requirements.txt
python deploy.py ${REGION} ${GROUP} ${INSTANCE} ${OWNER}
