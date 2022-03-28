import sys
import json

# get url and store to path
def getJSON(url:str)->dict:

  text = ""

  # fetch the file
  if sys.platform == 'emscripten':
    import js
    import pyodide
    jsreq = js.XMLHttpRequest.new()
    jsreq.open("GET", url, False)
    try:
      jsreq.send()
    except pyodide.JsException as err:
      print("Get Error: " + str(err.js_error))
      return
    if jsreq.status != 200:
      print("Get Error: " + str(jsreq.status))
      return
    if jsreq.getResponseHeader("Content-Type") == 'text/plain; charset=utf-8':
      text = jsreq.responseText
    else:
      print("Unknown Content Type: " +
                    str(jsreq.getResponseHeader("Content-Type")))
      return
  else:
    import requests
    res = requests.get(url)
    if res.status_code != 200:
      print("Get Error: " + str(res.status_code))
      return
    if res.headers['content-type'] == 'text/plain; charset=utf-8':
      text = res.text
    else:
      print("Unknown Content Type: " + str(res.headers['content-type']))
      return

  return json.loads(text)
