
wget --no-check-certificate "https://drive.google.com/file/d/1R8NGaXsKs-6YU8jd2Fe1mti2BXWhXFmK/view?usp=sharing" -D .

#install psql:

brew install postgresql
postgres --version

#start postgresql:
brew services start postgresql

#stop postgresql:
brew services stop postgresql


pyenv global 3.11.8 <br>
git clone <repo_project> <br> 
cd <project> <br>
python -m venv venv_gpt <br>
source venv_gpt/bin/activate <br>
pip install -r requirements.txt -e . <br>
export BASE_URL='cellolighting.com' <br>
export PORT=50100 <br>
export SCHOOL_NAME='Cello Lighting' <br>
poetry run python scripts/setup <br>
poetry run python -m u-copilot  <br>


