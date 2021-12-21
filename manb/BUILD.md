# Build and Manage 'manb' Package

[Python Packaging Tutorial](https://packaging.python.org/en/latest/tutorials/packaging-projects/)

```
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade build
python3 -m pip install --upgrade twine

python3 -m build
python3 -m twine upload --repository testpypi dist/*

```