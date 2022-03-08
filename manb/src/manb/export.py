import requests
from .env import Environment
from .pr import Project
from pprint import pprint
from IPython.display import clear_output
import json
import os

# Export project db - schema definition & entities
class Export:
  def __init__(this, env: Environment):
    this.env = env

    with open('./projects/projects.json') as f:
      projects = json.load(f)

      found = False
      for proj in projects:
        if proj['id'] == this.env.projectDict[this.env.project.value]:
          this.projPath = proj['path']
          found = True

      if found != True:
        print("Selected project not found in projects.json")
      else:
        # Create project export directory
        if not os.path.exists('./projects/' + this.projPath):
          os.makedirs('./projects/' + this.projPath)
        print("Export project to: ./projects/" + this.projPath)
    return

  def Dump(this):
    clear_output()
    print("Loading selected project....")
    # load selected project
    this.compTypes = ['Category', 'Component', 'ControlAction', 'DomainSet',
                      'Exit', 'Feedback', 'Function', 'Hazard', 'HazardousAction',
                      'Item', 'Link', 'Loss', 'LossScenario', 'UseCase']

    this.pr = Project(this.env)
    this.pr.FetchSchema()
    this.pr.FetchEntities(this.compTypes)
    this.pr.FetchStructure()

    clear_output()
    print('Dumping schema to ' + this.projPath)

    with open('./projects/' + this.projPath + '/n2idEntityDict.json', 'w') as f:
      json.dump(this.pr.n2idEntityDict, f, indent=2)
    with open('./projects/' + this.projPath + '/id2nEntityDict.json', 'w') as f:
      json.dump(this.pr.id2nEntityDict, f, indent=2)
    with open('./projects/' + this.projPath + '/id2nRelDict.json', 'w') as f:
      json.dump(this.pr.id2nRelDict, f, indent=2)
    with open('./projects/' + this.projPath + '/n2idRelDict.json', 'w') as f:
      json.dump(this.pr.n2idRelDict, f, indent=2)

    clear_output()
    print('Dumping entities to ' + this.projPath)
    with open('./projects/' + this.projPath + '/entities.json', 'w') as f:
      json.dump(this.pr.entities, f, indent=2)
    with open('./projects/' + this.projPath + '/entitiesDict.json', 'w') as f:
      json.dump(this.pr.entitiesDict, f, indent=2)
    with open('./projects/' + this.projPath + '/entitiesForTypeList.json', 'w') as f:
      json.dump(this.pr.entitiesForTypeList, f, indent=2)

    clear_output()
    print('Dumping structures to ' + this.projPath)
    with open('./projects/' + this.projPath + '/structures.json', 'w') as f:
      json.dump(this.pr.structures, f, indent=2)

    clear_output()
    print("Project Dump Complete!")