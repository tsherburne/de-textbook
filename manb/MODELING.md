# GENESYS Modeling Conventions

For usage of Mission Aware NoteBook ([MANB](https://pypi.org/project/manb/)) Package

## System Description

*  Use Case Diagrams
   *  Use Case Diagrams to include **Category** Name: *'SD: UC'*
   *  Optional display **hint** (l/r/u/d) for each Use Case **involves** Components
*  Use Case Table
   *  All Use Cases within Use Case Diagrams
*  Control Structure
   *  Components to include **Category** Name: *'SD: CS: Components'*
      *  Using **title** and **abbreviation**
   *  Functions to include **Category** Name: *'SD: CS: Functions'*
*  Control Action Table
   *  All Control Actions for Functions of Control Stucture
*  Message Sequence Diagrams
   *  All Use Cases within Use Case Diagrams - each Use Case is *categorized* - **Category** includes:
      *  Single *Fuction* being elaborated
      *  *Component* swimlanes - with left-to-right **order** (0..n) attribute
## Risk Assessment
*  Loss Table
   *  All Loss Entities
*  Hazard Table
   *  All Hazard Entities
*  Hazardous Action Table
   *  All Hazardous Action Entities
*  Control Action Analysis Table
   *  All Control Actions for Functions of Control Stucture

## Vulnerability Assessment

## Resilience Architecture
