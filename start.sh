
#!/bin/bash

# Define the model directory
MODEL_DIR="models"

cd ..

# Check if the directory exists and is not empty
if [ ! -d "$MODEL_DIR" ] || [ -z "$(ls -A "$MODEL_DIR")" ]; then
    echo "Directory '$MODEL_DIR' does not exist or is empty. Downloading and extracting models..."
    
    # Download the file
    wget --no-check-certificate "https://docs.google.com/uc?export=download&id=1R8NGaXsKs-6YU8jd2Fe1mti2BXWhXFmK" -O models.tar.gz
    
    # Extract the file
    tar -xzvf models.tar.gz
    
    # Remove the tar.gz file after extraction (optional)
    rm models.tar.gz
    
    echo "Models downloaded and extracted successfully."
else
    echo "Directory '$MODEL_DIR' exists and is not empty. No action needed."
fi


python -m venv ../venv
source ../venv/bin/activate



export BASE_URL='www.cellolighting.com'
export PORT=50100
export SCHOOL_NAME='Cello Lighting'
mkdir local_data
./tools/init_web_d4.sh $BASE_URL $PORT
python ./tools/cleansing_data.py
python scripts/setup
python scripts/ingest_folder.py cleansed_website
python u_copilot
