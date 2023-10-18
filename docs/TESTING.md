# Testing

This repo runs the original Superset tests, which run on Jenkins on every PR. To run the tests locally, run:

## Backend

```bash
# install python and virtual env
pyenv install 3.9

# install virtualenv
pyenv virtualenv 3.9 superset
pyenv activate superset

pip install -r requirements/base.text
pip install -r requirements/testing.txt

# dependencies for weasyprint
brew install weasyprint

# copy missing files
# NOTE: please make sure to clean them up and not commit them
cp -R zf_integration/ superset/zf_integration/
cp zf_utils/jwt.py superset/utils/jwt.py

pytest ./tests/unit_tests/
```

To exit virtual environment run `source deactivate`

## Frontend

```bash
cd superset-frontend && npm ci
npm run test
```
