from .env import Environment, Section
import requests
from pprint import pprint
import pandas as pd
import ipywidgets as widgets
from ipywidgets import Layout, Button, VBox, FloatText, Textarea
from ipywidgets import Dropdown, Label, IntSlider
from IPython.display import clear_output, display
import json


class Exercises:
  def __init__(this, env: Environment, section: Section):
    this.env = env
    this.section = section
    this.category = ""
    this.exList = []
    this.exDict = {}

    this.exDF = {}
    this.exDT = {}

    # form widget handles
    this.output = {}
    this.title = {}
    this.status = {}
    this.decision = {}
    this.save = {}
    this.result = {}
    this.table = {}
    this.vbox = {}

    if this.section.name == Section.RISK_ASSESSMENT.name:
      this.category = "EX: Risk Assessment"
    else:
      print("Invalid Exercises Section")
      return

    status, catId = this.env.getCategoryId(this.category)
    if status != 200:
      print("Failed to fetch assessment category: " + str(status))
      return

    # fetch 'categorized' exercises
    r = requests.get(this.env.url + 'projects/' +
                this.env.projectDict[this.env.project.value] +
                '/entities/' + catId +
                '/relationshiptargets/' + this.env.relationDict['categorizes'] +
                '?sortBlockId=' + this.env.sortBlockDict['Numeric'],
                allow_redirects=False, headers=this.env.header)
    if r.status_code != 200:
      print("Failed to fetch categorized Exercises: " + str(r.status_code))
      return

    # collect all exercises
    exercises = r.json()['results']
    for exercise in exercises:
      exTitle = ""
      exEntry = {}
      exEntry['entityDefinitionId'] = exercise['entityDefinitionId']
      exEntry['folderId'] = exercise['folderId']
      exEntry['entityId'] = exercise['id']
      exEntry['exDecision'] = " "
      for attr in exercise['attributes']:
        if attr['definitionId'] == this.env.attributeDict['name']:
          if attr['value'] is not None:
            exEntry['exTitle'] = attr['value']['value']
        if attr['definitionId'] == this.env.attributeDict['description']:
          if attr['value'] is not None:
            exEntry['exDescription'] = attr['value']['value']['plainText']
        if attr['definitionId'] == this.env.attributeDict['note:status']:
          if attr['value'] is not None:
            exEntry['exStatus'] = attr['value']['value']['value']
        if attr['definitionId'] == this.env.attributeDict['note:decision']:
          if attr['value'] is not None:
            exEntry['exDecision'] = attr['value']['value']['plainText']
            if len(exEntry['exDecision']) == 0:
              exEntry['exDecision'] = " "

      this.exList.append(exEntry['exTitle'])
      this.exDict[exEntry['exTitle']] = exEntry

    this.exList.sort()

  def Edit(this):

    this.title = Dropdown(
      options=this.exList,
      description='Title:',
      disabled=False
    )
    this.status = Dropdown(
      options=['Open', 'Closed'],
      description='Status:',
      disabled=False
    )
    this.decision = Textarea(
      description='Decision:',
      placeholder='Enter Decision...',
      disabled=False
    )
    this.save = Button(
      description='Save',
      tooltip='Click to Save status & decision.',
      button_style='success',
      disabled=False
    )
    this.save.on_click(this._on_save)
    this.result = widgets.Text(
      value='',
      placeholder='Save Result',
      description='',
      disabled=True)

    # setup output area
    this.output = widgets.Output(layout={'border': '1px solid black'})
    display(this.output)
    this._refresh_output()

  def _on_save(this, b):
    # update exercise response
    payload = {}
    attrList = [{},{}]
    payload['attributes'] = attrList
    payload['entityDefinitionId'] = this.exDict[this.title.value]['entityDefinitionId']
    payload['folderId'] = this.exDict[this.title.value]['folderId']

    attrList[0]['definitionId'] = this.env.attributeDict['note:status']
    attrList[0]['value'] = {}
    attrList[0]['value']['value'] = this.status.value
    attrList[0]['value']['dataType'] = "string"
    attrList[1]['definitionId'] = this.env.attributeDict['note:decision']
    attrList[1]['value'] = {}
    attrList[1]['value']['value'] = {}
    attrList[1]['value']['value']['plainText'] = this.decision.value
    attrList[1]['value']['dataType'] = "text"

    this.env._set_json_header()
    r = requests.put(this.env.url + 'projects/' +
                    this.env.projectDict[this.env.project.value] +
                    '/entities/' + this.exDict[this.title.value]['entityId'],
                    allow_redirects=False, headers=this.env.header,
                    json=payload)
    if r.status_code != 200:
      this.result.value("Failed to save Exercise update: " + str(r.status_code))
      return
    else:
      this.result.value = "Save Success!"
      # update local dictionary
      this.exDict[this.title.value]['exStatus'] = this.status.value
      this.exDict[this.title.value]['exDecision'] = this.decision.value

      this._refresh_output()

  def _refresh_output(this):

    # assemble exercise table
    exTable = []
    for ex in this.exList:
      exItem = []
      exItem.append(this.exDict[ex]['exTitle'])
      exItem.append(this.exDict[ex]['exDescription'])
      exItem.append(this.exDict[ex]['exStatus'])
      exItem.append(this.exDict[ex]['exDecision'])
      exTable.append(exItem)

    this.exDF = pd.DataFrame(exTable, columns = ['Title', 'Description', \
                                                  'Status', 'Decision'])
    with this.output:
      clear_output()

    # output the DF/DT plus edit form
    try:
      from google.colab import data_table
      data_table.enable_dataframe_formatter()
      this.exDT = data_table.DataTable(this.exDF, include_index=False)
      # Display dataframa via Colab datatable
      this.table = widgets.Output(layout={'border': '1px solid black'})
      with this.table:
        display(this.exDT)
    except ModuleNotFoundError:
      # Display basic dataframe
      this.table = widgets.Output(layout={'border': '1px solid black'})
      with this.table:
        display(this.exDF)
    finally:
      vbox_items = [this.table, this.title, this.status, \
                    this.decision, this.save, this.result]
      this.vbox = VBox(vbox_items)
      with this.output:
        display(this.vbox)