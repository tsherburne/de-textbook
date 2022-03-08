# Mission Aware Note Book (manb)

## Description
* A Python package for Google Colab that supports [Mission Aware](https://mission-aware.net) concepts using the [GENESYS](https://www.vitechcorp.com/genesys_software/) REST API.

## Usage
```

# Notebook Initialization
import manb
env = manb.Environment(domain, path)
env.Tunnel()
env.Login()

# System Description
sd = manb.SystemDescription(env)
sd.UseCaseDiagram()
sd.UseCaseTable()
sd.ControlStructureDiagram()
sd.MSCDiagrams()

# Risk Assessment
ra = manb.RiskAssessment(env)
ra.LossTable()
ra.HazardTable()
ra.ControlActionTable()
ra.HazardousActionTable()
ra.ControlActionAnalysisTable()

# Vulnerability Assessment
va = manb.VulnerabilityAssesment(env)
va.LossScenarioTable()
va.PhysicalBlockDiagrams()
va.ComponentAnalysisTable()
va.LinkAnalysisTable()

# Resilience Architecture
arch = manb.ResilienceArchitecture(env)
arch.ResilientModeTable()
arch.LossScenarioElaborationTable()
arch.LossScenarioMSCDiagrams()
arch.ElictedRequirementsTable()

# Section Exercises
ex = manb.Exercises(env, manb.Section.<section enum>)
ex.Edit()
```