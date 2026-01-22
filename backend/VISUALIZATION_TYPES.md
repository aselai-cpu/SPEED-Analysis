# Visualization Types Reference

## Overview

The SPEED Knowledge Graph backend supports 8 visualization types that the Planning Agent can recommend based on the query. The Execution Agent prepares data in D3.js-ready formats for the frontend to render.

---

## Supported Visualization Types

### 1. Timeline ⏱️

**Type:** `timeline`

**Best For:**
- Events over time with intensity markers
- Temporal analysis of civil unrest
- Showing escalation patterns

**Data Structure:**
```json
{
  "type": "timeline",
  "title": "Syria Event Timeline 2011",
  "data": {
    "events": [
      {
        "date": "2011-01-01",
        "value": 12,
        "intensity": 3.5,
        "casualties": 45,
        "label": "2011-01"
      }
    ],
    "timeRange": {
      "start": "2011-01-01",
      "end": "2011-12-31"
    }
  }
}
```

**Example Queries:**
- "Show me the timeline of events in Syria 2011"
- "When did major instability episodes occur in Lebanon?"

---

### 2. Network Graph 🕸️

**Type:** `network_graph`

**Best For:**
- Actor-event relationships
- Event linkages and escalation chains
- Showing interactions between entities

**Data Structure:**
```json
{
  "type": "network_graph",
  "title": "Actor Interaction Network",
  "data": {
    "nodes": [
      {"id": "actor_1", "label": "Government", "type": "initiator", "size": 10},
      {"id": "actor_2", "label": "Protesters", "type": "target", "size": 8}
    ],
    "links": [
      {"source": "actor_1", "target": "actor_2", "value": 15}
    ]
  }
}
```

**Example Queries:**
- "Show me the actor network in Egyptian civil unrest"
- "Who were the main actors in Syrian events?"

---

### 3. Bar Chart 📊

**Type:** `bar_chart`

**Best For:**
- Comparing categories or metrics
- Driver distributions
- Event type comparisons
- Country-based statistics

**Data Structure:**
```json
{
  "type": "bar_chart",
  "title": "Event Distribution by Type",
  "data": {
    "categories": [
      {"category": "Anti-Government", "value": 145},
      {"category": "Socio-Cultural", "value": 89},
      {"category": "Economic", "value": 67}
    ]
  }
}
```

**Example Queries:**
- "What are the main drivers of civil unrest?"
- "Compare event types across countries"

---

### 4. Line Chart 📈

**Type:** `line_chart`

**Best For:**
- Trends over time
- Continuous temporal data
- Violence intensity trends

**Data Structure:**
```json
{
  "type": "line_chart",
  "title": "Violence Trend Over Time",
  "data": {
    "series": [
      {"x": 2011, "y": 234, "violence": 4.2},
      {"x": 2012, "y": 456, "violence": 5.8}
    ]
  }
}
```

**Example Queries:**
- "Show casualty trends in Syria from 2011-2015"
- "How did violence intensity change over time?"

---

### 5. Sankey Diagram 🌊 ✨ NEW

**Type:** `sankey_diagram`

**Best For:**
- Flow from one category to another
- Precursor events leading to major conflicts
- Driver to outcome flows
- Event type transitions

**Data Structure:**
```json
{
  "type": "sankey_diagram",
  "title": "Flow from Small Protests to Major Conflicts",
  "data": {
    "nodes": [
      {"id": 0, "name": "Small Protest"},
      {"id": 1, "name": "Large Demonstration"},
      {"id": 2, "name": "Violent Conflict"}
    ],
    "links": [
      {"source": 0, "target": 1, "value": 45},
      {"source": 1, "target": 2, "value": 23}
    ]
  }
}
```

**Example Queries:**
- "Find small protests that led to major conflicts"
- "Show the progression from symbolic acts to violence"
- "How do different drivers lead to different outcomes?"

