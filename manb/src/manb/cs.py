import requests
import ipywidgets as widgets
import subprocess
from IPython.display import clear_output, display
from IPython.display import Image
from .env import Environment
from pprint import pprint
from io import _io
import plantuml
import pandas as pd

class ControlStructure:
  def __init__(this, env: Environment):
    this.env = env
    this.compByName = {}
    this.compById = {}
    this.compList = []

    this.funcByName = {}
    this.funcById = {}
    this.funcList = []

    # item: Control Action & Feedback types
    this.itemList = []
    this.itemByName = {}

    this.arcList = []
    this.arcByName = {}

    this.output = {}
    this.csImage = {}

    # control actions
    this.caDF = {}
    this.caDT = {}

    clear_output()
    print("Initializing Control Structure....")

    status, catId = this.env.getCategoryId("STPA: CS: Components")
    if status != 200:
      print("Failed to fetch control structure components category: " + str(status))
      return
    # fetch 'categorized' components
    r = requests.get(this.env.url + 'projects/' +
                this.env.projectDict[this.env.project.value] +
                '/entities/' + catId +
                '/relationshiptargets/' + this.env.relationDict['categorizes'] +
                '?sortBlockId=' + this.env.sortBlockDict['Numeric'],
                allow_redirects=False, headers=this.env.header)
    if r.status_code != 200:
      print("Failed to fetch categorized components: " + str(r.status_code))
      return
    # collect all components using Title
    components = r.json()['results']
    for component in components:
      compEntry = {}
      for attr in component['attributes']:
        if attr['definitionId'] == this.env.attributeDict['component:title']:
          if attr['value'] is not None:
            compEntry['id'] = component['id']
            this.compByName[attr['value']['value']] = compEntry
            this.compList.append(attr['value']['value'])
            this.compById[component['id']] = attr['value']['value']
        if attr['definitionId'] == this.env.attributeDict['component:type']:
          if attr['value'] is not None:
              compEntry['type'] = attr['value']['value']['value']
        if attr['definitionId'] == this.env.attributeDict['component:abbreviation']:
          if attr['value'] is not None:
              compEntry['abbreviation'] = attr['value']['value']

    this.compList.sort()
    for component in this.compList:
      # fetch 'built from' components
      r = requests.get(this.env.url + 'projects/' +
                  this.env.projectDict[this.env.project.value] +
                  '/entities/' + this.compByName[component]['id'] +
                  '/relationshiptargets/' + this.env.relationDict['built from'] +
                  '?sortBlockId=' + this.env.sortBlockDict['Numeric'],
                  allow_redirects=False, headers=this.env.header)
      if r.status_code != 200:
        print("Failed to fetch built from components: " + str(r.status_code))
        return
      bf_components = r.json()['results']
      bf_list = []
      for bf_component in bf_components:
        for attr in bf_component['attributes']:
          if attr['definitionId'] == this.env.attributeDict['component:title']:
            if attr['value'] is not None:
              # check if component is included in control structure
              if attr['value']['value'] in this.compByName.keys():
                bf_list.append(attr['value']['value'])
      this.compByName[component]['bf_list'] = []
      this.compByName[component]['bf_list'] = bf_list

    status, catId = this.env.getCategoryId("STPA: CS: Functions")
    if status != 200:
      print("Failed to fetch control structure functions category: " + str(status))
      return
    # fetch 'categorized' functions
    r = requests.get(this.env.url + 'projects/' +
                this.env.projectDict[this.env.project.value] +
                '/entities/' + catId +
                '/relationshiptargets/' + this.env.relationDict['categorizes'] +
                '?sortBlockId=' + this.env.sortBlockDict['Numeric'],
                allow_redirects=False, headers=this.env.header)
    if r.status_code != 200:
      print("Failed to fetch categorized functions: " + str(r.status_code))
      return
    # collect all functions using Title
    functions = r.json()['results']
    for function in functions:
      funcEntry = {}
      for attr in function['attributes']:
        if attr['definitionId'] == this.env.attributeDict['name']:
          if attr['value'] is not None:
            funcEntry['id'] = function['id']
            this.funcByName[attr['value']['value']] = funcEntry
            this.funcList.append(attr['value']['value'])
            this.funcById[function['id']] = attr['value']['value']

    this.funcList.sort()
    # fetch 'allocated to' component for function
    for function in this.funcList:
      r = requests.get(this.env.url + 'projects/' +
                  this.env.projectDict[this.env.project.value] +
                  '/entities/' + this.funcByName[function]['id'] +
                  '/relationshiptargets/' + this.env.relationDict['allocated to'] +
                  '?sortBlockId=' + this.env.sortBlockDict['Numeric'],
                  allow_redirects=False, headers=this.env.header)
      if r.status_code != 200:
        print("Failed to fetch allocated to components: " + str(r.status_code))
        return
      at_components = r.json()['results']
      for at_component in at_components:
        for attr in at_component['attributes']:
          if attr['definitionId'] == this.env.attributeDict['component:title']:
            if attr['value'] is not None:
              # check if component is included in control structure
              if attr['value']['value'] in this.compByName.keys():
                this.funcByName[function]['component'] = \
                    this.compByName[attr['value']['value']]['abbreviation']

    # fetch output control actions and feedback items
    for function in this.funcList:
      r = requests.get(this.env.url + 'projects/' +
                  this.env.projectDict[this.env.project.value] +
                  '/entities/' + this.funcByName[function]['id'] +
                  '/relationshiptargets/' + this.env.relationDict['outputs'] +
                  '?sortBlockId=' + this.env.sortBlockDict['Numeric'],
                  allow_redirects=False, headers=this.env.header)
      if r.status_code != 200:
        print("Failed to fetch output control actions / feedback items: " + str(r.status_code))
        return
      outputs = r.json()['results']
      for output in outputs:
        itemType = ""
        itemTitle = ""
        itemDescription = ""
        # check item type
        if output['entityDefinitionId'] == this.env.entityDict['ControlAction']:
          itemType = "ControlAction"
        else:
          itemType = "Feedback"

        for attr in output['attributes']:
          if attr['definitionId'] == this.env.attributeDict['item:title']:
            if attr['value'] is not None:
              itemTitle = attr['value']['value']
          if attr['definitionId'] == this.env.attributeDict['description']:
            if attr['value'] is not None:
              itemDescription = attr['value']['value']['plainText']

        # add to itemList
        this.itemList.append(itemTitle)
        itemEntry = {}
        itemEntry['type'] = itemType
        itemEntry['description'] = itemDescription
        itemEntry['inputComponent'] = ""
        itemEntry['outputComponent'] = this.funcByName[function]['component']
        this.itemByName[itemTitle] = itemEntry

    # fetch input control actions and feedback items
    for function in this.funcList:
      r = requests.get(this.env.url + 'projects/' +
                  this.env.projectDict[this.env.project.value] +
                  '/entities/' + this.funcByName[function]['id'] +
                  '/relationshiptargets/' + this.env.relationDict['inputs'] +
                  '?sortBlockId=' + this.env.sortBlockDict['Numeric'],
                  allow_redirects=False, headers=this.env.header)
      if r.status_code != 200:
        print("Failed to fetch input control actions / feedback items: " + str(r.status_code))
        return
      outputs = r.json()['results']
      for output in outputs:
        for attr in output['attributes']:
          if attr['definitionId'] == this.env.attributeDict['item:title']:
            if attr['value'] is not None:
              # update input component
              this.itemByName[attr['value']['value']]['inputComponent'] = \
                    this.funcByName[function]['component']

    this.itemList.sort()

    # combine items with same output/input pair into an arc
    for item in this.itemList:
      arcName = this.itemByName[item]['outputComponent'] + ':' + this.itemByName[item]['inputComponent']

      if arcName in this.arcByName.keys():
        this.arcByName[arcName]['arcLabels'].append(item)
      else:
        this.arcList.append(arcName)
        arcEntry = {}
        arcEntry['type'] = this.itemByName[item]['type']
        arcEntry['outputComponent'] = this.itemByName[item]['outputComponent']
        arcEntry['inputComponent'] = this.itemByName[item]['inputComponent']
        arcLabels = []
        arcLabels.append(item)
        arcEntry['arcLabels'] = arcLabels
        this.arcByName[arcName] = arcEntry

    clear_output()
    print("Control Structure Initialization Complete!")

  # create control structure plantuml diagram file
  def Diagram(this):
    lineColor = '#tan;line.bold;text:black'

    with open('cs.txt', 'w') as f:
      f.write('skinparam roundCorner 15\n')
      f.write('scale .75\n')
      f.write('@startuml\n')

      # every control structrue starts with 'Context' componenet
      for bf_component in this.compByName['Context']['bf_list']:
        this._output_built_from(f, 0, bf_component)

      for arc in this.arcList:
        arrowDir = ""
        labelDecorator = ""
        if this.arcByName[arc]['type'] == "ControlAction":
          arrowDir = ' -do-> '
          labelDecorator = '<&caret-bottom>'
        else:
          arrowDir = ' -up-> '
          labelDecorator = '<&caret-top>'

        # concatenate arc labels
        labelCount = 0
        labelString = ""
        for label in this.arcByName[arc]['arcLabels']:
          labelCount += 1
          labelString += labelDecorator + label
          if labelCount < len(this.arcByName[arc]['arcLabels']):
            labelString += '\\n'

        labelString += '\n'
        f.write(this.arcByName[arc]['outputComponent'] +
                arrowDir +
                this.arcByName[arc]['inputComponent'] +
                ' ' + lineColor + ' : ' + labelString)

      f.write('@enduml\n')

    server = plantuml.PlantUML('http://www.plantuml.com/plantuml/img/')
    try:
      ret = server.processes_file('./cs.txt', './cs.png', './cs_error.html')
    except BaseException as err:
      print(err)

    # setup output area
    this.output = widgets.Output(layout={'border': '1px solid black'})
    display(this.output)
    this.csImage = Image('./cs.png')
    # display cs diagram to output area
    with this.output:
      display(this.csImage)

  # recursively output built from
  def _output_built_from(this, f: _io.TextIOWrapper, level: int, component: str):
    compColor = '#deepskyblue'
    sysColor = '#white;line:grey;line.bold'

    if this.compByName[component]['type'] == 'Human':
      f.write(' '*level + 'person "' + component + '" as ' +
              this.compByName[component]['abbreviation'] +
              ' ' + compColor )
    elif this.compByName[component]['type'] == "System":
      f.write(' '*level + 'rectangle "' + component + '" as ' +
              this.compByName[component]['abbreviation'] +
              ' ' + sysColor )
    else:
      f.write(' '*level + 'rectangle "' + component + '" as ' +
              this.compByName[component]['abbreviation'] +
              ' ' + compColor )
    # check for built from components
    if len(this.compByName[component]['bf_list']) != 0:
      f.write(' {\n')
      level += 2
      for bf_component in this.compByName[component]['bf_list']:
        this._output_built_from(f, level, bf_component)
      level -= 2
      f.write(' '*level + '}\n')
    else:
      f.write('\n')

# display table of control actions
  def ControlActionTable(this):

    caTable = []
    for ca in this.itemList:
      caItem = []
      if this.itemByName[ca]['type'] == 'ControlAction':
        caItem.append(ca)
        caItem.append(this.itemByName[ca]['description'])
        caTable.append(caItem)

    this.caDF = pd.DataFrame(caTable, columns = ['Control Action', 'Description'])

    # setup output area
    this.output = widgets.Output(layout={'border': '1px solid black'})
    display(this.output)

    with this.output:
      try:
        from google.colab import data_table
        data_table.enable_dataframe_formatter()
        this.caDT = data_table.DataTable(this.caDF, include_index=False)
        # Display dataframa via Colab datatable
        display(this.caDT)
      except ModuleNotFoundError:
        # Display basic dataframe
        display(this.caDF)
