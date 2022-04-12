# GENESYS Modeling Conventions

For usage of Mission Aware NoteBook ([MANB](https://pypi.org/project/manb/)) Package

## System Description

*  Use Case Diagrams
   *  Use Case Diagrams to include **Category** Name: *'SD: UC'*
   *  Components populate: **Title** and **Abbreviation**
   *  Optional display **hint** (l/r/u/d) for each Use Case **involves** Components
*  Use Case Table
   *  All Use Cases within Use Case Diagrams
*  Control Structure
   *  Components to include **Category** Name: *'SD: CS: Components'*
      *  Using **title** and **abbreviation**
   *  Functions to include **Category** Name: *'SD: CS: Functions'*
*  Control Action Table
   *  All Control Actions for Functions of Control Stucture
   *  Using **title**
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
*  Loss Scenario Table
*  Physical Block Diagram
   * Physical Blocks to include **Category** Name: *'PA: Block Diagrams'*
     * Each *categorized* Physical Block is a **Category** which includes:
       *  All Components - one component identified as 'context' via *'hint'*
       *  Components ordered in diagram by Hiearchical numbering
       *  All Links - each Link has *'hint'* (l/r/u/d) for *connected*
          components - hint is relative to Hierarchically ordered components *number*
*  Components - Loss Scenario Analysis Table
*  Links - Loss Scenario Analysis Table
   *  Links to include **Category** Name: *'PA: Links'*
   *  Link Decomposition (*connects to*) - must consistently populate 'hints' direction (l/r/u/d)
   *  Sub-Links ordered by Hiearchical number must consistently align with hints direction.

## Resilience Architecture
*  Physical Block Diagram
   *  See Vulnerability Assessment
*  Loss Scenario Message Sequence Diagrams
   *  All Loss Scenarios MSCs to include **Category** Name: *'RA: Loss Scenarios'*
   *  See MSC conventions in System Description