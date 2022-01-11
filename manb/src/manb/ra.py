from .env import Environment
from .cs import ControlStructure
import requests
from IPython.display import clear_output
import sys
from pprint import pprint
import pandas as pd
import ipywidgets as widgets


class RiskAssessment:
  def __init__(this, env: Environment, cs: ControlStructure):
    this.env = env
    this.cs = cs

    this.lossList = []
    this.lossesById = {}
    this.lossDF = {}
    this.lossDT = {}

    this.hazardList = []
    this.hazardsById = {}
    this.hazardDF = {}
    this.hazardDT = {}

    this.hcaList = []
    this.hcasById = {}
    this.hcaDF = {}
    this.hcaDT = {}

    clear_output()
    print("Initializing Risk Assessment....")

    # fetch losses
    r = requests.get(this.env.url + 'projects/' +
                this.env.projectDict[this.env.project.value] +
                '/folders/' + this.env.entityDict['Loss'] + '/entities?sortBlockId=' +
                this.env.sortBlockDict['Numeric'],
                allow_redirects=False, headers=this.env.header)

    if r.status_code != 200:
      sys.exit("Error Fetching Losses: " + str(r.status_code))
    else:
      losses = r.json()['results']
      for loss in losses:
        lossEntry = {}
        lossId = ""

        for attr in loss['attributes']:
          if attr['definitionId'] == this.env.attributeDict['number']:
            if attr['value'] is not None:
              lossId = attr['value']['value']
          elif attr['definitionId'] == this.env.attributeDict['name']:
            if attr['value'] is not None:
              lossEntry['lossName'] = attr['value']['value']
          elif attr['definitionId'] == this.env.attributeDict['description']:
            if attr['value'] is not None:
              lossEntry['lossDescription'] = attr['value']['value']['plainText']
          elif attr['definitionId'] == this.env.attributeDict['priority']:
            if attr['value'] is not None:
              lossEntry['lossPriority'] = attr['value']['value']['value']
        # fetch related hazards (ma: is caused by)
        r2 = requests.get(this.env.url + 'projects/' +
                  this.env.projectDict[this.env.project.value] +
                  '/entities/' + loss['id'] +
                  '/relationshiptargets/' + this.env.relationDict['ma: is caused by'] +
                  '?sortBlockId=' + this.env.sortBlockDict['Numeric'],
                  allow_redirects=False, headers=this.env.header)
        if r2.status_code != 200:
          sys.exit("Error Fetching Related Hazards: " + str(r2.status_code))
        else:
          hazards = r2.json()['results']
          first = True
          lossEntry['hazardList'] = ""
          for hazard in hazards:
            for attr in hazard['attributes']:
              if attr['definitionId'] == this.env.attributeDict['number']:
                if attr['value'] is not None:
                  if first == True:
                    first = False
                  else:
                    lossEntry['hazardList'] += ','
                  lossEntry['hazardList'] += attr['value']['value']
        # save loss
        this.lossList.append(lossId)
        this.lossesById[lossId] = lossEntry

    # fetch hazards
    r = requests.get(this.env.url + 'projects/' + this.env.projectDict[this.env.project.value] +
                    '/folders/' + this.env.entityDict['Hazard'] + '/entities?sortBlockId=' +
                    this.env.sortBlockDict['Numeric'],
                    allow_redirects=False, headers=this.env.header)

    if r.status_code != 200:
      sys.exit("Error Fetching Hazards: " + str(r.status_code))
    else:
      hazards = r.json()['results']
      for hazard in hazards:
        hazardEntry = {}
        hazardId = " "
        for attr in hazard['attributes']:
          if attr['definitionId'] == this.env.attributeDict['number']:
            if attr['value'] is not None:
              hazardId = attr['value']['value']
          elif attr['definitionId'] == this.env.attributeDict['name']:
            if attr['value'] is not None:
              hazardEntry['hazardName'] = attr['value']['value']
          elif attr['definitionId'] == this.env.attributeDict['description']:
            if attr['value'] is not None:
              hazardEntry['hazardDescription'] = attr['value']['value']['plainText']

        # fetch related losses (ma: leads to)
        r2 = requests.get(this.env.url + 'projects/' + this.env.projectDict[this.env.project.value] +
                  '/entities/' + hazard['id'] +
                  '/relationshiptargets/' + this.env.relationDict['ma: leads to'] +
                  '?sortBlockId=' + this.env.sortBlockDict['Numeric'],
                  allow_redirects=False, headers=this.env.header)
        if r2.status_code != 200:
          sys.exit("Error Fetching Related Hazards: " + str(r2.status_code))
        else:
          losses = r2.json()['results']
          first = True
          hazardEntry['lossList'] = " "
          for loss in losses:
            if loss['entityDefinitionId'] == this.env.entityDict['Loss']:
              for attr in loss['attributes']:
                if attr['definitionId'] == this.env.attributeDict['number']:
                  if attr['value'] is not None:
                    if first == True:
                      first = False
                    else:
                      hazardEntry['lossList'] += ','
                    hazardEntry['lossList'] += attr['value']['value']

        # fetch related hazardous control actions (ma: is caused by)
        r2 = requests.get(this.env.url + 'projects/' + this.env.projectDict[this.env.project.value] +
                  '/entities/' + hazard['id'] +
                  '/relationshiptargets/' + this.env.relationDict['ma: is caused by'] +
                  '?sortBlockId=' + this.env.sortBlockDict['Numeric'],
                  allow_redirects=False, headers=this.env.header)
        if r2.status_code != 200:
          sys.exit("Error Fetching Related HCA: " + str(r2.status_code))
        else:
          hcas = r2.json()['results']
          first = True
          hazardEntry['hcaList'] = " "
          for hca in hcas:
            if hca['entityDefinitionId'] == this.env.entityDict['HazardousAction']:
              for attr in hca['attributes']:
                if attr['definitionId'] == this.env.attributeDict['number']:
                  if attr['value'] is not None:
                    if first == True:
                      first = False
                    else:
                      hazardEntry['hcaList'] += ','
                    hazardEntry['hcaList'] += attr['value']['value']
        # save hazard
        this.hazardList.append(hazardId)
        this.hazardsById[hazardId] = hazardEntry

    # fetch hca
    r = requests.get(this.env.url + 'projects/' + this.env.projectDict[this.env.project.value] +
                    '/folders/' + this.env.entityDict['HazardousAction'] + '/entities?sortBlockId=' +
                    this.env.sortBlockDict['Numeric'],
                    allow_redirects=False, headers=this.env.header)
    if r.status_code != 200:
      sys.exit("Error Fetching HCAs: " + str(r.status_code))
    else:
      hcas = r.json()['results']
      for hca in hcas:
        hcaId = ""
        hcaEntry = {}
        for attr in hca['attributes']:
          if attr['definitionId'] == this.env.attributeDict['number']:
            if attr['value'] is not None:
              hcaId = attr['value']['value']
          elif attr['definitionId'] == this.env.attributeDict['name']:
            if attr['value'] is not None:
              hcaEntry['hcaName'] = attr['value']['value']
          elif attr['definitionId'] == this.env.attributeDict['description']:
            if attr['value'] is not None:
              hcaEntry['hcaDescription'] = attr['value']['value']['plainText']
          elif attr['definitionId'] == this.env.attributeDict['variationType']:
            if attr['value'] is not None:
              hcaEntry['hcaVariationType'] = attr['value']['value']['value']

        # fetch related hazards (ma: leads to)
        r2 = requests.get(this.env.url + 'projects/' + this.env.projectDict[this.env.project.value] +
                  '/entities/' + hca['id'] +
                  '/relationshiptargets/' + this.env.relationDict['ma: leads to'] +
                  '?sortBlockId=' + this.env.sortBlockDict['Numeric'],
                  allow_redirects=False, headers=this.env.header)
        if r2.status_code != 200:
          sys.exit("Error Fetching Related Hazards: " + str(r2.status_code))
        else:
          hazards = r2.json()['results']
          first = True
          hcaEntry['hazardList'] = " "
          for hazard in hazards:
            if hazard['entityDefinitionId'] == this.env.entityDict['Hazard']:
              for attr in hazard['attributes']:
                if attr['definitionId'] == this.env.attributeDict['number']:
                  if attr['value'] is not None:
                    if first == True:
                      first = False
                    else:
                      hcaEntry['hazardList'] += ','
                    hcaEntry['hazardList'] += attr['value']['value']

        # fetch related control actions (ma: is variation of)
        r2 = requests.get(this.env.url + 'projects/' + this.env.projectDict[this.env.project.value] +
                  '/entities/' + hca['id'] +
                  '/relationshiptargets/' + this.env.relationDict['ma: variation of'] +
                  '?sortBlockId=' + this.env.sortBlockDict['Numeric'],
                  allow_redirects=False, headers=this.env.header)
        if r2.status_code != 200:
          sys.exit("Error Fetching Related CA: " + str(r2.status_code))
        else:
          controlActions = r2.json()['results']
          first = True
          hcaEntry['relatedCAList'] = " "
          for controlAction in controlActions:
            if controlAction['entityDefinitionId'] == this.env.entityDict['ControlAction']:
              for attr in controlAction['attributes']:
                if attr['definitionId'] == this.env.attributeDict['ca:title']:
                  if attr['value'] is not None:
                    if first == True:
                      first = False
                    else:
                      hcaEntry['relatedCAList'] += ','
                    hcaEntry['relatedCAList'] += attr['value']['value']

        this.hcaList.append(hcaId)
        this.hcasById[hcaId] = hcaEntry

    this.lossList.sort()
    this.hazardList.sort()
    this.hcaList.sort()
    clear_output()
    print("Risk Assessment Initialization Complete!")

  def LossTable(this):
    lossTable = []
    for loss in this.lossList:
        lossItem = []
        lossItem.append(loss)
        lossItem.append(this.lossesById[loss]['lossName'])
        lossItem.append(this.lossesById[loss]['lossPriority'])
        lossItem.append(this.lossesById[loss]['hazardList'])
        lossTable.append(lossItem)

    this.lossDF = pd.DataFrame(lossTable, columns = ['ID', 'Title', 'Priority', 'is caused by: Hazard'])

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
    hazardTable = []
    for hazard in this.hazardList:
        hazardItem = []
        hazardItem.append(hazard)
        hazardItem.append(this.hazardsById[hazard]['hazardName'])
        hazardItem.append(this.hazardsById[hazard]['hazardDescription'])
        hazardItem.append(this.hazardsById[hazard]['lossList'])
        hazardItem.append(this.hazardsById[hazard]['hcaList'])

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
    hcaTable = []
    for hca in this.hcaList:
        hcaItem = []
        hcaItem.append(hca)
        hcaItem.append(this.hcasById[hca]['hcaName'])
        hcaItem.append(this.hcasById[hca]['hcaDescription'])
        hcaItem.append(this.hcasById[hca]['hcaVariationType'])
        hcaItem.append(this.hcasById[hca]['hazardList'])
        hcaItem.append(this.hcasById[hca]['relatedCAList'])

        hcaTable.append(hcaItem)

    this.hcaDF = pd.DataFrame(hcaTable, columns = ['ID', 'Title', 'Description', \
                    'Variation Type', 'leads to: Hazard', 'is variation of: Control Action'])

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
