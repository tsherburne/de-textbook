from .env import Environment
from .sd import SystemDescription
from .pr import Project
import requests
from IPython.display import clear_output, display
import sys
from pprint import pprint
import pandas as pd
import ipywidgets as widgets


class RiskAssessment:
  def __init__(this, env: Environment):
    this.env = env

    this.compTypes = ['Category', 'ControlAction', 'Hazard', 'Loss', 'HazardousAction']

    this.pr = Project(env)
    this.pr.FetchSchema()
    this.pr.FetchEntities(this.compTypes)

    this.output = {}

    # losses
    this.lossDF = {}
    this.lossDT = {}

    # hazards
    this.hazardDF = {}
    this.hazardDT = {}

    # hazardous control action
    this.hcaDF = {}
    this.hcaDT = {}

    # control action analysis
    this.caaDF = {}
    this.caaDT = {}

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

    this.lossDF = pd.DataFrame(lossTable, columns = ['ID', 'Title', 'Priority', \
                                        'is caused by: Hazard'])

    # setup output area
    this.output = widgets.Output(layout={'border': '1px solid black'})
    display(this.output)

    with this.output:
      try:
        from google.colab import data_table
        data_table.enable_dataframe_formatter()
        this.lossDT = data_table.DataTable(this.lossDF, include_index=False)
        # Display dataframa via Colab datatable
        display(this.lossDT)
      except ModuleNotFoundError:
        # Display basic dataframe
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

    this.hazardDF = pd.DataFrame(hazardTable, columns = ['ID', 'Title', 'Description', \
                    'leads to: Loss', 'is caused by: Hazardous Action'])

    # setup output area
    this.output = widgets.Output(layout={'border': '1px solid black'})
    display(this.output)

    with this.output:
      try:
        from google.colab import data_table
        data_table.enable_dataframe_formatter()
        this.hazardDT = data_table.DataTable(this.hazardDF, include_index=False)
        # Display dataframa via Colab datatable
        display(this.hazardDT)
      except ModuleNotFoundError:
        # Display basic dataframe
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

    this.hcaDF = pd.DataFrame(hcaTable, columns = ['ID', 'Title', 'Description', \
                    'Variation Type', 'leads to: Hazard', 'variation of: Control Action'])

    # setup output area
    this.output = widgets.Output(layout={'border': '1px solid black'})
    display(this.output)

    with this.output:
      try:
        from google.colab import data_table
        data_table.enable_dataframe_formatter()
        this.hcaDT = data_table.DataTable(this.hcaDF, include_index=False)
        # Display dataframa via Colab datatable
        display(this.hcaDT)
      except ModuleNotFoundError:
        # Display basic dataframe
        display(this.hcaDF)

  def ControlActionAnalysisTable(this):
    db = this.pr.entities
    dbTypeList = this.pr.entitiesForTypeList

    caaTable = []
    for ca in dbTypeList['ControlAction']:
      for hcaType in this.hcaTypes:
        caItem = []
        caItem.append(db[ca]['attrs']['title']['value'])
        caItem.append(hcaType)
        # check if hca of this type exists for this ca
        if 'ma: has variation' in db[ca]['rels']:
          for hca in db[ca]['rels']['ma: has variation']:
            if db[hca['targetId']]['attrs']['variationType']['value'] == hcaType:
              caItem.append(db[hca['targetId']]['attrs']['number']['value'])
            else:
              caItem.append(' ')
        else:
          caItem.append(' ')

        # Todo: save / retrieve variation type justification
        caItem.append(' ')
        caaTable.append(caItem)

    this.caaDF = pd.DataFrame(caaTable, columns = ['Control Action', 'Variation', \
                    'has variation: Hazardous Action', 'has variation: .justification'])

    # setup output area
    this.output = widgets.Output(layout={'border': '1px solid black'})
    display(this.output)

    with this.output:
      try:
        from google.colab import data_table
        data_table.enable_dataframe_formatter()
        this.caaDT = data_table.DataTable(this.caaDF, include_index=False)
        # Display dataframa via Colab datatable
        display(this.caaDT)
      except ModuleNotFoundError:
        # Display basic dataframe
        display(this.caaDF)

