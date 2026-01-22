# Backend Logging Guide

## Overview

The SPEED Knowledge Graph backend now includes comprehensive logging that shows:
1. **Agentic Loop Reasoning** - The decision-making process of each agent
2. **LLM Requests/Responses** - All interactions with Claude API
3. **Neo4j Query Execution** - Cypher queries and their results

This logging is invaluable for debugging, monitoring, and understanding how the system processes queries.

---

## What Gets Logged

### 🚀 Main Workflow (main.py)

When a query is received, the logs show:

```
================================================================================
🚀 NEW QUERY RECEIVED
================================================================================
📝 User Query: Show me event escalation patterns in Syria during 2011
--------------------------------------------------------------------------------
```

Each phase is clearly marked:

#### Phase 1: Planning Agent
```
🧠 PHASE 1: PLANNING AGENT
================================================================================
Analyzing query intent and creating execution plan...
✅ Planning Complete
📊 Query Intent: Analyze event escalation patterns in Syria during 2011
🔍 Research Questions: Q3: Dynamics and Outcomes
📈 Cypher Queries Planned: 2
📉 Visualizations Planned: 2
  Query 1: event_chains using template 'event_escalation_chain'
  Query 2: intensity_trend using template 'temporal_intensity_trend'
  Viz 1: timeline - Syria Event Timeline 2011
  Viz 2: network_graph - Event Linkage Network
```

#### Phase 2: Execution Agent
```
⚙️  PHASE 2: EXECUTION AGENT
================================================================================
Executing Cypher queries against Neo4j...
✅ Execution Complete
📦 Total Records Retrieved: 156
🔢 Queries Executed: 2
  event_chains: 85 records
  intensity_trend: 71 records
📊 Visualizations Prepared: 2
```

#### Phase 3: Rendering Agent
```
✨ PHASE 3: RENDERING AGENT
================================================================================
Generating natural language analysis with Claude...
✅ Rendering Complete
📝 Text Analysis Generated: 3245 characters
📊 Final Visualizations: 2
🎯 Data Points: 156
```

---

### 🤖 Claude API Interactions (claude_service.py)

Every Claude API call is logged with full details:

```
🤖 CLAUDE API REQUEST
------------------------------------------------------------
Model: claude-sonnet-4-5-20250929
Max Tokens: 2000
Temperature: 0.3
User Prompt:
You are a SPEED Knowledge Graph query planning agent...
[First 500 characters of prompt shown]
------------------------------------------------------------
⏳ Sending request to Claude API...
✅ CLAUDE API RESPONSE
------------------------------------------------------------
Input Tokens: 1245
Output Tokens: 387
Response Length: 1829 characters
Response Preview:
{
  "query_intent": "Analyze event escalation patterns...",
  "research_questions": ["Q3"],
  ...
}
[First 500 characters of response shown]
------------------------------------------------------------
```

This shows:
- Exact model being used
- Token configuration
- The prompt sent to Claude (preview)
- Token usage (input + output)
- The response received (preview)

---

### 🗄️ Neo4j Query Execution (neo4j_service.py)

Every Cypher query is logged:

```
🗄️  NEO4J QUERY EXECUTION
------------------------------------------------------------
Cypher Query:
MATCH (e:Event)-[:OCCURRED_IN]->(loc:Location {country: $country})
WHERE e.year = $year
MATCH (e)-[:LINKED_TO]->(next:Event)
RETURN e, next
LIMIT $limit
Parameters: {'country': 'Syria', 'year': 2011, 'limit': 30}
------------------------------------------------------------
⏳ Executing query against Neo4j...
✅ NEO4J QUERY RESULT
------------------------------------------------------------
Records Returned: 85
Sample Record Keys: ['e', 'next', 'linkage_type', 'casualties']
  e: {id: 12345, event_type: 'protest', ...}
  next: {id: 12346, event_type: 'violence', ...}
  linkage_type: escalation
  ... and 1 more fields
------------------------------------------------------------
```

This shows:
- The exact Cypher query
- Parameters passed
- Number of records returned
- Sample data from the first record

---

### 🎯 Planning Agent Reasoning (agents/planning_agent.py)

Shows how the Planning Agent analyzes the query:

