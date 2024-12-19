#!/bin/bash

# Usage :  ./init_web.sh <domain_name> <port-number>
# example : ./init_web.sh paly.net 50001

# Check if a URL was provided as an argument
if [ -z "$1" ]; then
     echo "Usage: $0 <URL>"
     exit 1
fi

# Use the URL from the command line argument
wget --recursive --level=4 --no-clobber --page-requisites --html-extension --convert-links --restrict-file-names=windows --no-parent "https://$1"

# Extract the domain name for moving the downloaded directory
 domain=$1

rm -R website
rm -R cleansed_website
rm -R local_data/private_gpt

# Move the downloaded website to a specific directory
mv "$domain" website

# Run a Python script for data cleansing
#python tools/cleansing_data.py

#poetry install --with ui,local
#poetry run python scripts/setup
#PGPT_PROFILES=local make ingest cleansed_website
#PGPT_PROFILES=local make run
