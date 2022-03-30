import ipywidgets as widgets
from IPython.display import display
from .env import Environment
from .pr import Project
from pprint import pprint
import pandas as pd
import html

def createReqTable(env: Environment, pr: Project, groups: list):

  db = pr.entities
  dbDict = pr.entitiesDict
  reqDF = {}

  reqTable = []
  for group in groups:
    for req in db[dbDict[group]]['rels']['groups']:
      reqItem = []
      reqItem.append(db[req['targetId']]['attrs']['number']['value'])
      reqItem.append(db[req['targetId']]['attrs']['name']['value'])
      reqItem.append(html.escape(db[req['targetId']]['attrs']\
                                                ['description']['value']))
      reqItem.append(db[req['targetId']]['attrs']['type']['value'])

      refineList = " "
      if 'refines' in db[req['targetId']]['rels']:
        first = True
        for refine in db[req['targetId']]['rels']['refines']:
          refineNum = db[refine['targetId']]['attrs']['number']['value']
          if first == True:
            first = False
          else:
            refineList += ','
          refineList += refineNum

      reqItem.append(refineList)
      reqTable.append(reqItem)

  reqDF = pd.DataFrame(reqTable, columns = ['ID', 'Title',\
                    'Description', 'Type', 'refines: Requirement'])

  # setup output area
  output = widgets.Output(layout={'border': '1px solid black'})
  display(output)

  with output:
    display(reqDF)

  return
