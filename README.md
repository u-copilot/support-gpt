% pyenv global 3.11.8
% git clone <repo_project> 
% cd <project>
% python -m venv venv_gpt
% source venv_gpt/bin/activate
(venv_gpt)% pip install -r requirements.txt -e .
(venv_gpt)% export BASE_URL='cellolighting.com'
(venv_gpt)% export PORT=50100
(venv_gpt)% export SCHOOL_NAME='Cello Lighting'
(venv_gpt)% poetry run python scripts/setup
(venv_gpt)% poetry run python -m u-copilot 


