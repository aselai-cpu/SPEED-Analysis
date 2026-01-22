# ✅ Comprehensive Logging Added to Backend

## What Was Added

Comprehensive logging has been added to the SPEED Knowledge Graph backend to provide full visibility into:

1. **Agentic Loop Reasoning** - How each agent (Planning, Execution, Rendering) makes decisions
2. **LLM Request/Response** - All interactions with Claude API including prompts, responses, and token usage
3. **Neo4j Query Execution** - All Cypher queries executed against the database with parameters and results

---

## Files Modified

### 1. `backend/main.py`
**Added:** Detailed workflow logging showing each phase of the agentic loop

**What You'll See:**
- 🚀 New query received notifications
- 🧠 Phase 1: Planning Agent status
- ⚙️ Phase 2: Execution Agent status
- ✨ Phase 3: Rendering Agent status
- Statistics for each phase (queries planned, records retrieved, visualizations created)
- Complete success/error reporting

**Example:**
```log
================================================================================
🚀 NEW QUERY RECEIVED
================================================================================
📝 User Query: Show me event escalation patterns in Syria during 2011
```

---

### 2. `backend/services/claude_service.py`
**Added:** Full Claude API request/response logging

**What You'll See:**
- 🤖 Claude API request details
- Model name and configuration (temperature, max tokens)
- Complete prompt sent to Claude (first 500 chars)
- Token usage (input tokens + output tokens)
- Response received (first 500 chars)
- API errors with context

**Example:**
```log
🤖 CLAUDE API REQUEST
Model: claude-sonnet-4-5-20250929
Input Tokens: 1245
Output Tokens: 387
Response Length: 1829 characters
```

**Benefits:**
- Monitor API costs (token usage visible)
- Debug prompt engineering
- Troubleshoot API errors
- Understand Claude's responses

---

### 3. `backend/services/neo4j_service.py`
**Added:** Complete Neo4j query execution logging

**What You'll See:**
- 🗄️ Cypher queries being executed
- Query parameters
- Number of records returned
- Sample data from first record
- Query execution errors

**Example:**
```log
🗄️  NEO4J QUERY EXECUTION
Cypher Query:
MATCH (e:Event)-[:OCCURRED_IN]->(loc:Location {country: $country})
WHERE e.year = $year
Parameters: {'country': 'Syria', 'year': 2011}
Records Returned: 85
```

**Benefits:**
- Debug Cypher queries
- Verify parameters are correct
- See what data is being retrieved
- Identify slow queries

---

### 4. `backend/agents/planning_agent.py`
**Added:** Planning agent reasoning process logging

**What You'll See:**
- 🎯 Query intent analysis
- 📚 Research questions identified
- 📊 Cypher queries to execute (with templates and parameters)
- 📈 Visualizations to create
- JSON parsing status
- Fallback plan activation (if needed)

**Example:**
```log
✅ Planning Agent Reasoning:
🎯 Intent Identified: Analyze event escalation patterns in Syria during 2011
📚 Research Questions: ['Q3: Dynamics and Outcomes']
📊 Execution Plan Details:
  • Cypher queries to execute: 2
    1. event_chains → event_escalation_chain
       Params: {'country': 'Syria', 'year': 2011}
```

**Benefits:**
- Understand how queries are interpreted
- Verify correct templates are selected
- Debug planning failures
- See agent's reasoning

---

### 5. `backend/agents/execution_agent.py`
**Added:** Execution agent processing logs

**What You'll See:**
- ⚙️ Query execution progress (Query 1/N, Query 2/N, etc.)
- 🔍 Each query's template and parameters
- ✅ Records retrieved per query
- 📊 Visualization preparation status
- 📈 Statistics calculation

**Example:**
```log
🔍 Query 1/2: event_chains
  Template: event_escalation_chain
  Parameters: {'country': 'Syria', 'year': 2011, 'limit': 30}
  ⏳ Executing Neo4j query...
  ✅ Retrieved 85 records

📈 Viz 1/2: timeline
  Title: Syria Event Timeline 2011
  Data Source: intensity_trend
  ✅ Prepared successfully
```

**Benefits:**
- Track query execution progress
- Verify data transformation
- Debug visualization preparation
- Identify slow queries

---

### 6. `backend/agents/rendering_agent.py`
**Added:** Rendering agent workflow logs

**What You'll See:**
- ✨ Rendering steps (text generation, viz formatting, response creation)
- 📝 Data summary building
- 🤖 Claude analysis request
- 📊 Visualization formatting
- 📦 Final response assembly

**Example:**
```log
✨ Rendering Agent: Generating final response...
📝 Step 1: Generating natural language analysis with Claude...
  ✅ Data summary prepared (847 chars)
  ✅ Claude analysis received (3245 chars)
📊 Step 2: Formatting visualizations for frontend...
  ✅ Formatted 2 visualizations
```

**Benefits:**
- Track rendering pipeline
- Monitor text generation
- Verify visualization formatting
- Debug response creation

---

## Log Format

### Emoji Legend

