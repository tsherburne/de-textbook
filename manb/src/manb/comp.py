import ipywidgets as widgets
from IPython.display import display
from IPython.display import Image
from .env import Environment
from .pr import Project
from pprint import pprint
from io import _io
from .puml import displayPlantUML

def drawComp(catId:str, env: Environment, pr: Project) -> None:
  db = pr.entities
  dbDict = pr.entitiesDict
  compList = []
  linkDict = {}
  pbName = ""
  pbTitle = ""

  # retrieve physical block diagram components
  for entity in db[catId]['rels']['categorizes']:
    entityName = db[entity['targetId']]['attrs']['name']['value']
    if db[entity['targetId']]['type'] == 'Component':
      if entity['attrs']['hint']['value'] == 'context':
        pbTitle = db[entity['targetId']]['attrs']['title']['value']
        pbName = db[entity['targetId']]['attrs']['name']['value']
      else:
        compList.append(entityName)
    elif db[entity['targetId']]['type'] == 'Link':
      linkDict[entityName]= entity['attrs']['hint']['value']
    else:
      print("Invalid categorized type: " + db[entity['targetId']]['type'])

  inputPath = "./diagrams/pb_" + pbTitle.replace(" ", "") + ".txt"
  outputPath = "./diagrams/pb_" + pbTitle.replace(" ", "") + ".png"
  errorPath = "./diagrams/pb_" + pbTitle.replace(" ", "") + "_error.html"

  if pbName == "":
    print("No 'context' set for: " + db[catId]['attrs']['name']['value'])
    return

  with open(inputPath, 'w') as f:

    f.write('@startuml\n')
    f.write('title Physical Block Diagram: ' + pbTitle + '\n')
    f.write('skinparam componentStyle rectangle\n')
    f.write('skinparam BackgroundColor silver\n')
    f.write('skinparam roundCorner 15\n')
    f.write('frame "' + pbTitle + '" {\n')

    # retrive 'built from' components
    for bfcomp in db[dbDict[pbName]]['rels']['built from']:
      bfcompName = db[bfcomp['targetId']]['attrs']['name']['value']
      bfcompAbbr = db[bfcomp['targetId']]['attrs']['abbreviation']['value']
      bfcompType = db[bfcomp['targetId']]['attrs']['type']['value']
      bfcompTitle = db[bfcomp['targetId']]['attrs']['title']['value']

      # only include built from compnents included in category
      if bfcompName in compList:
        f.write('  [' + bfcompAbbr + ': ' + bfcompTitle + '] as ' + bfcompAbbr +
            ' <<' + bfcompType + '>> ' + env.PhyColor + '\n')
        compList.remove(bfcompName)
    f.write('}\n')

    # add remaining external components
    for comp in compList:
      bfcompName = db[dbDict[comp]]['attrs']['name']['value']
      bfcompAbbr = db[dbDict[comp]]['attrs']['abbreviation']['value']
      bfcompType = db[dbDict[comp]]['attrs']['type']['value']
      bfcompTitle = db[dbDict[comp]]['attrs']['title']['value']
      f.write('[' + bfcompAbbr + ': ' + bfcompTitle + '] as ' + bfcompAbbr +
            ' <<' + bfcompType + '>> ' + env.PhyColor + '\n')

    # add links
    for link, hint in linkDict.items():
      if 'connects to' in db[dbDict[link]]['rels']:
        if len(db[dbDict[link]]['rels']['connects to']) == 2:
          ctc1 = db[dbDict[link]]['rels']['connects to'][0]
          c1Abbrv = db[ctc1['targetId']]['attrs']['abbreviation']['value']
          ctc2 = db[dbDict[link]]['rels']['connects to'][1]
          c2Abbrv = db[ctc2['targetId']]['attrs']['abbreviation']['value']
          f.write(c1Abbrv + ' -' + hint + '- ' + c2Abbrv + ' ' +
                  env.IntfColor + ';line.bold : ' + link + '\n')
        else:
          print("Both endpoints not set for: " + link)

    f.write('@enduml\n')

  # setup output area
  output = widgets.Output(layout={'border': '1px solid black'})
  display(output)
  # display pb diagram to output area
  with output:
    displayPlantUML(env.plantuml, inputPath)

  return