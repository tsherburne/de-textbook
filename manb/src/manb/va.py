from tty import CC
from manb.sd import SystemDescription
from .env import Environment
from .pr import Project
from .comp import drawComp
from IPython.display import clear_output, display
from IPython.display import Image
from pprint import pprint
import pandas as pd
import ipywidgets as widgets
import copy


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

    # component analysis table
    this.caDF = {}

    # link analysis table
    this.laDF = {}

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

    this.lsDF = pd.DataFrame(lsTable, columns = ['ID', 'Name', 'Sub-Type',\
                      'targets: Item/Function', 'leads to: HCA'])

    # setup output area
    this.output = widgets.Output(layout={'border': '1px solid black'})
    display(this.output)

    with this.output:
      display(this.lsDF)
    return

  # Physical Block Diagrams
  def PhysicalBlockDiagrams(this):
    db = this.pr.entities
    dbDict = this.pr.entitiesDict
    clear_output()

    # get category ID for Physical Block Diagrams
    compCatId = dbDict['PA: Block Diagrams']

    for bd in db[compCatId]['rels']['categorizes']:
      drawComp(bd['targetId'], this.env, this.pr)

    return


  # Components - Loss Scenario Analysis
  def ComponentAnalysisTable(this):
    db = this.pr.entities
    dbDict = this.pr.entitiesDict

    # get category ID for System Control Structure Components
    compCatId = dbDict['SD: CS: Components']

    caTable = []
    # retrieve components
    for comp in db[compCatId]['rels']['categorizes']:
      # skip Context component
      if db[comp['targetId']]['attrs']['type']['value'] != 'Context':
        compId = db[comp['targetId']]['attrs']['number']['value']
        compTitle = db[comp['targetId']]['attrs']['title']['value']
        compAbbr = db[comp['targetId']]['attrs']['abbreviation']['value']

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
                lsList = this._get_targeted_by(db[func['targetId']],
                                                            itemFlow[0:4])

                caItem = []
                caItem.append(compAbbr + ':' + compTitle)
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
                lsList = this._get_targeted_by(db[func['targetId']],
                                                            itemFlow[0:4])
                caItem = []
                caItem.append(compAbbr + ':' + compTitle)
                caItem.append('(' + ucNum + ') ' + funcName)
                caItem.append(itemFlow)
                caItem.append(lsList)
                caTable.append(caItem)


    this.caDF = pd.DataFrame(caTable, columns = ['Component',\
                      '(UC) Function', 'Item', 'targeted by:LS(sub-type)'])

    # setup output area
    this.output = widgets.Output(layout={'border': '1px solid black'})
    display(this.output)

    with this.output:
      display(this.caDF)
    return


  # Links - Loss Scenario Analysis
  def LinkAnalysisTable(this):
    db = this.pr.entities
    dbDict = this.pr.entitiesDict

    # get category ID for Physical Architecture Links
    linkCatId = dbDict['PA: Links']

    linkTable = []

    # retrieve links
    for link in db[linkCatId]['rels']['categorizes']:
      linkName = db[link['targetId']]['attrs']['name']['value']
      level = 0

      # messages that are 'transferred' over the link
      messages = {}

      # is current link at 'level' depth a 'connected component'
      cCompStack = []

      # components path for link using component abbreviations
      # for example: C1-C2:C3 where '-' represents link between
      # components and ':' represents link within a component
      components = []
      this._decompose_link(level, cCompStack, components, messages, link)

      for message in messages:

        linkItem = []
        linkItem.append(linkName)
        linkItem.append(messages[message]['msgPath'])
        linkItem.append(message)
        linkItem.append(messages[message]['lsList'])
        linkTable.append(linkItem)

    this.laDF = pd.DataFrame(linkTable, columns = ['Link',\
                      'Path', 'Item', 'targeted by:LS(sub-type)'])

    # setup output area
    this.output = widgets.Output(layout={'border': '1px solid black'})
    display(this.output)

    with this.output:
      display(this.laDF)
    return

  # decompose link - return list of dict: {connects: str, transfer: str}
  def _decompose_link(this, level:int, cCompStack:list, components:list,
                                          messages:dict, link:dict):
    db = this.pr.entities

    # retrieve link name and end-points
    linkName = db[link['targetId']]['attrs']['name']['value']
    ep1 = db[link['targetId']]['rels']['connects to'][0]
    ep2 = db[link['targetId']]['rels']['connects to'][1]
    ep1Dir = ep1['attrs']['hint']['value']
    ep2Dir = ep2['attrs']['hint']['value']
    ep1bf = db[ep1['targetId']]['rels']['built in'][0]
    ep1bfAbbr = db[ep1bf['targetId']]['attrs']['abbreviation']['value']
    ep2bf = db[ep2['targetId']]['rels']['built in'][0]
    ep2bfAbbr = db[ep2bf['targetId']]['attrs']['abbreviation']['value']

    epLName = ""
    epLbfName = ""
    epRName = ""
    epRbfName = ""

    # is current link processed as connecting component
    cComp = False

    if ep1Dir == 'd' or ep1Dir == 'r':
      # read top to bottom / right to left
      epLName = db[ep1['targetId']]['attrs']['abbreviation']['value']
      epRName = db[ep2['targetId']]['attrs']['abbreviation']['value']
      epLbfName = ep1bfAbbr
      epRbfName = ep2bfAbbr
    else:
      # swap end-points based on direction hint
      ep2Dir = ep1['attrs']['hint']['value']
      ep1Dir = ep2['attrs']['hint']['value']
      epRName = db[ep1['targetId']]['attrs']['abbreviation']['value']
      epLName = db[ep2['targetId']]['attrs']['abbreviation']['value']
      epRbfName = ep1bfAbbr
      epLbfName = ep2bfAbbr

    if len(components) == 0:
      # start of link decomposition
      components.append(epLName)
      components.append('-')
      components.append(epRName)
    elif epLName in components:
      if epRName not in components:
        # check if epRName 'built from' in components
        if epRbfName in components:
          # add a 'sub' component - to end of parent component chain
          try:
            # insert before 'connecting' component - if exists
            iPoint = components.index('-', components.index(epRbfName))
            components.insert(iPoint - 1, ':')
            components.insert(iPoint - 2, epRName)
          except ValueError:
            # no 'connecting' component - insert at end of chain
            components.append(':')
            components.append(epRName)
        else:
          # add as 'connecting' component
          components.insert(components.index(epLName) + 1, '-')
          components.insert(components.index(epLName) + 2, epRName)
          cComp = True
    elif epRName in components:
      if epLName not in components:
        # check if epLName 'built from' in components
        if epLbfName in components:
          # add a 'sub' component - to end of parent component chain
          try:
            # insert before 'connecting' component - if exists
            iPoint = components.index('-', components.index(epLbfName))
            components.insert(iPoint, ':')
            components.insert(iPoint + 1, epLName)
          except ValueError:
            print("Error #1 decomposing Link: " + linkName)
        else:
          # add as a 'connecting' component
          components.insert(components.index(epRName) - 1, '-')
          components.insert(components.index(epLName) - 2, epLName)
          cComp = True
    else:
      print("Error #2 decomposing Link: " + linkName)

    icomponents = copy.deepcopy(components)

    # save connected component status
    cCompStack.append(cComp)
    # decompose included links
    if 'includes' in db[link['targetId']]['rels']:
      for ilink in db[link['targetId']]['rels']['includes']:

        level += 2
        this._decompose_link(level, cCompStack, icomponents,
                                                    messages, ilink)
        level -= 2

        # if top of stack is a 'connecting component'
        # connecting components will be processed in pairs
        if cCompStack[-1] != True:
          # reset component list
          cCompStack.pop()
          icomponents = copy.deepcopy(components)

    # output transfer messages
    if 'transfers' in db[link['targetId']]['rels']:
      level += 2
      for item in db[link['targetId']]['rels']['transfers']:
        msgType = ""
        if db[item['targetId']]['type'] == 'ControlAction':
          msgType = '->CA::'
        elif db[item['targetId']]['type'] == 'Feedback':
          msgType = '<-FB::'

        msgName = msgType + db[item['targetId']]['attrs']['name']['value']

        msgEntry = {}
        msgEntry['msgPath'] = ''.join(icomponents)
        msgEntry['lsList'] = this._get_targeted_by(db[item['targetId']],
                                                        msgType[0:4])

        messages[msgName] = msgEntry

      level -= 2
    return

  # get 'ma: targeted by' loss scenario list
  def _get_targeted_by(this, entity: dict, itemFlow: str) -> str:
    db = this.pr.entities

    lsList = " "
    if 'ma: targeted by' in entity['rels']:
      first = True
      for ls in entity['rels']['ma: targeted by']:
        lsNum = db[ls['targetId']]['attrs']['number']['value']
        lsType = db[ls['targetId']]['attrs']['sub-type']['value']
        if entity['type'] == 'Function':
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
        elif entity['type'] == 'ControlAction':
          pass
        elif entity['type'] == 'Feedback':
          pass

        if first == True:
          first = False
        else:
          lsList += ','
        lsList += lsNum + '(' + lsType[0:3] + ')'
    return lsList