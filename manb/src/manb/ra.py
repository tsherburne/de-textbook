from .env import Environment
from .pr import Project
from .item import getItemList
from IPython.display import clear_output, display
from pprint import pprint
import pandas as pd
import ipywidgets as widgets

class RiskAssessment:
  def __init__(this, env: Environment):
    this.env = env

    this.compTypes = ['Category', 'Component', 'ControlAction', 'Function',
                      'Hazard', 'Loss', 'HazardousAction']

    this.pr = Project(env)
    this.pr.FetchSchema()
    this.pr.FetchEntities(this.compTypes)

    this.output = {}

    # losses
    this.lossDF = {}

    # hazards
    this.hazardDF = {}

    # hazardous control action
    this.hcaDF = {}

    # control action analysis
    this.caaDF = {}

    this.hcaTypes = ['Providing', 'NotProviding', 'TooEarlyTooLate']
    return

  def LossTable(this):
    db = this.pr.entities
    dbTypeList = this.pr.entitiesForTypeList


    lossTable = []
    for loss in dbTypeList['Loss']:
      lossItem = []
      lossItem.append(db[loss]['attrs']['number']['value'])
      lossItem.append(db[loss]['attrs']['name']['value'])
      lossItem.append(db[loss]['attrs']['priority']['value'])

      hazardList = " "
      if 'ma: is caused by' in db[loss]['rels']:
        first = True
        for hazard in db[loss]['rels']['ma: is caused by']:
          hazardNum = db[hazard['targetId']]['attrs']['number']['value']
          if first == True:
            first = False
          else:
            hazardList += ','
          hazardList += hazardNum
      lossItem.append(hazardList)
      lossTable.append(lossItem)

    this.lossDF = pd.DataFrame(lossTable, columns = ['ID', 'Title', \
                          'Priority', 'is caused by: Hazard'])

    # setup output area
    this.output = widgets.Output(layout={'border': '1px solid black'})
    display(this.output)

    with this.output:
      display(this.lossDF)

  def HazardTable(this):
    db = this.pr.entities
    dbTypeList = this.pr.entitiesForTypeList

    hazardTable = []
    for hazard in dbTypeList['Hazard']:
      hazardItem = []
      hazardItem.append(db[hazard]['attrs']['number']['value'])
      hazardItem.append(db[hazard]['attrs']['name']['value'])
      hazardItem.append(db[hazard]['attrs']['description']['value'])

      lossList = " "
      if 'ma: leads to' in db[hazard]['rels']:
        first = True
        for loss in db[hazard]['rels']['ma: leads to']:
          lossNum = db[loss['targetId']]['attrs']['number']['value']
          if first == True:
            first = False
          else:
            lossList += ','
          lossList += lossNum
      hazardItem.append(lossList)

      hcaList = " "
      if 'ma: is caused by' in db[hazard]['rels']:
        first = True
        for hca in db[hazard]['rels']['ma: is caused by']:
          hcaNum = db[hca['targetId']]['attrs']['number']['value']
          if first == True:
            first = False
          else:
            hcaList += ','
          hcaList += hcaNum
      hazardItem.append(hcaList)

      hazardTable.append(hazardItem)

    this.hazardDF = pd.DataFrame(hazardTable, columns = ['ID', 'Title', \
            'Description', 'leads to: Loss', 'is caused by: Hazardous Action'])

    # setup output area
    this.output = widgets.Output(layout={'border': '1px solid black'})
    display(this.output)

    with this.output:
      display(this.hazardDF)

  def HazardousActionTable(this):
    db = this.pr.entities
    dbTypeList = this.pr.entitiesForTypeList

    hcaTable = []
    for hca in dbTypeList['HazardousAction']:
      hcaItem = []
      hcaItem.append(db[hca]['attrs']['number']['value'])
      hcaItem.append(db[hca]['attrs']['name']['value'])
      hcaItem.append(db[hca]['attrs']['description']['value'])
      hcaItem.append(db[hca]['attrs']['variationType']['value'])

      hazardList = " "
      if 'ma: leads to' in db[hca]['rels']:
        first = True
        for hazard in db[hca]['rels']['ma: leads to']:
          hazardNum = db[hazard['targetId']]['attrs']['number']['value']
          if first == True:
            first = False
          else:
            hazardList += ','
          hazardList += hazardNum
      hcaItem.append(hazardList)

      caVariationList = " "
      if 'ma: variation of' in db[hca]['rels']:
        first = True
        for caVariation in db[hca]['rels']['ma: variation of']:
          caVariationNum = db[caVariation['targetId']]['attrs']['number']['value']
          if first == True:
            first = False
          else:
            caVariationList += ','
          caVariationList += caVariationNum
      hcaItem.append(caVariationList)

      hcaTable.append(hcaItem)

    this.hcaDF = pd.DataFrame(hcaTable, columns = ['ID', 'Title', \
                    'Description', 'Variation Type', 'leads to: Hazard', \
                    'variation of: Control Action'])

    # setup output area
    this.output = widgets.Output(layout={'border': '1px solid black'})
    display(this.output)

    with this.output:
      display(this.hcaDF)

  def ControlActionAnalysisTable(this):
    db = this.pr.entities
    dbTypeList = this.pr.entitiesForTypeList

    itemList, itemByName = getItemList(this.env, this.pr)

    caaTable = []
    for item in itemList:
      if itemByName[item]['itemType'] == 'ControlAction':
        for hcaType in this.hcaTypes:
          caItem = []
          caItem.append(itemByName[item]['itemNumber'])
          caItem.append(itemByName[item]['itemTitle'])
          caItem.append(hcaType)
          # check if hca of this type exists for this ca
          if 'ma: has variation' in db[itemByName[item]['itemId']]['rels']:
            for hca in db[itemByName[item]['itemId']]['rels']['ma: has variation']:
              if db[hca['targetId']]['attrs']['variationType']['value'] == hcaType:
                caItem.append(db[hca['targetId']]['attrs']['number']['value'])
              else:
                caItem.append(' ')
          else:
            caItem.append(' ')

          # Todo: save / retrieve variation type justification
          # caItem.append(' ')
          caaTable.append(caItem)

    this.caaDF = pd.DataFrame(caaTable, columns = ['ID', 'Control Action', \
                  'Variation', 'has variation: Hazardous Action'])

    # setup output area
    this.output = widgets.Output(layout={'border': '1px solid black'})
    display(this.output)

    with this.output:
      display(this.caaDF)

