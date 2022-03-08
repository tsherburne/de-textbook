from .env import Environment
from .pr import Project
from typing import Tuple


def getItemList(env: Environment, pr: Project) -> Tuple[list, dict]:
  itemByName = {}
  itemList = []
  db = pr.entities
  dbDict = pr.entitiesDict
  csFuncCatId = dbDict['SD: CS: Functions']

  # fetch output control actions and feedback items
  for function in db[csFuncCatId]['rels']['categorizes']:
    if 'outputs' in db[function['targetId']]['rels']:
      for output in db[function['targetId']]['rels']['outputs']:
        itemEntry = {}
        itemEntry['itemId'] = output['targetId']
        itemEntry['itemTitle'] = db[output['targetId']]['attrs']['title']\
                  ['value']
        itemEntry['itemDescription'] = db[output['targetId']]['attrs']\
                  ['description']['value']
        itemEntry['itemType'] = db[output['targetId']]['type']
        itemEntry['inputComponent'] = ""
        outCompId = db[function['targetId']]['rels']['allocated to'][0]
        itemEntry['outputComponent'] = db[outCompId['targetId']]['attrs']\
                  ['abbreviation']['value']

        # add to list and dict
        itemList.append(itemEntry['itemTitle'])
        itemByName[itemEntry['itemTitle']] = itemEntry

  # fetch input control actions and feedback items
  for function in db[csFuncCatId]['rels']['categorizes']:
    if 'inputs' in db[function['targetId']]['rels']:
      for input in db[function['targetId']]['rels']['inputs']:
        inCompId = db[function['targetId']]['rels']['allocated to'][0]
        itemTitle = db[input['targetId']]['attrs']['title']['value']
        # update input component
        itemByName[itemTitle]['inputComponent'] = \
                db[inCompId['targetId']]['attrs']['abbreviation']['value']

  itemList.sort()
  return(itemList, itemByName)