**Handles:**
- `precursor_type` → `result_type` flows
- `driver` → `outcome` flows

---

### 6. Choropleth Map 🗺️ ✨ NEW

**Type:** `choropleth_map`

**Best For:**
- Geographic distribution of events
- Country or region-based intensity
- Spatial patterns

**Data Structure:**
```json
{
  "type": "choropleth_map",
  "title": "Event Intensity by Country",
  "data": {
    "regions": [
      {
        "location": "Syria",
        "value": 423,
        "casualties": 4567,
        "avg_intensity": 5.3
      },
      {
        "location": "Egypt",
        "value": 312,
        "casualties": 2341,
        "avg_intensity": 4.1
      }
    ]
  }
}
```

**Example Queries:**
- "Show me the geographic distribution of events in the Middle East"
- "Which countries had the most intense events in 2011?"
- "Map civil unrest across North Africa"

---

### 7. Heatmap 🔥 ✨ NEW

**Type:** `heatmap`

**Best For:**
- Intensity patterns by two dimensions (e.g., time x location)
- Event type x country matrices
- Temporal patterns (year x month)

**Data Structure:**
```json
{
  "type": "heatmap",
  "title": "Event Intensity: Time x Location",
  "data": {
    "cells": [
      {"x": 2011, "y": 1, "value": 23, "intensity": 3.5},
      {"x": 2011, "y": 2, "value": 45, "intensity": 4.2},
      {"x": 2011, "y": 3, "value": 67, "intensity": 5.8}
    ]
  }
}
```

**Example Queries:**
- "Show intensity patterns over time and location"
- "Create a heatmap of event types by country"
- "Visualize monthly event patterns across years"

**Handles:**
- `year` x `month` (temporal patterns)
- `country` x `event_type` (geographic patterns)
- `category1` x `category2` (generic matrix)

---

### 8. Force-Directed Graph 🎯 ✨ NEW

**Type:** `force_directed_graph`

**Best For:**
- Complex actor-event networks
- Multi-layered relationships
- Community detection
- Advanced network analysis

**Data Structure:**
```json
{
  "type": "force_directed_graph",
  "title": "Complex Actor-Event Network",
  "data": {
    "nodes": [
      {
        "id": "actor_123",
        "label": "Syrian Government",
        "type": "actor",
        "size": 15
      },
      {
        "id": "event_456",
        "label": "protest",
        "type": "event",
        "size": 8
      }
    ],
    "links": [
      {
        "source": "actor_123",
        "target": "event_456",
        "value": 5,
        "type": "initiated"
      }
    ]
  }
}
```

**Example Queries:**
- "Show the complex network of actors and events in Syria"
- "Visualize the full actor-event interaction network"
- "Map all relationships between initiators and targets"

**Handles:**
- Actor-event relationships (`actor_id` + `event_id`)
- Generic node-node networks (`source` + `target`)

---

## Implementation Details

### How Visualization Routing Works

1. **Planning Agent** analyzes query and recommends visualization types
2. **Execution Agent** receives the plan and routes to preparation methods:

```python
# In execution_agent.py
if viz_type == "timeline":
    return self._prepare_timeline(source_data, title)
elif viz_type == "sankey_diagram":
    return self._prepare_sankey(source_data, title)
# ... etc
```

3. **Preparation methods** transform Neo4j query results into D3-ready format
4. **Rendering Agent** includes visualizations in the final response
5. **Frontend** receives structured data and renders with D3.js

---

## Data Format Requirements

Each visualization type expects specific fields in the Neo4j query results:

### Timeline
- `year`, `month` (required)
- `event_count`, `avg_political_violence`, `total_casualties` (optional)

### Network Graph
- `initiator`, `target`, `initiator_id`, `target_id` (required)
- `interaction_count` (optional)

### Bar Chart
- Flexible: `anti_government`, `event_type`, `country`, etc.
- `event_count`, `value` (required for values)

