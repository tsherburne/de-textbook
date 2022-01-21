from .env import Environment
from .ra import RiskAssessment
import requests
from IPython.display import clear_output
import sys
from pprint import pprint
import pandas as pd
import ipywidgets as widgets

class VulnerabilityAssessment:
  def __init__(this, env: Environment, ra: RiskAssessment):
    this.env = env
    this.ra = ra
    print("Initializing Vulnerability Assessment")


  def LossScenarioTable(this):
    print("Loss Table")


