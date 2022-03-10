import ipywidgets as widgets
from IPython.display import display
from IPython.display import Image
from .env import Environment
from .pr import Project
from pprint import pprint
from io import _io
import plantuml

lastFunction = ""
partList = []

# each MSC is 'categorized by' a single category (catId) that
# includes an 'ordered' list of participants (swimlanes)
def drawMSC(catId:str, env: Environment, pr: Project) -> None:
  global lastFunction, partList
  lastFunction = ""
  partList = []

  db = pr.entities
  dbDict = pr.entitiesDict
  structures = pr.structures

  # need to sort the parts by 'order' relationship attribute
  partDict = {}
  partList = []
  for part in db[catId]['rels']['categorizes']:
    if db[part['targetId']]['type'] == 'Component':
      partDict[part['attrs']['order']['value']] = part['targetId']
      partList.append(part['targetId'])
    elif db[part['targetId']]['type'] == 'Item':
      # Items are displayed as Entity (datatstore) in swimlane
      partDict[part['attrs']['order']['value']] = part['targetId']
      partList.append(part['targetId'])
      pass
    elif db[part['targetId']]['type'] == 'Function':
      # a single function is 'categorized' to be decomposed for the MSC
      fnName = db[part['targetId']]['attrs']['name']['value']
      fnId = part['targetId']

  sortedPartList = sorted(partDict)
  inputPath = "./diagrams/uc_" + fnName.replace(" ", "") + ".txt"
  outputPath = "./diagrams/uc_" + fnName.replace(" ", "") + ".png"
  errorPath = "./diagrams/uc_" + fnName.replace(" ", "") + "_error.html"

  with open(inputPath, 'w') as f:
    f.write('@startuml\n')
    f.write('skinparam backgroundColor silver\n')
    f.write('skinparam sequenceArrowThickness 2\n')
    f.write('skinparam sequenceArrowColor ' + env.MAColor + '\n')

    f.write('title MSC: ' + fnName + '\n')

    # output participants (swimlanes)
    for part in sortedPartList:
      if db[partDict[part]]['type'] == 'Item':
        f.write('entity "' + db[partDict[part]]['attrs']['name']['value'] +
                '" as ' +
                db[partDict[part]]['attrs']['number']['value'] + '\n')
      else:
        builtFromId = db[partDict[part]]['rels']['built in'][0]['targetId']
        if db[builtFromId]['attrs']['type']['value'] == 'Sentinel':
          f.write('control "' + db[partDict[part]]['attrs']['title']['value'] +
                '" as ' +
                db[partDict[part]]['attrs']['abbreviation']['value'] +
                ' ' + env.MAColor + '\n')
        else:
          if db[partDict[part]]['attrs']['type']['value'] == 'Human':
            f.write('actor "' + db[partDict[part]]['attrs']['title']['value'] +
                  '" as ' +
                  db[partDict[part]]['attrs']['abbreviation']['value'] +
                  ' ' + env.PhyColor + '\n')
          else:
            f.write('control "' + db[partDict[part]]['attrs']['title']['value'] +
                  '" as ' +
                  db[partDict[part]]['attrs']['abbreviation']['value'] +
                  ' ' + env.PhyColor + '\n')

    # check if alt flow and put reference to primary flow
    for elaborate in db[fnId]['rels']['elaborates']:
      if db[elaborate['targetId']]['type'] == 'UseCase':
        if elaborate['attrs']['flowType']['value'] == 'Alternate':
          # output reference on right side participant (swimlane)
          rightPart = db[partDict[sortedPartList[-1]]]['attrs']\
                                    ['abbreviation']['value']
          f.write('ref over ' + rightPart + ' : ' +
                db[elaborate['targetId']]['attrs']['number']['value'] + ':' +
                db[elaborate['targetId']]['attrs']['name']['value'] + '\n')

    # parse call structure for function
    constructs = structures[fnId]['mainBranch']['constructs']
    _process_constructs(env, db, f, 0, constructs)
    f.write('@enduml\n')

  # create UML diagram
  server = plantuml.PlantUML(env.plantuml)
  try:
    ret = server.processes_file(inputPath, outputPath, errorPath)
  except BaseException as err:
    print(err)

  # setup output area
  output = widgets.Output(layout={'border': '1px solid black'})
  display(output)
  # display uc diagram to output area
  with output:
    display(Image(outputPath))
  return

