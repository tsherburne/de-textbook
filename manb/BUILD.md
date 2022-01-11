# Build and Manage 'manb' Package

## [Python Packaging Tutorial](https://packaging.python.org/en/latest/tutorials/packaging-projects/)

```
sudo apt-get install python3.8-venv

python3 -m pip install --upgrade pip
python3 -m pip install --upgrade build
python3 -m pip install --upgrade twine

python3 -m build
python3 -m twine upload --repository pypi dist/*

```

## Local Dev Environment
```
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade jupyterlab
```
```
export PYTHONPATH=/home/ubuntu/pypi/de-textbook/manb/src
```

### NoteBook Module Reload Cell Magic
```
%load_ext autoreload
%autoreload 2
```