### Line Chart
- `year` (required for x-axis)
- `event_count` (required for y-axis)
- `avg_political_violence` (optional)

### Sankey Diagram
- Option 1: `precursor_type`, `result_type`, `flow_count`
- Option 2: `driver`, `outcome`, `event_count`

### Choropleth Map
- `country` or `location` (required)
- `event_count` or `intensity` (required)
- `total_casualties`, `avg_political_violence` (optional)

### Heatmap
- Option 1: `year`, `month` (temporal)
- Option 2: `country`, `event_type` (geographic)
- Option 3: `category1`, `category2` (generic)
- `event_count` or `value` (required)

### Force-Directed Graph
- Option 1: `actor_id`, `event_id`, `actor_name`, `event_type`
- Option 2: `source`, `target`, `source_label`, `target_label`
- `interaction_count`, `strength`, `weight` (optional)

---

## Fallback Behavior

If a visualization type is unknown or data preparation fails:

1. **Logs warning** with the unknown type
2. **Falls back to bar_chart** (most versatile)
3. **Continues processing** instead of failing

```python
else:
    logger.warning(f"Unknown visualization type: {viz_type}")
    logger.warning(f"  Falling back to bar_chart for visualization")
    return self._prepare_bar_chart(source_data, title)
```

---

## Adding New Visualization Types

To add a new visualization type:

1. **Update routing** in `_prepare_visualization_data()`:
   ```python
   elif viz_type == "new_type":
       return self._prepare_new_type(source_data, title)
   ```

2. **Add preparation method**:
   ```python
   def _prepare_new_type(self, data: List[Dict], title: str) -> Dict:
       # Transform data
       return {
           "type": "new_type",
           "title": title,
           "data": {...}
       }
   ```

3. **Update Planning Agent** prompt in `planning_agent.py` to include the new type

4. **Implement frontend** D3.js component to render the visualization

---

## Testing

Test visualization preparation:

```python
# In your test file
from agents.execution_agent import ExecutionAgent
from services.neo4j_service import Neo4jService

agent = ExecutionAgent(neo4j_service)

# Mock data
data = [
    {"precursor_type": "protest", "result_type": "violence", "flow_count": 23}
]

# Test sankey preparation
result = agent._prepare_sankey(data, "Test Sankey")
assert result["type"] == "sankey_diagram"
assert len(result["data"]["nodes"]) == 2
assert len(result["data"]["links"]) == 1
```

---

## Performance Notes

- **Timeline**: Fast, handles 1000+ events efficiently
- **Network Graph**: Medium, best for 50-500 nodes
- **Bar Chart**: Very fast, handles any size
- **Line Chart**: Fast, handles 1000+ points
- **Sankey**: Medium, best for 20-100 flows
- **Choropleth**: Fast, limited by number of regions
- **Heatmap**: Medium, best for < 500 cells
- **Force-Directed**: Slow for > 1000 nodes, use with care

---

## Examples from Logs

### Success Case
```log
📈 Viz 1/2: sankey_diagram
  Title: Flow from Small Protests to Major Conflicts
  Data Source: precursor_events
  ✅ Prepared successfully
```

### Warning Case (No Data)
```log
📈 Viz 2/3: choropleth_map
  Title: Geographic Distribution
  Data Source: location_data
  ⚠️  No geographic data available for choropleth
  ⚠️  Failed to prepare visualization
```

### Fallback Case
```log
📈 Viz 3/3: unknown_type
  Title: Some Visualization
  ⚠️  Unknown visualization type: unknown_type
  ⚠️  Falling back to bar_chart for visualization
  ✅ Prepared successfully (as bar_chart)
```

---

## Summary

✅ **8 visualization types** supported
✅ **Flexible data handling** with multiple format options
✅ **Fallback mechanism** prevents failures
✅ **D3.js-ready** output format
✅ **Comprehensive logging** for debugging

All visualization types are production-ready and handle edge cases gracefully! 🎉
