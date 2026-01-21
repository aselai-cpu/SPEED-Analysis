# PlantUML Compatibility Notes

## Version Requirement
All diagrams in this directory are compatible with **PlantUML version 1.2017.15 or later**.

## Changes Made for Compatibility

### Removed Features
1. **`!theme plain`** - Theme directive may not be available in version 1.2017.15
2. **`skinparam linetype ortho`** - Orthogonal line type may have rendering issues in older versions

### Features Used (All Compatible)
- ✅ Class diagrams (`class` keyword)
- ✅ Packages (`package` keyword)
- ✅ Relationships with cardinality (`"1" --> "*"`)
- ✅ Notes (`note right of`, `note left of`, `note bottom of`)
- ✅ Stereotypes (`<<Entity>>`, `<<Node>>`)
- ✅ Visibility modifiers (`+` for public)
- ✅ Separators in class bodies (`--`)
- ✅ Rectangle elements
- ✅ Basic skinparam commands (`roundcorner`, `shadowing`)

## Diagram Files

1. **speed_entity_diagram.puml** - Entity Relationship Diagram using class diagram syntax
2. **speed_neo4j_graph_model.puml** - Neo4j graph database model
3. **speed_csv_to_neo4j_mapping.puml** - CSV to Neo4j mapping guide

All diagrams use standard PlantUML class diagram syntax that has been stable since early versions.

## Testing
To verify compatibility, you can test with:
```bash
java -jar plantuml.jar -version  # Check version
java -jar plantuml.jar design/*.puml  # Generate diagrams
```

## Notes
- If you encounter rendering issues, try removing `skinparam roundcorner` or `skinparam shadowing`
- All relationship syntax uses standard PlantUML arrows which are fully supported
- Package syntax is standard and compatible
