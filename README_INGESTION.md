# SPEED Temporal Knowledge Graph - Ingestion Guide

## Overview

This package ingests the SPEED (Social, Political and Economic Event Database) CSV data into Neo4j as a Temporal Knowledge Graph (TKG), enabling advanced querying and analysis of civil unrest events globally from 1946 to present.

## Prerequisites

1. **Docker** - for running Neo4j
2. **Python 3.10+**
3. **SPEED CSV data** - `output/resolved_data_20260121_152103.csv`

## Quick Start

### 1. Start Neo4j Container

```bash
docker-compose up -d
```

This will start Neo4j on:
- **Bolt**: `bolt://localhost:7687`
- **Browser**: `http://localhost:7474`
- **Credentials**: neo4j / speedkg123

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Ingestion

```bash
python ingest_speed_to_neo4j.py
```

Or with custom configuration:

```bash
python ingest_speed_to_neo4j.py --config config.yaml
```

### 4. Validate the Knowledge Graph

```bash
# Run validation checks only
python ingest_speed_to_neo4j.py --validate-only

# Or use the Jupyter notebook
jupyter notebook validate_speed_kg.ipynb
```

## Configuration

Edit `config.yaml` to customize:

```yaml
neo4j:
  uri: bolt://localhost:7687
  user: neo4j
  password: speedkg123

data:
  csv_path: output/resolved_data_20260121_152103.csv

ingestion:
  batch_size: 10000  # Nodes per transaction

logging:
  level: INFO
  file: logs/ingestion.log
```

## Command-Line Options

```bash
# Basic usage
python ingest_speed_to_neo4j.py

# Use custom config
python ingest_speed_to_neo4j.py --config my_config.yaml

# Override specific settings
python ingest_speed_to_neo4j.py --uri bolt://remote:7687 --password mypass

# Only run validation
python ingest_speed_to_neo4j.py --validate-only
```

## What Gets Ingested

### Node Types (9)

1. **Event** (Core) - 106 CSV columns mapped to event nodes
2. **Location** - Geographic information with spatial indexing
3. **Actor** - Polymorphic (Group/Individual/GovernmentEntity)
4. **EventType** - Classification of events
5. **IntensityMetrics** - Severity measurements
6. **Drivers** - Root causes and motivations
7. **Outcomes** - Results and impacts
8. **TemporalInfo** - TKG temporal metadata
9. **NewsSource** - Provenance tracking

### Relationship Types (14)

- `OCCURRED_AT` - Event → Location
- `HAS_TYPE` - Event → EventType
- `HAS_INTENSITY` - Event → IntensityMetrics
- `DRIVEN_BY` - Event → Drivers
- `RESULTS_IN` - Event → Outcomes
- `HAS_TEMPORAL_INFO` - Event → TemporalInfo
- `REPORTED_IN` - Event → NewsSource
- `HAS_INITIATOR` - Event → Actor
- `HAS_TARGET` - Event → Actor
- `HAS_VICTIM` - Event → Actor
- `LINKED_TO` - Event → Event (with temporal validity)
- `REACTS_TO` - Event → Event (post-hoc reactions)
- `CONTAINS` - Location → Location (hierarchy)
- `IS_A` - Actor type classification

## Temporal Knowledge Graph Features

The ingestion implements advanced TKG capabilities:

1. **Temporal Validity** - All events have `valid_from` and `valid_to` timestamps
2. **Point-in-Time Queries** - Query graph state at specific dates
3. **Temporal Ranges** - Find events within time windows
4. **Event Sequences** - Track escalation via `LINKED_TO` relationships
5. **Bitemporal Modeling** - Valid time vs. transaction time

### Example TKG Queries

