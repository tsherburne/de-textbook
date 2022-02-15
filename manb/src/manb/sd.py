import ipywidgets as widgets
from IPython.display import clear_output, display
from IPython.display import Image
from .env import Environment
from .pr import Project
from pprint import pprint
from io import _io
import plantuml
import pandas as pd

class SystemDescription:
  def __init__(this, env: Environment):
    this.env = env

    this.compTypes = ['Category', 'Component', 'ControlAction', 'DomainSet',
                      'Exit', 'Feedback', 'Function', 'Link', 'UseCase']

    this.pr = Project(env)
    this.pr.FetchSchema()
    this.pr.FetchEntities(this.compTypes)
    this.pr.FetchStructure()

    # last function processed - when parsing call structure
    this.lastFunction = ""

    this.output = {}

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

    # use cases
    this.ucDF = {}
    this.ucDT = {}
    clear_output()
    print("System Description Initialization Complete!")
    return

  # create control structure plantuml diagram file
  def ControlStructureDiagram(this):
    db = this.pr.entities
    dbDict = this.pr.entitiesDict

    lineColor = '#tan;line.bold;text:black'

    with open('./diagrams/cs.txt', 'w') as f:
      f.write('skinparam roundCorner 15\n')
      f.write('scale .75\n')
      f.write('@startuml\n')

      contextId = dbDict['System Context']

      # every control structure starts with 'System Context' component
      for bf_component in db[contextId]['rels']['built from']:
        this._output_built_from(f, 0, bf_component)

      this._create_control_structure_arcs()
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
      ret = server.processes_file('./diagrams/cs.txt',
                            './diagrams/cs.png', './diagrams/cs_error.html')
    except BaseException as err:
      print(err)

    # setup output area
    this.output = widgets.Output(layout={'border': '1px solid black'})
    display(this.output)
    this.csImage = Image('./diagrams/cs.png')
    # display cs diagram to output area
    with this.output:
      display(this.csImage)
    return

