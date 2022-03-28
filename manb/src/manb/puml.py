from zlib import compress
import base64
import string
from IPython.display import Image, display

# display PlantUML diagram from input PlantUML text file
def displayPlantUML(url:str, inPath:str):

  try:
    with open(inPath, 'r') as f:
      diagram = f.read()
  except FileNotFoundError:
    print("Error: Input file not found")
    return

  maketrans = bytes.maketrans
  plantuml_alphabet = \
    string.digits + string.ascii_uppercase + string.ascii_lowercase + '-_'
  base64_alphabet = \
    string.ascii_uppercase + string.ascii_lowercase + string.digits + '+/'
  b64_to_plantuml = \
    maketrans(base64_alphabet.encode('utf-8'),
                  plantuml_alphabet.encode('utf-8'))

  zlibbed_str = compress(diagram.encode('utf-8'))
  compressed_string = zlibbed_str[2:-4]
  diagramurl = \
    base64.b64encode(compressed_string).translate(b64_to_plantuml).\
      decode('utf-8')

  fetchurl = url + diagramurl
  display(Image(url=fetchurl))

  return