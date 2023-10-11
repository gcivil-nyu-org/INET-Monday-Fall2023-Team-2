To work on the project

1. Clone the repo
- `git clone https://github.com/gcivil-nyu-org/INET-Monday-Fall2023-Team-2.git`
- `cd INET-Monday-Fall2023-Team-2`

2. Create virtual environment
- `virtualenv .env`
- `.env/Scripts/activate`

3. Install dependencies
- `pip install -r requirements.txt` 

4. For the first time you clone the repo
- Create file ".env" inside of ./symbi
- Run this command in your terminal 
  - `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
  - Copy the output to clipboard 
- Inside .env, create variable called `SECRET_KEY` and paste the key that was generated