```
🎯 Sending planning request to Claude...
📋 Processing Claude's planning response...
  Removed JSON markdown wrapper
  Parsing JSON execution plan...
✅ Planning Agent Reasoning:
------------------------------------------------------------
🎯 Intent Identified: Analyze event escalation patterns in Syria during 2011
📚 Research Questions: ['Q3']

📊 Execution Plan Details:
  • Cypher queries to execute: 2
    1. event_chains → event_escalation_chain
       Params: {'country': 'Syria', 'year': 2011, 'limit': 30}
    2. intensity_trend → temporal_intensity_trend
       Params: {'country': 'Syria', 'start_year': 2011, 'end_year': 2011}

  • Visualizations to create: 2
    1. timeline - Syria Event Timeline 2011
       Data from: intensity_trend
    2. network_graph - Event Linkage Network
       Data from: event_chains

  • Text sections to include: ['summary', 'temporal_analysis', 'escalation_patterns']
------------------------------------------------------------
```

---

### ⚙️ Execution Agent Processing (agents/execution_agent.py)

Shows step-by-step query execution:

```
⚙️  Execution Agent: Processing execution plan...
------------------------------------------------------------
📊 Total queries to execute: 2

🔍 Query 1/2: event_chains
  Template: event_escalation_chain
  Parameters: {'country': 'Syria', 'year': 2011, 'limit': 30}
  ⏳ Executing Neo4j query...
  ✅ Retrieved 85 records

🔍 Query 2/2: intensity_trend
  Template: temporal_intensity_trend
  Parameters: {'country': 'Syria', 'start_year': 2011, 'end_year': 2011}
  ⏳ Executing Neo4j query...
  ✅ Retrieved 71 records

------------------------------------------------------------
📊 Preparing visualization data...
  Visualizations to prepare: 2

  📈 Viz 1/2: timeline
    Title: Syria Event Timeline 2011
    Data Source: intensity_trend
    ✅ Prepared successfully

  📈 Viz 2/2: network_graph
    Title: Event Linkage Network
    Data Source: event_chains
    ✅ Prepared successfully

------------------------------------------------------------
📊 Calculating statistics...
✅ Execution Agent Complete:
  • Total records: 156
  • Queries executed: 2
  • Visualizations prepared: 2
------------------------------------------------------------
```

---

### ✨ Rendering Agent Processing (agents/rendering_agent.py)

Shows the final response generation:

```
✨ Rendering Agent: Generating final response...
------------------------------------------------------------
📝 Step 1: Generating natural language analysis with Claude...
  📊 Building data summary for Claude...
  ✅ Data summary prepared (847 chars)
  🤖 Preparing analysis prompt for Claude...
  ⏳ Sending analysis request to Claude...
  ✅ Claude analysis received (3245 chars)
  ✅ Text analysis generated: 3245 characters

📊 Step 2: Formatting visualizations for frontend...
  ✅ Formatted 2 visualizations:
    1. timeline - Syria Event Timeline 2011
    2. network_graph - Event Linkage Network

📦 Step 3: Creating response object...

✅ Rendering Agent Complete:
  • Message ID: abc123-def456
  • Response Type: analysis
  • Text Length: 3245 chars
  • Visualizations: 2
  • Data Points: 156
------------------------------------------------------------
```

---

## Running with Logs

### Development Mode

```bash
cd backend
source venv/bin/activate
python main.py
```

Logs will appear in the console with colors and formatting.

### Production Mode with Docker

```bash
# View logs in real-time
docker-compose -f docker-compose.webapp.yml logs -f backend

# View last 100 lines
docker-compose -f docker-compose.webapp.yml logs --tail=100 backend
```

---

## Log Levels

The application uses Python's standard logging levels:

- **INFO** - Normal operation (all agent steps, queries, etc.)
- **WARNING** - Recoverable issues (fallback plans, missing templates)
- **ERROR** - Errors that prevent processing

### Changing Log Level

Edit `backend/main.py`:

```python
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more details
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

Available levels:
- `logging.DEBUG` - Most verbose
- `logging.INFO` - Standard (recommended)
- `logging.WARNING` - Only warnings and errors
- `logging.ERROR` - Only errors

---

## Filtering Logs

### By Component

```bash
# Only Neo4j queries
python main.py 2>&1 | grep "NEO4J"