```cypher
// Point-in-time query: Events active on 2010-01-15
MATCH (e:Event)
WHERE e.valid_from <= datetime('2010-01-15T00:00:00')
  AND (e.valid_to IS NULL OR e.valid_to >= datetime('2010-01-15T00:00:00'))
RETURN e

// Temporal range: All events in 2010
MATCH (e:Event)
WHERE e.valid_from >= datetime('2010-01-01T00:00:00')
  AND e.valid_from <= datetime('2010-12-31T23:59:59')
RETURN e

// Event escalation chains
MATCH path = (e1:Event)-[:LINKED_TO*1..5]->(e2:Event)
WHERE e1.country = 'Syria' AND e1.year = 2011
RETURN path
ORDER BY length(path) DESC
```

## Research Questions Supported

The knowledge graph enables answering all 6 SPEED research questions:

1. **Origins and Drivers** - What causes civil unrest?
2. **Intensity** - How severe are events?
3. **Dynamics** - How do events escalate?
4. **Temporal Boundaries** - When do episodes begin/end?
5. **Precursor Events** - Role of small-bore events?
6. **Actors** - Who participates in unrest?

See `validate_speed_kg.ipynb` for example queries.

## Performance

Expected ingestion time on standard hardware:
- **Small dataset** (< 10k rows): ~5 minutes
- **Medium dataset** (10k-100k rows): ~15-30 minutes
- **Full dataset** (100k+ rows): ~30-60 minutes

Performance optimizations included:
- Batch processing (10k nodes per transaction)
- Indexes created before data load
- MERGE for deduplication, CREATE for unique nodes
- Progress tracking with tqdm

## Validation

The script performs comprehensive validation:

### Graph Statistics
- Node counts by label
- Relationship counts by type
- Total graph size

### Data Quality Checks
- Events without locations
- Events without temporal info
- Actors without type labels
- Orphaned nodes

### Research Question Validation
- Tests all 6 research questions
- Verifies TKG temporal features
- Checks actor networks
- Geographic distribution

## Troubleshooting

### Connection Issues

```bash
# Check Neo4j is running
docker ps | grep neo4j

# View Neo4j logs
docker logs speedkg-neo4j

# Test connection
curl http://localhost:7474
```

### APOC Not Available

Some advanced queries require APOC. It's enabled in docker-compose.yml:

```yaml
NEO4J_PLUGINS: ["apoc"]
```

Restart container if needed:
```bash
docker-compose restart
```

### Memory Issues

If ingestion fails with memory errors, adjust Neo4j heap:

```yaml
# In docker-compose.yml
NEO4J_dbms_memory_heap_max__size: 4G  # Increase from 2G
```

### Slow Performance

1. Reduce batch size in config.yaml
2. Check indexes are created (run validation)
3. Monitor Neo4j browser query performance
4. Consider using `--validate-only` to check current state

## File Structure

```
.
├── ingest_speed_to_neo4j.py      # Main ingestion script
├── validate_speed_kg.ipynb        # Validation notebook
├── Prompt_Ingestion.txt           # Original prompt specification
├── config.yaml                    # Configuration
├── requirements.txt               # Python dependencies
├── docker-compose.yml             # Neo4j container config
├── output/
│   └── resolved_data_20260121_152103.csv  # SPEED data
├── design/                        # Ontology design files
│   ├── IMPLEMENTATION_GUIDE.md
│   ├── speed_csv_to_neo4j_mapping.puml
│   └── speed_neo4j_graph_model.puml
├── data/
│   └── Questions.txt              # Research questions
└── logs/
    └── ingestion.log              # Ingestion logs
```

## Next Steps

After successful ingestion:

1. **Explore the graph** in Neo4j Browser: http://localhost:7474
2. **Run validation notebook** to verify research questions
3. **Execute custom queries** for your analysis
4. **Build visualizations** using the temporal data
5. **Export results** for further analysis

## Support

For issues or questions:
- Check logs in `logs/ingestion.log`
- Review validation output
- Consult IMPLEMENTATION_GUIDE.md
- Examine the ontology diagrams in `/design`

## License

This ingestion script follows the SPEED dataset licensing terms.
