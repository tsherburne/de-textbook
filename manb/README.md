# Mission Aware Note Book (manb)

## Description
* A Python package for Google Colab that supports [Mission Aware](https://mission-aware.net) concepts using the GENESYS REST API.

## Usage
```
import manb
env = manb.Environment(domain, path)
env.Tunnel()
env.Login()

cs = manb.ControlStructure(env)
cs.Diagram()
cs.ControlActionTable()

ra = manb.RiskAssessment(env, cs)
ra.LossTable()
ra.HazardTable()
ra.HazardousActionTable()
ra.ControlActionAnalysisTable()

ex = manb.Exercises(env, manb.Section.RISK_ASSESSMENT)
ex.Edit()
```