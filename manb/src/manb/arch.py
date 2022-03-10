from .env import Environment
from .pr import Project
from .msc import drawMSC
from IPython.display import clear_output, display
from pprint import pprint
import pandas as pd
import ipywidgets as widgets

class ResilienceArchitecture:

  def __init__(this, env: Environment):
    this.env = env
    this.compTypes = ['Category', 'Component', 'ControlAction', 'Exit',
                      'Feedback', 'Function', 'Hazard', 'HazardousAction',
                      'Item', 'Link', 'Loss', 'LossScenario', 'Remediation',
                      'Requirement', 'ResilientMode', 'Resource', 'UseCase']

    this.pr = Project(env)
    this.pr.FetchSchema()
    this.pr.FetchEntities(this.compTypes)
    this.pr.FetchStructure()

    this.output = {}

    # resilient mode table
    this.rmDF = {}

    # loss scenario table
    this.lsDF = {}
    return

  def ResilientModeTable(this):
    db = this.pr.entities

    rmTable = []
    for rm in this.pr.entitiesForTypeList['ResilientMode']:
      rmItem = []
      rmItem.append(db[rm]['attrs']['number']['value'])
      rmItem.append(db[rm]['attrs']['name']['value'])
      rmItem.append(db[rm]['attrs']['description']['value'])
      rmItem.append(db[rm]['attrs']['effectiveness']['value'])

      lsList = " "
      if 'ma: provides reconfiguration for' in db[rm]['rels']:
        first = True
        for ls in db[rm]['rels']['ma: provides reconfiguration for']:
          lsNum = db[ls['targetId']]['attrs']['number']['value']
          if first == True:
            first = False
          else:
            lsList += ','
          lsList += lsNum

      rmItem.append(lsList)
      rmTable.append(rmItem)

    this.rmDF = pd.DataFrame(rmTable, columns = ['ID', 'Resilient Mode',\
                      'Description', 'Effectiveness',
                      'provides reconfig for: LS'])

    # setup output area
    this.output = widgets.Output(layout={'border': '1px solid black'})
    display(this.output)

    with this.output:
      display(this.rmDF)
    return

  def LossScenarioElaborationTable(this):
    db = this.pr.entities

    lsTable = []
    for ls in this.pr.entitiesForTypeList['LossScenario']:
      lsItem = []
      lsItem.append(db[ls]['attrs']['number']['value'])
      lsItem.append(db[ls]['attrs']['name']['value'])
      lsItem.append(db[ls]['attrs']['detect-pattern']['value'])
      lsItem.append(db[ls]['attrs']['likelihood']['value'])

      rmList = " "
      if 'ma: reconfigures using' in db[ls]['rels']:
        first = True
        for rm in db[ls]['rels']['ma: reconfigures using']:
          rmNum = db[rm['targetId']]['attrs']['number']['value']
          if first == True:
            first = False
          else:
            rmList += ','
          rmList += rmNum

      lsItem.append(rmList)
      lsTable.append(lsItem)

    this.lsDF = pd.DataFrame(lsTable, columns = ['ID', 'Name',\
                      'Detect Pattern', 'Likelihood',
                      'reconfigures uing: RM'])

    # setup output area
    this.output = widgets.Output(layout={'border': '1px solid black'})
    display(this.output)

    with this.output:
      display(this.lsDF)
    return

  def LossScenarioMSCDiagrams(this):
    db = this.pr.entities
    dbDict = this.pr.entitiesDict

    # get category ID for Loss Scenarios
    lsCatId = dbDict['RA: Loss Scenarios']

    # retrieve categorized Loss Scenarios
    for ls in db[lsCatId]['rels']['categorizes']:
      drawMSC(ls['targetId'], this.env, this.pr)

    return

  def ElicitedRequirementsTable(this):
    return