def _process_constructs(env: Environment, db: dict, f: _io.TextIOWrapper,
                          level: int, constructs: dict):
  global lastFunction

  for construct in constructs:
    if construct['constructType'] == 'function':
      lastFunction = construct['functionId']
      _process_function(env, db, f, level, construct['functionId'])
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
        _process_constructs(env, db, f, level, branch['constructs'])
        level -= 2
      if exitCount > 0:
        f.write(' '*level + 'end\n')
    elif construct['constructType'] == 'parallel':
      f.write(' '*level + 'par\n')
      for branch in construct['branches']:
        level += 2
        _process_constructs(env, db, f, level, branch['constructs'])
        level -= 2
      f.write(' '*level + 'end par\n')
    elif construct['constructType'] == 'loop':
      if construct['annotation'] is not None:
        f.write(' '*level + 'loop ' + construct['annotation'] + '\n')
      else:
        f.write(' '*level + 'loop\n')

      level += 2
      _process_constructs(env, db, f, level, construct['branch']['constructs'])
      level -= 2
      f.write(' '*level + 'end loop\n')
    elif construct['constructType'] == 'replicate':
      # retrieve domain set name
      dsName = db[construct['domainSetId']]['attrs']['name']['value']
      f.write(' '*level + 'group repl[' + dsName + ']\n')

      level += 2
      _process_constructs(env, db, f, level, construct['branch']['constructs'])
      level -= 2
      f.write(' '*level + 'end\n')
    elif construct['constructType'] == 'loopExit':
      comp = db[lastFunction]['rels']['allocated to'][0]['targetId']
      compAbbrv = db[comp]['attrs']['abbreviation']['value']
      f.write(' '*level + compAbbrv + ' --> ' + compAbbrv + ' : [Loop Exit]\n')
    else:
      print("Unknown Construct Type!")
  return

def _process_function(env: Environment, db: dict, f: _io.TextIOWrapper,
                      level: int, functionId: str):

  global partList

  # process 'inputs' items (control action / feedback) from external
  if 'inputs' in db[functionId]['rels']:
    for input in db[functionId]['rels']['inputs']:
      itemType = db[input['targetId']]['type']
      itemName = db[input['targetId']]['attrs']['name']['value']
      itemNum = db[input['targetId']]['attrs']['number']['value']

      # retrieve 'output to' endpoints
      for outFuncTarget in db[input['targetId']]['rels']['output from']:
        outFunc = outFuncTarget['targetId']

        # retrieve function 'allocated to' component abbreviation
        inComp = db[functionId]['rels']['allocated to'][0]['targetId']
        inAbbrv = db[inComp]['attrs']['abbreviation']['value']
        outComp = db[outFunc]['rels']['allocated to'][0]['targetId']
        outAbbrv = db[outComp]['attrs']['abbreviation']['value']
        if outComp not in partList:
          # output Component not part of current MSC
          # show as off page connector
          if itemType == 'ControlAction':
            f.write(' '*level + inAbbrv + ' <-] ' +
                    ' : <&caret-bottom>' + itemName + '\n')
          else:
            f.write(' '*level + inAbbrv + ' <-] ' +
                    ' : <&caret-top>' + itemName + '\n')
        else:
          if itemType == 'Item':
            #show flow out of datastore
            f.write(' '*level + itemNum + ' -> ' + inAbbrv +
                  ' : <&file>' + 'Read' + '\n')


  # process 'outputs' items (control action / feedback)
  if 'outputs' in db[functionId]['rels']:
    for output in db[functionId]['rels']['outputs']:
      itemType = db[output['targetId']]['type']
      itemName = db[output['targetId']]['attrs']['name']['value']
      itemNum = db[output['targetId']]['attrs']['number']['value']

      # retrieve 'input to' endpoints
      for inFuncTarget in db[output['targetId']]['rels']['input to']:
        inFunc = inFuncTarget['targetId']

        # retrieve function 'allocated to' component abbreviation
        outComp = db[functionId]['rels']['allocated to'][0]['targetId']
        outAbbrv = db[outComp]['attrs']['abbreviation']['value']
        inComp = db[inFunc]['rels']['allocated to'][0]['targetId']
        inAbbrv = db[inComp]['attrs']['abbreviation']['value']

        if inComp not in partList:
          # input Component not part of current MSC
          continue

        if itemType == 'ControlAction':
          f.write(' '*level + outAbbrv + ' -> ' + inAbbrv +
                  ' : <&caret-bottom>' + itemName + '\n')
        elif itemType == 'Feedback':
          f.write(' '*level + outAbbrv + ' -> ' + inAbbrv +
                  ' : <&caret-top>' + itemName + '\n')
        elif itemType == 'Item':
          # show flow into datastore
          f.write(' '*level + outAbbrv + ' -> ' + itemNum +
                  ' : <&file>' + 'Write' + '\n')
  return
