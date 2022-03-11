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

## Local Dev Environment Setup
```
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade jupyterlab
```
```
export PYTHONPATH=/home/ubuntu/pypi/de-textbook/manb/src
```

## Local Usage via VS Code

### NoteBook Module Reload Cell Magic
```
%load_ext autoreload
%autoreload 2
```
### Local PlantUML Server
* https://github.com/plantuml/plantuml/releases
* https://plantuml.com/picoweb
```
 java -jar plantuml-1.2022.2.jar -picoweb:8000:127.0.0.1
```

### Using Notebook Logger
```
# create a cell for log output
import logging
env.logger.setLevel(logging.INFO)
env.loghandler.clear_logs()
env.loghandler.show_logs()
```

```
# using the logger
env.logger.warning('a warning message')
env.logger.warning('json message: ' + json.dumps(<dict>), indent=2)
```