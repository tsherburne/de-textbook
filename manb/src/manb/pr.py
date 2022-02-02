import requests
from .env import Environment
from pprint import pprint
from IPython.display import clear_output

# Project db - schema definition & entities
class Project:
  def __init__(this, env: Environment):
    this.env = env

    # schema definition dictionaries name <-> uuid

    # fetch: entityType UUID
    #   n2IdEntityDict['<entityTypeName>']['id']
    # fetch: entity AttributeType UUID
    #   n2IdEntityDict['<entityTypeName>']['attrs']['<attributeTypeName>']['id']
    this.n2idEntityDict = {}

    # fetch: entityType Name
    #   id2nEntityDict['<entityTypeUUID']['name']
    # fetch: entity AttributeType Name
    #   id2nEntityDict['<entityTypeUUID']['attrs']['<attributeTypeUUID>']['name']
    this.id2nEntityDict = {}

    # same as above for relationships
    this.id2nRelDict = {}
    this.n2idRelDict = {}

    # entity data store

    # fetch: entity type
    #   entities[<entity uuid>]['type']
    # fetch: entity attribute value
    #   entities[<entity uuid>]['attrs'][<attr name>]
    # fetch: entity related targets list
    #   entities[<entity uuid>]['rels'][<rel name>]
    this.entities = {}

    # entity name -> uuid
    this.entitiesDict = {}

    # entity type list
    # fetch: list of entities by type
    #   entitesForTypeList[<entityTypeName>]
    this.entitiesForTypeList = {}

    # call structure for functions
    this.structures = {}

    return

  # fetch and save entities
  def FetchEntities(this, entityList: list):
    clear_output()
    print("Fetch Entities....")
    this.entities.clear()

    for entity in entityList:
      entityEntry = {}
      # fetch entity instances
      this.env._set_json_header()
      r = requests.get(this.env.url + 'projects/' +
                  this.env.projectDict[this.env.project.value] + '/entities/byclass/' +
                  this.n2idEntityDict[entity]['id'],
                  allow_redirects=False, headers=this.env.header)
      if r.status_code != 200:
        print("Failed to fetch entity: " + entity + ": " + str(r.status_code))
        return

      entityInstances = r.json()['results']

      # initialize entity list for entity Type
      this.entitiesForTypeList[entity] = []

      for entityInstance in entityInstances:
        entityEntry = {}
        entityId = entityInstance['id']
        entityEntry['type'] = this.id2nEntityDict[entityInstance['entityDefinitionId']]['name']

        # add entity to list by type
        this.entitiesForTypeList[entity].append(entityId)

        entityEntry['attrs'] = {}
        entityEntry['rels'] = {}
        for attr in entityInstance['attributes']:
          attrEntry = this._parse_attr_value(attr)

          # set attribute name
          entityEntry['attrs'][this.id2nEntityDict[entityInstance\
            ['entityDefinitionId']]['attrs'][attr['definitionId']]] = attrEntry


          if attr['definitionId'] == this.n2idEntityDict[entity]['attrs']['name']:
            # create entity name to uuid dictionary
            this.entitiesDict[attrEntry['value']] = entityId

        this.entities[entityId] = entityEntry

    # fetch relationship instances
    this.env._set_json_header()
    r = requests.get(this.env.url + 'projects/' +
                this.env.projectDict[this.env.project.value] +
                '/relationships',
                allow_redirects=False, headers=this.env.header)
    if r.status_code != 200:
      print("Failed to fetch relationships: " + str(r.status_code))
      return

    relationships = r.json()['results']
    for relationship in relationships:
      # check if both ends of relationship exist in project scope
      if (relationship['sourceEntityId'] in this.entities) and \
            (relationship['targetEntityId'] in this.entities):
        relName = this.id2nRelDict[relationship['relationDefinitionId']]['name']
        relRevName = this.id2nRelDict[relationship['relationDefinitionId']]['rev-name']

        attrs = {}

        # add relationship attributes
        if len(relationship['attributes']) > 0:
          for attr in relationship['attributes']:
            attrEntry = this._parse_attr_value(attr)

            # set attribute name
            attrs[this.id2nRelDict[relationship\
              ['relationDefinitionId']]['attrs'][attr['attributeDefinitionId']]] = attrEntry

        # add relationsip to source entity
        relEntry = {}
        relEntry['targetId'] = ""
        relEntry['attrs'] = attrs
        relEntry['targetId'] = relationship['targetEntityId']
        if relName not in this.entities[relationship['sourceEntityId']]['rels']:
          this.entities[relationship['sourceEntityId']]['rels'][relName] = []

        this.entities[relationship['sourceEntityId']]['rels'][relName].append(relEntry)

        # add reverse relationship to target entity
        relRevEntry = {}
        relRevEntry['targetId'] = ""
        relRevEntry['attrs'] = attrs
        relRevEntry['targetId'] = relationship['sourceEntityId']
        if relRevName not in this.entities[relationship['targetEntityId']]['rels']:
          this.entities[relationship['targetEntityId']]['rels'][relRevName] = []

        this.entities[relationship['targetEntityId']]['rels'][relRevName].append(relRevEntry)

    clear_output()
    print("Entites Fetch Complete!")
    return

  # fetch and save schema mapping - for name to/from uuid mapping
  def FetchSchema(this):
    clear_output()
    print("Fetch Schema Definition....")

    # fetch project schema
    this.env._set_json_header()
    r = requests.get(this.env.url + 'projects/' +
                this.env.projectDict[this.env.project.value] + '/schemas/',
                allow_redirects=False, headers=this.env.header)
    if r.status_code != 200:
      print("Failed to fetch schema: " + str(r.status_code))
      return
    schema = r.json()

    # build entity defition dictionaries
    for entityDefinition in schema['entityDefinitions']:
      entityNEntry = {}
      entityNEntry['id'] = entityDefinition['id']
      entityNEntry['attrs'] = {}
      this.n2idEntityDict[entityDefinition['name']] = entityNEntry

      entityIEntry = {}
      entityIEntry['name'] = entityDefinition['name']
      entityIEntry['attrs'] = {}
      this.id2nEntityDict[entityDefinition['id']] = entityIEntry

      for attrDefinition in entityDefinition['attributeDefinitions']:
        entityNEntry['attrs'][attrDefinition['name']] = attrDefinition['id']
        entityIEntry['attrs'][attrDefinition['id']] = attrDefinition['name']

    # build relations definition dictionary
    for relationshipDefinition in schema['relationshipDefinitions']:

      relationshipNEntry = {}
      relationshipNEntry['id'] = relationshipDefinition['relationDefinitionA']['id']
      relationshipNEntry['rev-id'] = relationshipDefinition['relationDefinitionB']['id']
      relationshipNEntry['attrs'] = {}
      this.n2idRelDict[relationshipDefinition['relationDefinitionA']['name']] = relationshipNEntry
      # add relationship attributes
      for attrDefinition in relationshipDefinition['attributeDefinitions']:
        relationshipNEntry['attrs'][attrDefinition['name']] = attrDefinition['id']

      relationshipNEntry = {}
      relationshipNEntry['id'] = relationshipDefinition['relationDefinitionB']['id']
      relationshipNEntry['rev-id'] = relationshipDefinition['relationDefinitionA']['id']
      relationshipNEntry['attrs'] = {}
      this.n2idRelDict[relationshipDefinition['relationDefinitionB']['name']] = relationshipNEntry
      # add relationship attributes
      for attrDefinition in relationshipDefinition['attributeDefinitions']:
        relationshipNEntry['attrs'][attrDefinition['name']] = attrDefinition['id']

      relationshipIEntry = {}
      relationshipIEntry['name'] = relationshipDefinition['relationDefinitionA']['name']
      relationshipIEntry['rev-name'] = relationshipDefinition['relationDefinitionB']['name']
      relationshipIEntry['attrs'] = {}
      this.id2nRelDict[relationshipDefinition['relationDefinitionA']['id']] = relationshipIEntry
      # add relationship attributes
      for attrDefinition in relationshipDefinition['attributeDefinitions']:
        relationshipIEntry['attrs'][attrDefinition['id']] = attrDefinition['name']

      relationshipIEntry = {}
      relationshipIEntry['name'] = relationshipDefinition['relationDefinitionB']['name']
      relationshipIEntry['rev-name'] = relationshipDefinition['relationDefinitionA']['name']
      relationshipIEntry['attrs'] = {}
      this.id2nRelDict[relationshipDefinition['relationDefinitionB']['id']] = relationshipIEntry
      # add relationship attributes
      for attrDefinition in relationshipDefinition['attributeDefinitions']:
        relationshipIEntry['attrs'][attrDefinition['id']] = attrDefinition['name']

    clear_output()
    print("Schema Definition Fetch Complete!")
    return

  # parse entity / relationship attribute value
  def _parse_attr_value(this, attr: dict) -> dict:

    attrEntry = {}

    # set attribute name
    if attr['value'] is not None:
      attrEntry['dataType'] = attr['value']['dataType']
    else:
      attrEntry['dataType'] = ""

    # retrieve attribute value
    if attrEntry['dataType'] == "text":
      attrEntry['value'] = attr['value']['value']['plainText']
    elif attrEntry['dataType'] == "string":
      attrEntry['value'] = attr['value']['value']
    elif attrEntry['dataType'] == "hierarchicalNumber":
      attrEntry['value'] = attr['value']['value']
    elif attrEntry['dataType'] == "integer":
      attrEntry['value'] = attr['value']['value']
    elif attrEntry['dataType'] == "enumeration":
      attrEntry['value'] = attr['value']['value']['value']
    else:
      attrEntry['value'] = ""

    return attrEntry

  def FetchStructure(this):
    clear_output()
    print("Fetch Structure Definition....")
    this.structures.clear()

    # retrieve structure for functions
    for entity in this.entitiesForTypeList['Function']:
      # fetch structure
      this.env._set_json_header()
      r = requests.get(this.env.url + 'projects/' +
                  this.env.projectDict[this.env.project.value] + '/structures/' +
                  entity, allow_redirects=False, headers=this.env.header)
      if r.status_code != 200:
        print("Failed to fetch structure: " + entity + ": " + str(r.status_code))
        return

      this.structures[entity] = r.json()

    clear_output()
    print("Structure Definition Fetch Complete!")
