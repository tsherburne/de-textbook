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
    return
  def ResilientModeTable(this):
    return

  def LossScenarioElaborationTable(this):
    return

  def LossScenarioMSCDiagrams(this):
    db = this.pr.entities
    dbDict = this.pr.entitiesDict
    structures = this.pr.structures

    # get category ID for Loss Scenarios
    lsCatId = dbDict['RA: Loss Scenarios']

    # retrieve categorized Loss Scenarios
    for ls in db[lsCatId]['rels']['categorizes']:
      drawMSC(ls['targetId'], this.env, this.pr)

    return

  def ElicitedRequirementsTable(this):
    return