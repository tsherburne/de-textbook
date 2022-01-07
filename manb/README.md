# Mission Aware Note Book (manb)

## Description
* A Google Colab Notebook for [Mission Aware](https://mission-aware.net) using the GENESYS REST API

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
ra.LossEdit()

ex = manb.Exercises(env, manb.SECTION)
ex.Edit()
```