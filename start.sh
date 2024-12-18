export BASE_URL='www.cellolighting.com'
export PORT=50100
export SCHOOL_NAME='Cello Lighting'
mkdir local_data
cp -R ../50000_sample/private_gpt .
cp -R ../50000_sample/scripts .
cp ../50000_sample/settings* .
cp ../50000_sample/pyproject.toml .
cp ../50000_sample/Makefile .
../tools/init_web_d4.sh $BASE_URL $PORT
poetry install --with ui,local
poetry run python scripts/setup
PGPT_PROFILES=local make ingest cleansed_website
PGPT_PROFILES=local make run
