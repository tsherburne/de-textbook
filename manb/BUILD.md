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

jupyter lab --no-browser --ip="0.0.0.0"
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

## Ideas for [Jupyter Lite](https://jupyterlite.readthedocs.io/en/latest/)

*  Network Fetch - JSON DB Files
```
import json
from js import fetch
import pyodide_js, js
```
```
res = await fetch('https://raw.githubusercontent.com/tsherburne/de-textbook/main/projects/sf/entities.json')
text = await res.text()
obj = json.loads(text)
```
*  iTables Usage
```
await piplite.install('itables')
import itables
from itables import init_notebook_mode
init_notebook_mode(all_interactive=True)
```
```
from itables.sample_dfs import get_countries
df = get_countries()
df
```
*  [PlantUML Diagram Request](https://github.com/dougn/python-plantuml/blob/master/plantuml.py)
```
from zlib import compress
import base64
import string
import six
from six.moves.urllib.parse import urlencode
from IPython.display import Image

maketrans = bytes.maketrans
plantuml_alphabet = string.digits + string.ascii_uppercase + string.ascii_lowercase + '-_'
base64_alphabet   = string.ascii_uppercase + string.ascii_lowercase + string.digits + '+/'
b64_to_plantuml = maketrans(base64_alphabet.encode('utf-8'), plantuml_alphabet.encode('utf-8'))

diagram = "Bob->Alice : Hello!"
zlibbed_str = compress(diagram.encode('utf-8'))
compressed_string = zlibbed_str[2:-4]
diagramurl = base64.b64encode(compressed_string).translate(b64_to_plantuml).decode('utf-8')
fullurl = 'https://www.plantuml.com/plantuml/png/' + diagramurl
Image(url=fullurl)
```
*  Check Python Platform (Jupyter Light is ['emscripten'](https://emscripten.org/))
```
import sys
sys.platform
```