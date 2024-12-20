##!/bin/bash

export BASE_URL='www.cellolighting.com'
export PORT=50100
export ORGANIZATION_NAME='Cello Lighting'

source ../venv/bin/activate

python scripts/setup
python u_copilot
