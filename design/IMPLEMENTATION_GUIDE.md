# SPEED Dataset - Neo4j Implementation Guide

## Overview

This guide provides a roadmap for implementing the SPEED dataset as a Neo4j graph database ontology based on the entity relationship diagrams in this directory.

## Diagram Files

1. **speed_entity_diagram.puml** - Traditional ER diagram showing all entities and their attributes
2. **speed_neo4j_graph_model.puml** - Neo4j-specific graph model with nodes and relationships
3. **speed_csv_to_neo4j_mapping.puml** - Data transformation mapping from CSV to Neo4j

## Key Design Decisions

### 1. Event-Centric Model
The `Event` node is the central entity. All other entities relate to events, supporting queries about:
- What happened (Event)
- Where (Location)
- Who (Actor)
- Why (Drivers)
- How severe (IntensityMetrics)
- What resulted (Outcomes)

### 2. Polymorphic Actor Model
Actors can be:
- **Role**: Initiator, Target, or Victim
- **Type**: Group, Individual, or Government Entity

This design allows flexible querying:
```cypher
// Find all events where a political group was the initiator
MATCH (e:Event)-[:HAS_INITIATOR]->(a:Actor)-[:IS_A]->(g:Group)
WHERE g.category = 'political'
RETURN e, a, g
```

### 3. Event Linking
Events can be linked to show:
- **Sequences**: Event A → Event B → Event C
- **Reactions**: Event B reacts to Event A (post-hoc)
- **Causation**: Event B stems from Event A

This supports questions about escalation and diffusion.

## Implementation Steps

### Step 1: Create Node Constraints
```cypher
// Create unique constraints
CREATE CONSTRAINT event_eventid FOR (e:Event) REQUIRE e.eventid IS UNIQUE;
CREATE CONSTRAINT location_location_id FOR (l:Location) REQUIRE l.location_id IS UNIQUE;
CREATE CONSTRAINT actor_actor_id FOR (a:Actor) REQUIRE a.actor_id IS UNIQUE;

// Create node existence constraints
CREATE CONSTRAINT event_requires_eventid FOR (e:Event) REQUIRE e.eventid IS NOT NULL;
```

### Step 2: Create Indexes
```cypher
// Performance indexes
CREATE INDEX event_year FOR (e:Event) ON (e.year);
CREATE INDEX event_country FOR (e:Event) ON (e.country);
CREATE INDEX location_country FOR (l:Location) ON (l.country);
CREATE INDEX location_region FOR (l:Location) ON (l.region);
CREATE INDEX actor_name FOR (a:Actor) ON (a.name);
CREATE INDEX group_category FOR (g:Group) ON (g.category);
```

### Step 3: Import Events
```cypher
// Load events from CSV
LOAD CSV WITH HEADERS FROM 'file:///resolved_data.csv' AS row
CREATE (e:Event {
  eventid: row.eventid,
  year: toInteger(row.year),
  month: toIntegerOrNull(row.month),
  day: toIntegerOrNull(row.day),
  event: toBoolean(row.event),
  posthoc: row.posthoc,
  coup: toBoolean(row.coup),
  coup_failed: toBoolean(row.coup_failed)
})
```

### Step 4: Import Locations
```cypher
// Create location nodes (deduplicated)
LOAD CSV WITH HEADERS FROM 'file:///resolved_data.csv' AS row
MERGE (l:Location {
  country: row.country,
  cowcode: toIntegerOrNull(row.cowcode)
})
ON CREATE SET
  l.region = row.region,
  l.latitude = toFloatOrNull(row.gp7),
  l.longitude = toFloatOrNull(row.gp8),
  l.loc_type = row.loc_type
```

### Step 5: Create Actor Nodes
```cypher
// Create actors from initiator information
LOAD CSV WITH HEADERS FROM 'file:///resolved_data.csv' AS row
WHERE row.ini_igrp1 IS NOT NULL AND row.ini_igrp1 <> '.'
MERGE (a:Actor {name: row.ini_igrp1})
ON CREATE SET
  a.actor_role = 'initiator',
  a.actor_type = 'group'
MERGE (g:Group {group_name: row.ini_igrp1, category: 'insurgent'})
MERGE (a)-[:IS_A]->(g)
```

