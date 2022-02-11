from manb.sd import SystemDescription
from .env import Environment
from .pr import Project
import requests
from IPython.display import clear_output, display
import sys
from pprint import pprint
import pandas as pd
import ipywidgets as widgets

class VulnerabilityAssessment:
  def __init__(this, env: Environment):
    this.env = env

    this.compTypes = ['Category', 'Component', 'ControlAction', 'DomainSet',
                      'Exit', 'Feedback', 'Function', 'HazardousAction',
                      'LossScenario', 'Link', 'UseCase']

    this.pr = Project(env)
    this.pr.FetchSchema()
    this.pr.FetchEntities(this.compTypes)

    this.output = {}

    # loss scenario table
    this.lsDF = {}
    this.lsDT = {}

    # component analysis table
    this.caDF = {}
    this.caDT = {}

    clear_output()
    print("Vulnerability Assessment Complete!")

  def LossScenarioTable(this):
    db = this.pr.entities
    dbTypeList = this.pr.entitiesForTypeList


    lsTable = []
    for ls in dbTypeList['LossScenario']:
      lsItem = []
      lsItem.append(db[ls]['attrs']['number']['value'])
      lsItem.append(db[ls]['attrs']['name']['value'])
      lsItem.append(db[ls]['attrs']['sub-type']['value'])

      targetsList = " "
      if 'ma: targets' in db[ls]['rels']:
        first = True
        for target in db[ls]['rels']['ma: targets']:
          if db[target['targetId']]['type'] == 'ControlAction':
            targetNum = 'CA::'
          elif db[target['targetId']]['type'] == 'Feedback':
            targetNum = 'FB::'
          elif db[target['targetId']]['type'] == 'Function':
            targetNum = 'F::'
          else:
            targetNum = ''
          targetNum += db[target['targetId']]['attrs']['name']['value']
          if first == True:
            first = False
          else:
            targetsList += ','
          targetsList += targetNum
      lsItem.append(targetsList)

      hcaList = " "
      if 'ma: leads to' in db[ls]['rels']:
        first = True
        for hca in db[ls]['rels']['ma: leads to']:
          hcaNum = db[hca['targetId']]['attrs']['number']['value']
          if first == True:
            first = False
          else:
            hcaList += ','
          hcaList += hcaNum
      lsItem.append(hcaList)

      lsTable.append(lsItem)

    this.lsDF = pd.DataFrame(lsTable, columns = ['ID', 'Title', 'Sub-Type',\
                      'targets: Item/Function', 'leads to: HCA'])

    # setup output area
    this.output = widgets.Output(layout={'border': '1px solid black'})
    display(this.output)

    with this.output:
      try:
        from google.colab import data_table
        data_table.enable_dataframe_formatter()
        this.lsDT = data_table.DataTable(this.lsDF, include_index=False)
        # Display dataframa via Colab datatable
        display(this.lsDT)
      except ModuleNotFoundError:
        # Display basic dataframe
        display(this.lsDF)
    return

  # Components - Loss Scenario Analysis
  def ComponentAnalysisTable(this):
    db = this.pr.entities
    dbDict = this.pr.entitiesDict

    dbTypeList = this.pr.entitiesForTypeList

    # get category ID for System Control Structure Components
    compCatId = dbDict['SD: CS: Components']

    caTable = []
    # retrieve components
    for comp in db[compCatId]['rels']['categorizes']:
      # skip Context component
      if db[comp['targetId']]['attrs']['type']['value'] != 'Context':
        compId = db[comp['targetId']]['attrs']['number']['value']
        compTitle = db[comp['targetId']]['attrs']['title']['value']
        # retrieve functions
        if 'performs' in db[comp['targetId']]['rels']:
          for func in db[comp['targetId']]['rels']['performs']:
            funcName = db[func['targetId']]['attrs']['name']['value']
            # retrieve parent use case
            if 'decomposes' in db[func['targetId']]['rels']:
              ucId = db[func['targetId']]['rels']['decomposes'][0]
              ucNum = db[ucId['targetId']]['attrs']['number']['value']
            else:
              # function does not decompose a use case
              continue

            # retrieve 'outputs' - ca / fb
            if 'outputs' in db[func['targetId']]['rels']:
              for item in db[func['targetId']]['rels']['outputs']:
                itemName = db[item['targetId']]['attrs']['name']['value']
                itemFlow = ""
                if db[item['targetId']]['type'] == 'ControlAction':
                  itemFlow = '->CA::' + itemName
                elif db[item['targetId']]['type'] == 'Feedback':
                  itemFlow = '->FB::' + itemName
                else:
                  # item is not a control action or feedback
                  continue

                # check if function is 'ma: targeted by' a loss scenario
                lsList = this._get_targeted_by(func, itemFlow[0:4])

                caItem = []
                caItem.append(compId)
                caItem.append(compTitle)
                caItem.append('(' + ucNum + ') ' + funcName)
                caItem.append(itemFlow)
                caItem.append(lsList)
                caTable.append(caItem)

            # retrieve 'inputs' - ca / fb
            if 'inputs' in db[func['targetId']]['rels']:
              for item in db[func['targetId']]['rels']['inputs']:
                itemName = db[item['targetId']]['attrs']['name']['value']
                itemFlow = ""
                if db[item['targetId']]['type'] == 'ControlAction':
                  itemFlow = '<-CA::' + itemName
                elif db[item['targetId']]['type'] == 'Feedback':
                  itemFlow = '<-FB::' + itemName
                else:
                  # item is not a control action or feedback
                  continue

                # check if function is 'ma: targeted by' a loss scenario
                lsList = this._get_targeted_by(func, itemFlow[0:4])
                caItem = []
                caItem.append(compId)
                caItem.append(compTitle)
                caItem.append('(' + ucNum + ') ' + funcName)
                caItem.append(itemFlow)
                caItem.append(lsList)
                caTable.append(caItem)


    this.caDF = pd.DataFrame(caTable, columns = ['ID', 'Title',\
                      '(UC) Function', 'Item', 'targeted by:LS(sub-type)'])

    # setup output area
    this.output = widgets.Output(layout={'border': '1px solid black'})
    display(this.output)

    with this.output:
      try:
        from google.colab import data_table
        data_table.enable_dataframe_formatter()
        this.caDT = data_table.DataTable(this.caDF, include_index=False)
        # Display dataframa via Colab datatable
        display(this.lsDT)
      except ModuleNotFoundError:
        # Display basic dataframe
        display(this.caDF)
    return


  # Links - Loss Scenario Analysis
  def LinkAnalysisTable(this):
    db = this.pr.entities
    dbTypeList = this.pr.entitiesForTypeList
    return

  # get 'ma: targeted by' loss scenario list
  def _get_targeted_by(this, func: dict, itemFlow: str) -> str:
    db = this.pr.entities

    lsList = " "
    if 'ma: targeted by' in db[func['targetId']]['rels']:
      first = True
      for ls in db[func['targetId']]['rels']['ma: targeted by']:
        lsNum = db[ls['targetId']]['attrs']['number']['value']
        lsType = db[ls['targetId']]['attrs']['sub-type']['value']
        # function is controller with output control action
        if itemFlow == '->CA' and lsType[0:3] == 'a.1':
          pass
        # function is controlled process with input control action
        elif itemFlow == '<-CA' and lsType[0:3] == 'b.4':
          pass
        # function is controlled process with output feedback
        elif itemFlow == '->FB' and lsType[0:3] == 'b.4':
          pass
        # function is controller with input feedback
        elif itemFlow == '<-FB' and lsType[0:3] == 'a.1':
          pass
        else:
          continue

        if first == True:
          first = False
        else:
          lsList += ','
        lsList += lsNum + '(' + lsType[0:3] + ')'
    return lsList