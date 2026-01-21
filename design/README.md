# SPEED Dataset - Entity Relationship Diagrams

This directory contains PlantUML entity relationship diagrams for the SPEED (Social, Political and Economic Event Database) dataset, designed to support the creation of a Neo4j graph database ontology.

## Files

1. **speed_entity_diagram.puml** - Traditional ER diagram showing entities and relationships
2. **speed_neo4j_graph_model.puml** - Neo4j-oriented graph model showing nodes and relationships

## Overview

The SPEED dataset tracks **destabilizing events** globally from 1946 to the present, extracted from news reports. The entity model is designed to answer research questions about civil unrest, its causes, dynamics, and outcomes.

## Core Entities

### Event (Central Node)
The core entity representing a destabilizing event. Each event has:
- Unique identifier (`eventid`)
- Temporal information (year, month, day, Julian dates)
- Classification flags (coup, quasi-event, post-hoc reaction)
- Linkage information (can be linked to other events)

### Actor (Polymorphic Entity)
Represents participants in events. Can be:
- **Initiator** - Who started the event
- **Target** - Who/what was targeted
- **Victim** - Who/what was affected

Actors can be:
- **Group** - Insurgent, socio-cultural, or political groups
- **Individual** - Non-government or government individuals
- **GovernmentEntity** - Government agencies or entities at various levels

### Location
Geographic information including:
- Country and COW code
- Region
- Specific location (city, facility, etc.)
- Coordinates (latitude/longitude)
- Location type (densely populated, military facility, etc.)

### EventType
Classification of events:
- Event type (Political Expression, Political Attacks, Disruptive State Acts)
- Political expression subtypes
- Symbolic event types
- Attack types
- Disruptive state act types

### IntensityMetrics
Measures of event severity:
- Casualties (killed, injured)
- Number of participants
- Weapon types used
- Intensity scores (political violence, state violence, etc.)

### Drivers
Root causes and motivations:
- Socio-cultural animosities
- Anti-government sentiments
- Class-based conflict
- Ecological resource scarcities
- Political desires
- Personal security concerns

### Outcomes
Results and impacts:
- Property damage
- Arrests made
- Victim effects
- Country bias

### EventLink
Relationships between events:
- **Part of** - Event is part of a larger sequence
- **Stems from** - Event was caused by another event

## Mapping to Research Questions

### 1. Origins and Drivers of Civil Unrest
**Entities:** `Event`, `Drivers`
**Relationships:** `Event -[:DRIVEN_BY]-> Drivers`
**Query Pattern:**
```cypher
MATCH (e:Event)-[:DRIVEN_BY]->(d:Drivers)
WHERE d.anti_gov = true OR d.sc_animosity = true
RETURN e, d
```

### 2. Intensity and Disruptiveness
**Entities:** `Event`, `IntensityMetrics`
**Relationships:** `Event -[:HAS_INTENSITY]-> IntensityMetrics`
**Query Pattern:**
```cypher
MATCH (e:Event)-[:HAS_INTENSITY]->(im:IntensityMetrics)
WHERE im.n_killed > 10 OR im.pol_violence > threshold
RETURN e, im
ORDER BY im.pol_violence DESC
```

### 3. Dynamics and Outcomes
**Entities:** `Event`, `EventLink`, `Outcomes`
**Relationships:** 
- `Event -[:LINKED_TO]-> Event`
- `Event -[:RESULTS_IN]-> Outcomes`
**Query Pattern:**
```cypher
MATCH path = (e1:Event)-[:LINKED_TO*]->(e2:Event)
MATCH (e1)-[:RESULTS_IN]->(o:Outcomes)
RETURN path, o
```

### 4. Temporal Boundaries
**Entities:** `Event`, `TemporalInfo`
**Relationships:** `Event -[:HAS_TEMPORAL_INFO]-> TemporalInfo`
**Query Pattern:**
```cypher
MATCH (e:Event)-[:HAS_TEMPORAL_INFO]->(t:TemporalInfo)
WHERE t.start_date >= start AND t.end_date <= end
RETURN e, t
ORDER BY t.start_date
```

### 5. Precursor Events (Small-bore Events)
**Entities:** `Event`, `EventType`
**Relationships:** `Event -[:HAS_TYPE]-> EventType`
**Query Pattern:**
```cypher
MATCH (e:Event)-[:HAS_TYPE]->(et:EventType)
WHERE et.ev_type = 'Political Expression'
  AND et.pe_type IN ['Verbal', 'Symbolic Act']
RETURN e, et
```

### 6. Actors Involved
**Entities:** `Event`, `Actor`, `Group`, `Individual`, `GovernmentEntity`
**Relationships:**
- `Event -[:HAS_INITIATOR]-> Actor`
- `Event -[:HAS_TARGET]-> Actor`
- `Event -[:HAS_VICTIM]-> Actor`
**Query Pattern:**
```cypher
MATCH (e:Event)-[:HAS_INITIATOR]->(a:Actor)-[:IS_A]->(g:Group)
WHERE g.category = 'Political Group'
RETURN e, a, g
```

## Neo4j Implementation Notes

### Node Labels
- `Event` - Core event nodes
- `Location` - Geographic nodes
- `Actor` - Base actor nodes
- `Group`, `Individual`, `GovernmentEntity` - Actor subtypes
- `EventType`, `IntensityMetrics`, `Drivers`, `Outcomes` - Event characteristics
- `TemporalInfo`, `NewsSource` - Supporting information

### Relationship Types
- `OCCURRED_AT` - Event → Location
- `HAS_TYPE` - Event → EventType
- `HAS_INTENSITY` - Event → IntensityMetrics
- `DRIVEN_BY` - Event → Drivers
- `RESULTS_IN` - Event → Outcomes
- `HAS_INITIATOR` - Event → Actor
- `HAS_TARGET` - Event → Actor
- `HAS_VICTIM` - Event → Actor
- `LINKED_TO` - Event → Event
- `REACTS_TO` - Event → Event
- `IS_A` - Actor → Group/Individual/GovernmentEntity
- `CONTAINS` - Location → Location (hierarchical)

### Indexes Recommended
```cypher
CREATE INDEX event_eventid FOR (e:Event) ON (e.eventid);
CREATE INDEX event_year FOR (e:Event) ON (e.year);
CREATE INDEX location_country FOR (l:Location) ON (l.country);
CREATE INDEX actor_name FOR (a:Actor) ON (a.name);
```

## Usage

### Viewing the Diagrams

1. **Using PlantUML:**
   - Install PlantUML: `brew install plantuml` (macOS) or download from http://plantuml.com
   - Generate PNG: `plantuml speed_entity_diagram.puml`
   - Generate SVG: `plantuml -tsvg speed_entity_diagram.puml`

2. **Using Online Tools:**
   - Copy the `.puml` file content to http://www.plantuml.com/plantuml/uml/
   - Or use VS Code with PlantUML extension

3. **Using VS Code:**
   - Install "PlantUML" extension
   - Open `.puml` file
   - Press `Alt+D` to preview

## Next Steps

1. **Create Neo4j Schema:**
   - Use the graph model to create node and relationship constraints
   - Define property types and constraints

2. **Data Import:**
   - Transform CSV data to Neo4j import format
   - Create nodes first, then relationships
   - Use batch import for performance

3. **Query Development:**
   - Implement Cypher queries for each research question
   - Create indexes for common query patterns
   - Optimize for graph traversal performance

4. **Ontology Enhancement:**
   - Add domain-specific relationships
   - Create composite nodes for common patterns
   - Add temporal relationships for event sequences