### Step 6: Create Relationships
```cypher
// Link events to locations
MATCH (e:Event), (l:Location)
WHERE e.country = l.country
MERGE (e)-[:OCCURRED_AT]->(l)

// Link events to actors
MATCH (e:Event), (a:Actor)
WHERE a.actor_role = 'initiator' AND a.eventid = e.eventid
MERGE (e)-[:HAS_INITIATOR]->(a)

// Link events to each other
MATCH (e1:Event), (e2:Event)
WHERE e1.from_eid = e2.eventid
MERGE (e1)-[:LINKED_TO {link_type: e1.link_type}]->(e2)
```

## Query Patterns for Research Questions

### Q1: Origins and Drivers
```cypher
// What proportion of events are anti-government vs socio-cultural?
MATCH (e:Event)-[:DRIVEN_BY]->(d:Drivers)
RETURN 
  sum(CASE WHEN d.anti_gov_sentmnts THEN 1 ELSE 0 END) as anti_gov_count,
  sum(CASE WHEN d.sc_animosity THEN 1 ELSE 0 END) as socio_cultural_count,
  count(e) as total_events
```

### Q2: Event Intensity
```cypher
// Compare intensity of political violence vs political protest
MATCH (e:Event)-[:HAS_INTENSITY]->(im:IntensityMetrics)
WHERE e.year >= 2000
RETURN 
  e.year,
  avg(im.pol_viol) as avg_political_violence,
  avg(im.pol_express) as avg_political_expression
ORDER BY e.year
```

### Q3: Event Dynamics
```cypher
// Find event sequences (escalation patterns)
MATCH path = (e1:Event)-[:LINKED_TO*]->(e2:Event)
WHERE e1.year = 2010 AND e1.country = 'Syria'
RETURN path
ORDER BY length(path) DESC
LIMIT 10
```

### Q4: Temporal Boundaries
```cypher
// Define episode boundaries based on intensity
MATCH (e:Event)-[:HAS_TEMPORAL_INFO]->(t:TemporalInfo)
MATCH (e)-[:HAS_INTENSITY]->(im:IntensityMetrics)
WHERE e.country = 'Lebanon'
  AND im.pol_viol > 5.0
RETURN 
  min(t.start_date) as episode_start,
  max(t.end_date) as episode_end,
  count(e) as event_count
```

### Q5: Precursor Events
```cypher
// Find small-bore events that preceded major conflicts
MATCH (small:Event)-[:HAS_TYPE]->(et:EventType)
WHERE et.ev_type = 'Political Expression'
  AND et.pe_type IN ['Verbal', 'Symbolic Act']
MATCH (small)-[:LINKED_TO*1..5]->(major:Event)-[:HAS_INTENSITY]->(im:IntensityMetrics)
WHERE im.n_killed > 100
RETURN small, major, im
```

### Q6: Actors Involved
```cypher
// Which groups initiate events in a region?
MATCH (e:Event)-[:OCCURRED_AT]->(l:Location)
WHERE l.region = 'Middle East'
MATCH (e)-[:HAS_INITIATOR]->(a:Actor)-[:IS_A]->(g:Group)
RETURN g.group_name, g.category, count(e) as event_count
ORDER BY event_count DESC
```

## Data Quality Considerations

1. **Missing Values**: Many fields have NaN/null values. Decide whether to:
   - Skip relationship creation if data is missing
   - Create nodes with null properties
   - Use default values

2. **Deduplication**: 
   - Location nodes should be deduplicated by country/cowcode
   - Group nodes should be deduplicated by name
   - Actor nodes may need fuzzy matching for name variations

3. **Data Types**:
   - Convert string enums to appropriate types
   - Handle float-to-int conversions for enum lookups
   - Preserve original values for audit trail

## Performance Optimization

1. **Batch Processing**: Import in batches of 10,000-50,000 nodes
2. **Transaction Size**: Keep transactions under 50,000 operations
3. **Index Usage**: Ensure queries use indexes (check with PROFILE)
4. **Relationship Direction**: Consider directionality for traversal performance
5. **Composite Nodes**: Consider creating composite nodes for common patterns

## Next Steps

1. **Validate Model**: Review diagrams against actual data
2. **Create Import Scripts**: Write Python/Neo4j scripts for data transformation
3. **Test Queries**: Validate query patterns with sample data
4. **Optimize**: Profile and optimize slow queries
5. **Document**: Create query documentation for end users

## References

- Neo4j Cypher Manual: https://neo4j.com/docs/cypher-manual/
- Graph Data Modeling: https://neo4j.com/developer/modeling-guide/
- PlantUML Documentation: http://plantuml.com/
