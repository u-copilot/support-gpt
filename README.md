install psql:

brew install postgresql
postgres --version

start:
brew services start postgresql

stop:
brew services stop postgresql


% pyenv global 3.11.8 <br>
% git clone <repo_project> <br> 
% cd <project> <br>
% python -m venv venv_gpt <br>
% source venv_gpt/bin/activate <br>
(venv_gpt)% pip install -r requirements.txt -e . <br>
(venv_gpt)% export BASE_URL='cellolighting.com' <br>
(venv_gpt)% export PORT=50100 <br>
(venv_gpt)% export SCHOOL_NAME='Cello Lighting' <br>
(venv_gpt)% poetry run python scripts/setup <br>
(venv_gpt)% poetry run python -m u-copilot  <br>