# Only Claude API calls
python main.py 2>&1 | grep "CLAUDE"

# Only agent reasoning
python main.py 2>&1 | grep -E "(Planning Agent|Execution Agent|Rendering Agent)"
```

### By Query

```bash
# Watch logs for a specific query
python main.py 2>&1 | grep -A 50 "User Query: Show me"
```

---

## Saving Logs to File

### Development

```bash
# Save all logs
python main.py > backend.log 2>&1

# Save and view simultaneously
python main.py 2>&1 | tee backend.log
```

### Production (Docker)

```bash
# Continuous logging to file
docker-compose -f docker-compose.webapp.yml logs -f backend >> backend.log
```

---

## Understanding Token Usage

Claude API token usage is logged for every call:

```
Input Tokens: 1245   # Tokens in your prompt
Output Tokens: 387   # Tokens in Claude's response
```

**Cost Calculation:**
- Claude Sonnet 4.5: ~$3 per million input tokens, ~$15 per million output tokens
- Example above: (1245 × $0.000003) + (387 × $0.000015) ≈ $0.0096

Monitor these to estimate API costs.

---

## Troubleshooting with Logs

### Query Not Working?

Look for:
1. **Planning errors** - Check if Claude understood the query
2. **Template not found** - Check if query templates exist
3. **Neo4j errors** - Check if database is connected
4. **Zero records** - Check if data exists in Neo4j

### Slow Responses?

Check timing:
1. Planning usually takes 1-2 seconds
2. Execution depends on query complexity (1-5 seconds)
3. Rendering usually takes 2-3 seconds

If any phase is taking >10 seconds, investigate.

### Claude API Errors?

Look for:
```
❌ CLAUDE API ERROR
Error: Invalid API key
```

Common issues:
- Missing or invalid `ANTHROPIC_API_KEY` in `.env`
- Rate limits exceeded
- Network connectivity

---

## Advanced: Custom Logging

### Add Your Own Logs

```python
import logging
logger = logging.getLogger(__name__)

# In your code
logger.info("Custom info message")
logger.warning("Something unexpected")
logger.error("An error occurred")
```

### Add Timestamps

Logs already include timestamps by default:
```
2025-01-22 14:30:45 - __main__ - INFO - Processing query...
```

### Log to File AND Console

Edit `main.py`:

```python
import logging
from logging.handlers import RotatingFileHandler

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# File handler (rotates at 10MB)
file_handler = RotatingFileHandler(
    'backend.log',
    maxBytes=10*1024*1024,
    backupCount=5
)
file_handler.setLevel(logging.INFO)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[console_handler, file_handler]
)
```

---

## Log Format Reference

### Emoji Legend

- 🚀 New query started
- 🧠 Planning phase
- ⚙️ Execution phase
- ✨ Rendering phase
- 🤖 Claude API interaction
- 🗄️ Neo4j query
- 📝 Text content
- 📊 Visualization/data
- ✅ Success
- ⚠️ Warning
- ❌ Error
- ⏳ In progress
- 🎯 Goal/intent
- 🔍 Search/query
- 📈 Chart/graph
- 🔢 Numbers/stats

### Separator Legend

- `=` (80 chars) - Major section separator
- `-` (60 chars) - Minor section separator

---

## Example Complete Log

See `examples/sample_query_log.txt` for a complete log of a full query cycle.

---

## Best Practices

1. **Keep logs enabled** in development for debugging
2. **Monitor token usage** to control API costs
3. **Archive logs** periodically (they can get large)
4. **Check logs** if queries fail or return unexpected results
5. **Use log filtering** to focus on specific issues

---

## Summary

The comprehensive logging system provides full visibility into:
- ✅ How agents reason and make decisions
- ✅ Exact prompts sent to Claude and responses received
- ✅ All Cypher queries executed against Neo4j
- ✅ Data transformations and visualizations prepared
- ✅ Token usage and API costs
- ✅ Errors and warnings with context

This makes the system transparent, debuggable, and auditable.

Happy debugging! 🐛🔍
