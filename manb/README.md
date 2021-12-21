# Mission Aware Note Book (manb)

## Description
* A Google Colab Notebook for [Mission Aware](https://mission-aware.net)
* Using the GENESYS REST API 

## Local Development Setup
```
export PYTHONPATH=/home/ubuntu/pypi/manb/src
```

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