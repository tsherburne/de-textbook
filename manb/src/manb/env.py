import requests
import ipywidgets as widgets
from ipywidgets import VBox
import subprocess
from IPython.display import clear_output, display
import urllib.request
import os
from enum import Enum
from .log import MANBLogHandler
import logging
import json
from pprint import pprint

# https://github.com/mwouts/itables
from itables import init_notebook_mode
import itables.options as opt

class Section(Enum):
  RISK_ASSESSMENT = 1
  VULNERABILITY_ASSESSMENT = 2

class Environment:

  def __init__(this, domain: str, path: str,
                    plantuml: str = "http://www.plantuml.com/plantuml/img/"):

    # diagram colors
    this.ReqColor = "#FC9494"
    this.PhyColor = "#56C0FB"
    this.FuncColor = "#C2FFBF"
    this.IntfColor = "#FFFF09"
    this.MAColor = "#FFE6CC"

    clear_output()
    # REST API base URL
    this.domain = domain
    this.path = path
    this.url = domain + path

    # PlantUML Server
    this.plantuml = plantuml

    # GENESYS API refresh token
    this.refresh_token = ""

    # API content types
    this.content_form = 'application/x-www-form-urlencoded'
    this.content_json = 'application/json'
    # REST API Header
    #  cf-access-token: -> tunnel token
    #  Authorization: -> GENESYS api token
    this.header = {'cf-access-token': "",
                  'Authorization': "",
                  'Accept': 'application/json',
                  'Content-Type': ""}

    # Initialize iTables
    init_notebook_mode(all_interactive=True)
    opt.columnDefs = [{"className": "dt-left", "targets": "_all"}]
    opt.classes = ["display", "compact"]

    # Login widget handles
    this.output = {}

    this.name = {}
    this.pwd = {}
    this.login = {}
    this.status = {}
    this.project = {}
    this.vbox = {}
    this.vboxitems = []

    # Authorized Projects
    this.projectList = []
    this.projectDict = {}

    # Setup MANB Logger
    this.logger = logging.getLogger(__name__)
    this.loghandler = MANBLogHandler()
    this.loghandler.setFormatter(logging.Formatter(\
                '%(asctime)s - [%(levelname)s] %(message)s'))
    this.logger.addHandler(this.loghandler)
    this.logger.setLevel(logging.ERROR)

    # Create temporary directory for plantuml output
    if not os.path.exists('./diagrams'):
      os.makedirs('./diagrams')

    # Create temporary directory for local project storage
    if not os.path.exists('./projects'):
      os.makedirs('./projects')

    # form to select local / remote repository
    this.repository = widgets.ToggleButtons(
      options=['Local', 'Remote'],
      value='Local',
      description='Repository:',
      disabled=False,
      #button_style='info',
      tooltips=['Read-Only via Github JSON File',
                'Read-Write via GENESYS REST-API'],
      icons=['file','database']
    )
    # setup output area
    this.output = widgets.Output(layout={'border': '1px solid black'})
    display(this.output)
    # display project selection widgets to output area
    with this.output:
      display(this.repository)

    return

  # Authenticate the Cloudflare Tunnel
  def Tunnel(this):

    clear_output()
    if this.repository.value == 'Local':
      print("Tunnel authentication not required for local repository.")
    else:
      # Download cloudflared CLI
      print("Downloading Tunnel Client...")
      this._get_cloudflared()

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
                clear_output()
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

    this.project = widgets.Select(
      options=[''],
      value='',
      description='Project:',
      disabled=False)

    if this.repository.value == 'Local':
      # no login for local repository
      this.vbox_items = [this.project]

      # retrieve local project list
      if not os.path.exists('./projects/projects.json'):
        url = 'https://raw.githubusercontent.com/tsherburne/de-textbook/' \
              'main/projects/projects.json'
        urllib.request.urlretrieve(url, './projects/projects.json')

      with open('./projects/projects.json') as f:
        projects = json.load(f)

      # build project list and dict
      this.projectList = []
      this.projDict = {}
      for proj in projects:
        this.projectList.append(proj['name'])
        this.projectDict[proj['name']] = proj['path']

      this.projectList.sort()

      this.project.options = this.projectList
      this.project.value = this.projectList[0]

    else:
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
        description='Login',
        tooltip='Enter User Name and Password - then click to Login.',
        icon='sign-in'
      )

      this.status = widgets.Text(
        value='',
        placeholder='Login Status',
        description='',
        disabled=True)
      # Register Login button callback
      this.login.on_click(this._on_login)
      this.vbox_items = [this.name, this.pwd, this.login, this.status, this.project]

    this.vbox = VBox(this.vbox_items)
    # setup output area
    this.output = widgets.Output(layout={'border': '1px solid black'})
    display(this.output)
    # display login widgets to output area
    with this.output:
      display(this.vbox)

  # Login button clicked
  def _on_login(this, b):

    # Authenticate name / password
    payload = {'grant_type': 'password',
               'username': this.name.value,
               'password': this.pwd.value}

    this._set_form_header()
    r = requests.post(this.url + 'token', data=payload,
                      allow_redirects=False, headers=this.header)
    # clear password
    del payload
    this.pwd.value = ""

    # clear project list
    this.projectList = []
    this.projectDict = {}
    this.project.options = ['']
    this.project.value = ''

    if r.status_code != 200:
      this.header['Authorization'] = ""
      this.status.value = 'Login Failed: ' + str(r.status_code)
      return

    this.status.value = 'Login Success!'
    # save access token for future requests
    this.header['Authorization'] = 'bearer ' + r.json()['access_token']

    # get authorized projects for user
    r = requests.get(this.url + 'projects', allow_redirects=False,
                      headers=this.header)
    if r.status_code != 200:
      this.status.value = 'Project Request Failed: ' + str(r.status_code)
      return

    projects = r.json()['results']

    # build project list and dict
    for proj in projects:
      this.projectList.append(proj['name'])
      this.projectDict[proj['name']] = proj['id']

    this.projectList.sort()

    this.project.options = this.projectList
    this.project.value = this.projectList[0]

  # Set REST header for json content
  def _set_json_header(this):
    this.header['Content-Type'] = this.content_json
  # Set REST header for form content
  def _set_form_header(this):
    this.header['Content-Type'] = this.content_form

  # Download Cloudflared CLI
  def _get_cloudflared(this):
    url = 'https://github.com/cloudflare/cloudflared/releases/' \
          'latest/download/cloudflared-linux-amd64'
    urllib.request.urlretrieve(url, 'cloudflared')
    ret = os.chmod('./cloudflared', 0o775)