- 🚀 New query started
- 🧠 Planning phase
- ⚙️ Execution phase
- ✨ Rendering phase
- 🤖 Claude API interaction
- 🗄️ Neo4j query
- 📝 Text content
- 📊 Data/statistics
- ✅ Success
- ⚠️ Warning
- ❌ Error
- ⏳ In progress
- 🎯 Goal/intent
- 🔍 Search/query
- 📈 Visualization

### Log Levels

- **INFO** - Normal operation (all steps logged)
- **WARNING** - Non-critical issues (fallback plans, missing data)
- **ERROR** - Failures (API errors, query failures)

---

## How to Use

### View Logs in Development

```bash
cd backend
source venv/bin/activate
python main.py
```

Logs appear in console with emojis and formatting.

### View Logs in Production (Docker)

```bash
# Real-time logs
docker-compose -f docker-compose.webapp.yml logs -f backend

# Last 100 lines
docker-compose -f docker-compose.webapp.yml logs --tail=100 backend
```

### Save Logs to File

```bash
# Development
python main.py 2>&1 | tee backend.log

# Production
docker-compose logs -f backend >> backend.log
```

### Filter Logs

```bash
# Only Neo4j queries
python main.py 2>&1 | grep "NEO4J"

# Only Claude API calls
python main.py 2>&1 | grep "CLAUDE"

# Only agent reasoning
python main.py 2>&1 | grep -E "(Planning|Execution|Rendering) Agent"
```

---

## What You Can See Now

### ✅ Complete Query Lifecycle
- User query received
- Planning agent analyzes and creates plan
- Execution agent runs queries and prepares visualizations
- Rendering agent generates analysis
- Final response sent to frontend

### ✅ LLM Interactions
- Every prompt sent to Claude
- Every response received from Claude
- Token usage for cost tracking
- API errors with context

### ✅ Database Queries
- Every Cypher query executed
- Parameters used
- Records returned
- Sample data preview

### ✅ Agent Reasoning
- How each agent interprets the request
- What decisions it makes
- What templates/visualizations it selects
- Why it takes certain actions

### ✅ Performance Metrics
- Time spent in each phase
- Number of queries executed
- Records retrieved
- Token usage

### ✅ Error Tracking
- Where errors occur (which agent, which query)
- Full error context
- Stack traces for debugging

---

## Documentation Files Created

1. **`backend/LOGGING_GUIDE.md`** - Complete guide to the logging system
   - What gets logged
   - How to read logs
   - Filtering and searching
   - Best practices
   - Troubleshooting

2. **`backend/LOGGING_EXAMPLE.md`** - Real example of a complete query log
   - Shows actual log output
   - Demonstrates the full workflow
   - Annotated with explanations

3. **`LOGGING_SUMMARY.md`** (this file) - Overview of changes

---

## Benefits

### 🔍 **Debugging**
- Quickly identify where issues occur
- See exact queries and responses
- Track data flow through the system

### 📊 **Monitoring**
- Watch token usage and costs
- Track query performance
- Monitor system health

### 🎓 **Learning**
- Understand how agents reason
- See how queries are constructed
- Learn from Claude's responses

### 💰 **Cost Tracking**
- Token usage visible for every call
- Estimate API costs
- Optimize prompts to reduce costs

### 🚀 **Performance**
- Identify slow queries
- Track phase timings
- Optimize bottlenecks

---

## Example Query Flow

When you send: **"Show me event escalation patterns in Syria during 2011"**

You'll see:
1. Query received log with full text
2. Planning agent analyzes and creates plan (2 seconds)
   - Shows intent: "Analyze event escalation patterns..."
   - Shows 2 queries planned (event_chains, intensity_trend)
   - Shows 2 visualizations planned (timeline, network_graph)
3. Execution agent runs queries (3 seconds)
   - Query 1: event_escalation_chain → 85 records
   - Query 2: temporal_intensity_trend → 71 records
   - Prepares 2 visualizations
4. Rendering agent generates response (3 seconds)
   - Builds data summary (847 chars)
   - Requests Claude analysis
   - Receives 3,245 character response
   - Formats 2 visualizations
5. Complete response sent to frontend

**Total:** 8 seconds, 156 records, 3,758 tokens used (~$0.025 cost)

All steps visible in logs with emoji indicators and clear structure!

---

## Next Steps

1. **Start the backend** and watch the logs:
   ```bash
   cd backend
   python main.py
   ```

2. **Send a test query** from the frontend or with curl:
   ```bash
   curl -X POST http://localhost:8000/api/query \
     -H "Content-Type: application/json" \
     -d '{"query": "Show me events in Syria 2011"}'
   ```

3. **Watch the logs** show the complete agentic workflow

4. **Read the guides:**
   - `backend/LOGGING_GUIDE.md` - Full documentation
   - `backend/LOGGING_EXAMPLE.md` - Example output

---

## Summary

✅ **Comprehensive logging added** to all backend components
✅ **Full visibility** into agentic loop reasoning
✅ **Complete tracking** of LLM requests and responses
✅ **Detailed monitoring** of Neo4j query execution
✅ **Professional formatting** with emojis and structure
✅ **Documentation provided** with guides and examples

The system is now fully transparent, debuggable, and monitorable! 🎉
