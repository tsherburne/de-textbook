import requests
import ipywidgets as widgets
import subprocess
from IPython.display import clear_output

class Environment:
  
  def __init__(this, domain: str, path: str):
    # REST API base URL
    this.domain = domain
    this.path = path
    this.url = domain + path

    # GENESYS API refresh token
    this.refresh_token = ""
    
    # REST API Header
    #  cf-access-token: -> tunnel token
    #  Authorization: -> GENESYS api token
    this.header = {'cf-access-token': "",
                  'Authorization': "",
                  'Accept': 'application/json',
                  'Content-Type': 'application/x-www-form-urlencoded'}
    # Login widget handles
    this.output = {}

    this.name = None
    this.pwd = None
    this.login = None
    this.status = None
    this.project = None
    
    # Authorized Projects
    this.projectList = []
    this.projectDict = {}

    # Initialize API dictionaries
    this._init_api_dict()

  # Authenticate the Cloudflare Tunnel 
  def Tunnel(this):

    clear_output()

    process = subprocess.Popen(['./cloudflared', 'access', 'login', this.domain], 
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              universal_newlines=True)

    while True:
      # stderr output is URL for authentication (if token not already cached)
      output = process.stderr.readline()
      print(output.strip())
      # Wait for cloudflared to complete
      return_code = process.poll()
      if return_code is not None:
        if return_code == 0:
          # Line 1: Successfully fetched your token:
          # Line 2: <token>
          count = 0
          for output in process.stdout.readlines():
            if output.strip() != "":
              count += 1
              if count == 2:
                this.header['cf-access-token'] = output.strip()
                clear_output()
                print("Tunnel Token Fetch Success!")
        else:
          print("Cloudflared Error Exit: " + str(return_code))
        break

  # Login to GENESYS
  def Login(this):
    
    this.name = widgets.Text(
      value='',
      placeholder='Enter username',
      description='User Name:',
      disabled=False)
    
    this.pwd = widgets.Password(
      value='',
      placeholder='Enter password',
      description='Password:',
      disabled=False)
    
    this.login = widgets.Button(
      description="Login", 
      tooltip="Enter User Name and Password - then click to Login.",
      button_style='success')

    this.status = widgets.Text(
      value='',
      placeholder='Login Status',
      description='',
      disabled=True)
    # Register Login button callback
    this.login.on_click(this._on_login)

    # setup output area
    this.output = widgets.Output(layout={'border': '1px solid black'})
    display(this.output)
    # display login widgets to output area
    with this.output:
      display(this.name, this.pwd, this.login, this.status)

  # Login button clicked
  def _on_login(this, b):

    # Authenticate name / password
    payload = {'grant_type': 'password', 
               'username': this.name.value, 
               'password': this.pwd.value}
    r = requests.post(this.url + 'token', data=payload, 
                      allow_redirects=False, headers=this.header)
    # clear name / password
    del payload
    this.name.value = ""
    this.pwd.value = ""

    if r.status_code != 200:
      this.header['Authorization'] = ""
      this.projectList = []
      this.projectDict = {}
      if this.project:
        this.project.options = []
      this.status.value = 'Login Failed: ' + str(r.status_code)
      return
    
    this.status.value = 'Login Success!'
    # save access token for future requests
    this.header['Authorization'] = 'bearer ' + r.json()['access_token']

    # get authorized projects for user
    r = requests.get(this.url + 'projects', allow_redirects=False, 
                      headers=this.header)
    if r.status_code != 200:
      this.projectList = []
      this.projectDict = {}
      if this.project is not None:
        this.project.options = []
      this.status.value = 'Project Request Failed: ' + str(r.status_code)
      return

    projects = r.json()['results']
    
    for proj in projects:
      this.projectList.append(proj['name'])
      this.projectDict[proj['name']] = proj['id']
    
    this.projectList.sort()
    firstProj = this.projectList[0]

    if this.project:
        this.project.options=this.projectList
        this.project.value=firstProj
    else:
      this.project = widgets.Select(
        options=this.projectList,
        value=firstProj,
        description='Project:',
        disabled=False)
      # diplay projects widget to output area
      with this.output:
        display(this.project)

  # GENESYS API name to GUID dictionaries
  def _init_api_dict(this):
    this.entityDict = {}
    this.entityDict['Category'] = '40f7201d-af5b-463b-a10e-65d5db180b96'
    this.entityDict['ControlAction'] = '44d0db15-c706-402b-9bf4-9b235d6e4fad'
    this.entityDict['Hazard'] = 'a05af43e-ac3c-41ec-b17f-b0d30fff9a75'
    this.entityDict['HazardousAction'] = 'dd2870d1-a9ab-4c26-a1cf-d3efda1248ef'
    this.entityDict['Loss'] = '13f1f878-b40c-4c7a-a4e0-e348e4278d9d'
    
    this.relationDict = {}
    this.relationDict['ma: leads to'] = '9ee3b2ea-eaa9-4a02-ae33-cc11bb682167'
    this.relationDict['ma: is caused by'] = 'e734cdba-7143-4b37-9478-5b62497543f3'
    this.relationDict['ma: variation of'] = '39a672b3-e1d1-4005-a4d4-6a6e45a847fa'
    this.relationDict['ma: has variation'] = '59e2ba52-0282-466c-8727-2e2835f741af'
    this.relationDict['categorizes'] = '059208ef-009a-47b8-ae18-d8d93b71ea68'
    this.relationDict['categorized by'] = 'c2138bd9-06db-4146-bef2-1bbdeb5b6732'
    this.relationDict['built from'] = '6a545e1a-9052-4299-84bb-74ca62d532ad'
    this.relationDict['built in'] = '262f160b-c3a0-4207-9ba0-89ca78de45bf'

    this.attributeDict = {}
    this.attributeDict['name'] = '743d424c-daae-4dc9-887c-a8c92b9f08a4'
    this.attributeDict['number'] = '8a676ae6-2e9c-4f15-a037-b38d623adc1c'
    this.attributeDict['description'] = '5d4a1782-8b0e-4b5d-b0f2-a0985f01c817'
    this.attributeDict['priority'] ='3f58efe8-90f1-4793-9573-9575d580cb31'
    this.attributeDict['variationType'] = 'a00302c6-3a7f-40e6-b382-88ab33cacca9'
    this.attributeDict['component:title'] ='e70c8e32-8ed9-4c69-93d1-ec873ae22e8a'
    this.attributeDict['ca:title'] ='2a855444-2ddb-42a1-a04f-625f120cec26'
    this.attributeDict['note:status'] = '5b268627-f078-464e-8a12-f13cd8eee5f2'
    this.attributeDict['note:decision'] = 'd66bbaec-817e-469e-a3b3-354b6e9a2a08'
    
    this.sortBlockDict = {}
    this.sortBlockDict['Numeric'] = '78b85fc0-3aec-442d-95b9-2b291bd4d1bc' 

    this.hcaTypes = ['Providing', 'NotProviding', 'TooEarlyTooLate']