# recursively output built from
  def _output_built_from(this, f: _io.TextIOWrapper, level: int, component: dict):
    db = this.pr.entities
    dbDict = this.pr.entitiesDict
    csCompCatId = dbDict['SD: CS: Components']
    compColor = '#deepskyblue'
    sysColor = '#white;line:grey;line.bold'

    # check if component is to be included in control structure (by category)
    found = False
    for comp in db[csCompCatId]['rels']['categorizes']:
      if comp['targetId'] == component['targetId']:
        found = True
        break
    if found != True:
      return
    compType = db[component['targetId']]['attrs']['type']['value']
    compName = db[component['targetId']]['attrs']['title']['value']
    compAbbr = db[component['targetId']]['attrs']['abbreviation']['value']

    if compType == 'Human':
      f.write(' '*level + 'person "' + compName + '" as ' +
              compAbbr + ' ' + compColor )
    elif compType == "System":
      f.write(' '*level + 'rectangle "' + compName + '" as ' +
              compAbbr + ' ' + sysColor )
    else:
      f.write(' '*level + 'rectangle "' + compName + '" as ' +
              compAbbr + ' ' + compColor )

    # check for built from components
    if 'built from' in db[component['targetId']]['rels']:
      # check that at least one built from component is
      # included in control structure
      for bf_comp in db[component['targetId']]['rels']['built from']:
        found = False
        for comp in db[csCompCatId]['rels']['categorizes']:
          if comp['targetId'] == bf_comp['targetId']:
            found = True
            break
        if found == True:
          break
      # at least on 'built from' component in control structure
      if found == True:
        f.write(' {\n')
        level += 2
        for bf_component in db[component['targetId']]['rels']['built from']:
          this._output_built_from(f, level, bf_component)
        level -= 2
        f.write(' '*level + '}\n')
      else:
        f.write('\n')
    else:
      f.write('\n')
    return

  def _create_control_structure_arcs(this):
    this.arcByName = {}
    this.arcList = []
    this.itemByName = {}
    this.itemList = []
    db = this.pr.entities
    dbDict = this.pr.entitiesDict
    csFuncCatId = dbDict['SD: CS: Functions']

    # fetch output control actions and feedback items
    for function in db[csFuncCatId]['rels']['categorizes']:
      if 'outputs' in db[function['targetId']]['rels']:
        for output in db[function['targetId']]['rels']['outputs']:
          itemEntry = {}
          itemEntry['ItemTitle'] = db[output['targetId']]['attrs']['title']['value']
          itemEntry['itemDescription'] = db[output['targetId']]['attrs']\
                    ['description']['value']
          itemEntry['itemType'] = db[output['targetId']]['type']
          itemEntry['inputComponent'] = ""
          outCompId = db[function['targetId']]['rels']['allocated to'][0]
          itemEntry['outputComponent'] = db[outCompId['targetId']]['attrs']\
                    ['abbreviation']['value']

          # add to list and dict
          this.itemList.append(itemEntry['ItemTitle'])
          this.itemByName[itemEntry['ItemTitle']] = itemEntry

    # fetch input control actions and feedback items
    for function in db[csFuncCatId]['rels']['categorizes']:
      if 'inputs' in db[function['targetId']]['rels']:
        for input in db[function['targetId']]['rels']['inputs']:
          inCompId = db[function['targetId']]['rels']['allocated to'][0]
          itemTitle = db[input['targetId']]['attrs']['title']['value']
          # update input component
          this.itemByName[itemTitle]['inputComponent'] = \
                  db[inCompId['targetId']]['attrs']['abbreviation']['value']

    this.itemList.sort()

    # combine items with same output/input pair into an arc
    for item in this.itemList:
      arcName = this.itemByName[item]['outputComponent'] + ':' + \
                  this.itemByName[item]['inputComponent']

      if arcName in this.arcByName.keys():
        this.arcByName[arcName]['arcLabels'].append(item)
      else:
        this.arcList.append(arcName)
        arcEntry = {}
        arcEntry['type'] = this.itemByName[item]['itemType']
        arcEntry['outputComponent'] = this.itemByName[item]['outputComponent']
        arcEntry['inputComponent'] = this.itemByName[item]['inputComponent']
        arcLabels = []
        arcLabels.append(item)
        arcEntry['arcLabels'] = arcLabels
        this.arcByName[arcName] = arcEntry

    return

  # display use case diagram
  def UseCaseDiagrams(this):
    db = this.pr.entities
    dbDict = this.pr.entitiesDict

    # get category ID for System Description: Use Cases
    ucCatId = dbDict['SD: UC']

    # retrieve categorized Use Cases
    for uc in db[ucCatId]['rels']['categorizes']:
      ucName = db[uc['targetId']]['attrs']['name']['value']
      inputPath = "./diagrams/" + ucName.replace(" ", "") + ".txt"
      outputPath = "./diagrams/" + ucName.replace(" ", "") + ".png"
      errorPath = "./diagrams/" + ucName.replace(" ", "") + "_error.html"

      with open(inputPath, 'w') as f:
        f.write('@startuml\n')
        f.write('left to right direction\n')

        # retrieve 'involves' Components (actors)
        for comp in db[uc['targetId']]['rels']['involves']:
          f.write('actor "' + db[comp['targetId']]['attrs']['title']['value'] + '" as ' +
                   db[comp['targetId']]['attrs']['abbreviation']['value'] + '\n')

        # retrieve 'describes' Component (single association [0])
        desId = db[uc['targetId']]['rels']['describes'][0]['targetId']
        f.write('package ' + db[desId]['attrs']['title']['value'] + ' {\n')

        # retrieve 'includes' UseCases
        for iuc in db[uc['targetId']]['rels']['includes']:
          f.write('  usecase "' + db[iuc['targetId']]['attrs']['name']['value'] + '" as ' +
                  db[iuc['targetId']]['attrs']['number']['value'] + '\n')

        f.write('}\n')

        # retrieve 'involves' components per use case (connections)
        for iuc in db[uc['targetId']]['rels']['includes']:
          for invuc in db[iuc['targetId']]['rels']['involves']:

            # create connection between actors and usecase with display 'hint' u/d/l/r
            f.write(db[invuc['targetId']]['attrs']['abbreviation']['value'] + ' -' +
                    invuc['attrs']['hint']['value'] + '-> ' +
                    db[iuc['targetId']]['attrs']['number']['value'] + '\n')

        f.write('@enduml\n')

      # create UML diagram
      server = plantuml.PlantUML('http://www.plantuml.com/plantuml/img/')
      try:
        ret = server.processes_file(inputPath, outputPath, errorPath)
      except BaseException as err:
        print(err)

      # setup output area
      this.output = widgets.Output(layout={'border': '1px solid black'})
      display(this.output)
      # display uc diagram to output area
      with this.output:
        display(Image(outputPath))

  # display use case table
  def UseCaseTable(this):
    db = this.pr.entities
    dbDict = this.pr.entitiesDict
    # get category ID for System Description: Use Cases
    ucCatId = dbDict['SD: UC']

    ucTable = []
    # retrieve categorized Use Cases
    for uc in db[ucCatId]['rels']['categorizes']:
      for uci in db[uc['targetId']]['rels']['includes']:
        ucItem = []
        ucItem.append(db[uci['targetId']]['attrs']['name']['value'])
        ucItem.append(db[uci['targetId']]['attrs']['description']['value'])
        ucItem.append(db[uci['targetId']]['attrs']['preconditions']['value'])
        ucItem.append(db[uci['targetId']]['attrs']['postconditions']['value'])
        ucTable.append(ucItem)

    this.ucDF = pd.DataFrame(ucTable, columns = ['Name', 'Description',
                  'Pre-Conditions', 'Post-Conditions'])

    # setup output area
    this.output = widgets.Output(layout={'border': '1px solid black'})
    display(this.output)

    with this.output:
      try:
        from google.colab import data_table
        data_table.enable_dataframe_formatter()
        this.ucDT = data_table.DataTable(this.ucDF, include_index=False)
        # Display dataframa via Colab datatable
        display(this.ucDT)
      except ModuleNotFoundError:
        # Display basic dataframe
        display(this.ucDF)
    return

  # display use case message sequence diagrams
  def MSCDiagrams(this):
    db = this.pr.entities
    dbDict = this.pr.entitiesDict
    structures = this.pr.structures

    # get category ID for System Description: Use Cases
    ucCatId = dbDict['SD: UC']

    # retrieve categorized Use Cases
    for uc in db[ucCatId]['rels']['categorizes']:
      # retrieve 'includes' UseCases
      for iuc in db[uc['targetId']]['rels']['includes']:
        # each usecase is 'categorized by' a single category that
        # includes an 'ordered' list of participants (swimlanes)
        catById = db[iuc['targetId']]['rels']['categorized by'][0]

        # need to sort the parts by 'order' relationship attribute
        partDict = {}
        for part in db[catById['targetId']]['rels']['categorizes']:
          if db[part['targetId']]['type'] == 'Component':
            partDict[part['attrs']['order']['value']] = part['targetId']

        sortedPartList = sorted(partDict)
        ucName = db[iuc['targetId']]['attrs']['name']['value']
        inputPath = "./diagrams/" + ucName.replace(" ", "") + ".txt"
        outputPath = "./diagrams/" + ucName.replace(" ", "") + ".png"
        errorPath = "./diagrams/" + ucName.replace(" ", "") + "_error.html"

        with open(inputPath, 'w') as f:
          f.write('@startuml\n')
          f.write('title MSC: ' + ucName + '\n')

          # output participants (swimlanes)
          for part in sortedPartList:
            if db[partDict[part]]['attrs']['type']['value'] == 'Human':
              f.write('actor "' + db[partDict[part]]['attrs']['title']['value'] +
                      '" as ' + db[partDict[part]]['attrs']['abbreviation']['value'] + '\n')
            else:
              f.write('control "' + db[partDict[part]]['attrs']['title']['value'] +
                      '" as ' + db[partDict[part]]['attrs']['abbreviation']['value'] + '\n')
          # parse call structure for included use case 'elaborated by' function
          constructs = structures[db[iuc['targetId']]['rels']['elaborated by'][0]\
                        ['targetId']]['mainBranch']['constructs']
          this._process_constructs(f, 0, constructs)
          f.write('@enduml\n')

        # create UML diagram
        server = plantuml.PlantUML('http://www.plantuml.com/plantuml/img/')
        try:
          ret = server.processes_file(inputPath, outputPath, errorPath)
        except BaseException as err:
          print(err)

        # setup output area
        this.output = widgets.Output(layout={'border': '1px solid black'})
        display(this.output)
        # display uc diagram to output area
        with this.output:
          display(Image(outputPath))
      return

  def _process_constructs(this, f: _io.TextIOWrapper, level: int, constructs: dict):
    db = this.pr.entities

    for construct in constructs:
      if construct['constructType'] == 'function':
        this.lastFunction = construct['functionId']
        this._process_function(f, level, construct['functionId'])
        # process function exits
        exitCount = 0
        for branch in construct['branches']:
          exitCount += 1
          exitName = db[branch['exitId']]['attrs']['name']['value']
          if exitCount == 1:
            f.write(' '*level + 'alt ' + exitName + '\n')
          else:
            f.write(' '*level + 'else ' + exitName + '\n')
          level += 2
          this._process_constructs(f, level, branch['constructs'])
          level -= 2
        if exitCount > 0:
          f.write(' '*level + 'end\n')
      elif construct['constructType'] == 'parallel':
        f.write(' '*level + 'par\n')
        for branch in construct['branches']:
          level += 2
          this._process_constructs(f, level, branch['constructs'])
          level -= 2
        f.write(' '*level + 'end par\n')
      elif construct['constructType'] == 'loop':
        if construct['annotation'] is not None:
          f.write(' '*level + 'loop ' + construct['annotation'] + '\n')
        else:
          f.write(' '*level + 'loop\n')

        level += 2
        this._process_constructs(f, level, construct['branch']['constructs'])
        level -= 2
        f.write(' '*level + 'end loop\n')
      elif construct['constructType'] == 'replicate':
        # retrieve domain set name
        dsName = db[construct['domainSetId']]['attrs']['name']['value']
        f.write(' '*level + 'group repl[' + dsName + ']\n')

        level += 2
        this._process_constructs(f, level, construct['branch']['constructs'])
        level -= 2
        f.write(' '*level + 'end\n')
      elif construct['constructType'] == 'loopExit':
        comp = db[this.lastFunction]['rels']['allocated to'][0]['targetId']
        compAbbrv = db[comp]['attrs']['abbreviation']['value']
        f.write(' '*level + compAbbrv + ' --> ' + compAbbrv + ' : [Loop Exit]\n')
      else:
        print("Unknown Construct Type!")
    return

  def _process_function(this, f: _io.TextIOWrapper, level: int, functionId: str):
    db = this.pr.entities

    # process 'outputs' items (control action / feedback)
    if 'outputs' in db[functionId]['rels']:
      for output in db[functionId]['rels']['outputs']:
        itemType = db[output['targetId']]['type']
        itemName = db[output['targetId']]['attrs']['name']['value']
        # retrieve 'input to' endpoint
        inFunc = db[output['targetId']]['rels']['input to'][0]['targetId']
        # retrieve function 'allocated to' component abbreviation
        outComp = db[functionId]['rels']['allocated to'][0]['targetId']
        outAbbrv = db[outComp]['attrs']['abbreviation']['value']
        inComp = db[inFunc]['rels']['allocated to'][0]['targetId']
        inAbbrv = db[inComp]['attrs']['abbreviation']['value']

        if itemType == 'ControlAction':
          f.write(' '*level + outAbbrv + ' -> ' + inAbbrv +
                  ' : <&caret-bottom>' + itemName + '\n')
        else:
          f.write(' '*level + outAbbrv + ' -> ' + inAbbrv +
                  ' : <&caret-top>' + itemName + '\n')
    return

  # display table of control actions
  def ControlActionTable(this):

    caTable = []
    for ca in this.itemList:
      caItem = []
      if this.itemByName[ca]['itemType'] == 'ControlAction':
        caItem.append(ca)
        caItem.append(this.itemByName[ca]['itemDescription'])
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
    return
