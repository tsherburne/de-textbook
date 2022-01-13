from .env import Environment, Section
import requests
from IPython.display import clear_output
from pprint import pprint
import pandas as pd
import ipywidgets as widgets
from ipywidgets import Layout, Button, Box, FloatText, Textarea
from ipywidgets import Dropdown, Label, IntSlider
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
    this.form_items ={}
    this.form = {}

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
    # setup exercise editor form
    form_item_layout = Layout(
        display='flex',
        flex_flow='row',
        justify_content='space-between'
    )
    this.title = Dropdown(options=this.exList)
    this.status = Dropdown(options=['Open', 'Closed'])
    this.decision = Textarea()
    this.save = Button(description='Save', button_style='success')
    this.save.on_click(this._on_save)

    this.form_items = [
        Box([Label(value='Title:'),
            this.title], layout=form_item_layout),
        Box([Label(value='Status:'),
            this.status], layout=form_item_layout),
        Box([Label(value='Decision:'),
            this.decision], layout=form_item_layout),
        Box([Label(value='Operation:'),
            this.save], layout=form_item_layout)
    ]
    this.form = Box(this.form_items, layout=Layout(
        display='flex',
        flex_flow='column',
        border='solid 2px',
        align_items='stretch',
        width='40%'
    ))

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

    # setup output area
    this.output = widgets.Output(layout={'border': '1px solid black'})
    display(this.output)

    with this.output:
      try:
        from google.colab import data_table
        data_table.enable_dataframe_formatter()
        this.exDT = data_table.DataTable(this.exDF, include_index=False)
        # Display dataframa via Colab datatable
        display(this.exDT, this.form)
      except ModuleNotFoundError:
        # Display basic dataframe
        display(this.exDF, this.form)

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
      print("Failed to save Exercise update: " + str(r.status_code))
      return
    else:
      print("Saved Exercise Response!")
