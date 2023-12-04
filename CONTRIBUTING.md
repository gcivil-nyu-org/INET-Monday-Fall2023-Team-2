# Contributing Guidelines

## First Steps

1. Create a Fork and name it Symbi

- Resource on GitHub Forking: https://gist.github.com/Chaser324/ce0505fbed06b947d962

2. Clone your Fork to your local machine

- `git clone https://github.com/USERNAME/Symbi.git`

3. Change into the directory where the repository was cloned

- `cd symbi`

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

8. Install any node dependencies from package.json using Node Package Manager (npm). Then, start the tailwind server for automatic page reloads during development. **Make sure you have latest Node.js (preferable >= `v20.9.0``) setup locally before executing these commands.** For more details, please refer to [Tailwind's Usage Docs](https://django-tailwind.readthedocs.io/en/latest/usage.html).

- `npm install`
- `python manage.py tailwind start`

9.  In a different terminal window, start the django project

- `python manage.py runserver`

## Keeping Your Fork Up-To-Date

1. Make sure your fork is up-to-date

- `git fetch upstream`

2. Checkout your own development branch

- `git checkout develop`

3. Merge upstream with the original repository’s development branch

- `git merge upstream/develop`

## Working in the Fork

1. Checkout your own development branch

- `git checkout develop`

2. Create a branch

- `git branch featurename`

3. Checkout the newly created branch to switch to it

- `git checkout featurename`
