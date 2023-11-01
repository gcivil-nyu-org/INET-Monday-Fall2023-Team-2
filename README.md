# Symbi
[![Build](https://app.travis-ci.com/gcivil-nyu-org/INET-Monday-Fall2023-Team-2.svg?branch=develop)](https://app.travis-ci.com/github/gcivil-nyu-org/INET-Monday-Fall2023-Team-2)
[![Coverage Status](https://coveralls.io/repos/github/gcivil-nyu-org/INET-Monday-Fall2023-Team-2/badge.svg?branch=develop)](https://coveralls.io/github/gcivil-nyu-org/INET-Monday-Fall2023-Team-2?branch=develop)

## Want to work on the project? Follow these steps!

### First Steps

1. Create a Fork and name it Symbi

- Resource on GitHub Forking: https://gist.github.com/Chaser324/ce0505fbed06b947d962

2. Clone your Fork to your local machine

- `git clone https://github.com/USERNAME/Symbi.git`

3. Change into the directory where the repository was cloned

- `cd Symbi`

4. Keep up-to-date with the original upstream repository that you forked (this repository)

- Add 'upstream' repo to list of remotes
- `git remote add upstream https://github.com/UPSTREAM-USER/ORIGINAL-PROJECT.git`
- Verify the new remote named 'upstream'
- `git remote -v`

5. In the Symbi directory, create a virtual environment and activate it

- `virtualenv .env`
- on Mac: `source .env/bin/activate`
- on Windows: `.env/Scripts/activate`

6. Change into the directory containing the django project

- `cd symbi`

7. Install requirements in the virtual environment

- `pip install -r requirements.txt`

8. Create a file called ‘.env’

- `touch .env`

9. Generate a secret key and print the output by running this command in terminal:

- `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`

10. Inside the .env file, create a variable called SECRET_KEY and paste the key that was generated. GitHub knows to ignore files named .env, so your secret key will remain local.

### Keeping Your Fork Up-To-Date

1. Make sure your fork is up-to-date

- `git fetch upstream`

2. Checkout your own development branch

- `git checkout develop`

3. Merge upstream with the original repository’s development branch

- `git merge upstream/develop`

### Working in the Fork

1. Checkout your own development branch

- `git checkout develop`

2. Create a branch

- `git branch featurename`

3. Checkout the newly created branch to switch to it

- `git checkout featurename`
