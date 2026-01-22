# Logging Quick Reference

## Start Backend with Logging

```bash
cd backend
source venv/bin/activate
python main.py
```

---

## What You'll See

### 🚀 Query Received
```log
🚀 NEW QUERY RECEIVED
📝 User Query: Show me events in Syria 2011
```

### 🧠 Planning Phase
```log
🧠 PHASE 1: PLANNING AGENT
✅ Planning Complete
📊 Query Intent: Analyze events...
📈 Cypher Queries Planned: 2
📉 Visualizations Planned: 2
```

### ⚙️ Execution Phase
```log
⚙️  PHASE 2: EXECUTION AGENT
🔍 Query 1/2: event_chains
  ✅ Retrieved 85 records
📊 Visualizations Prepared: 2
```

### ✨ Rendering Phase
```log
✨ PHASE 3: RENDERING AGENT
📝 Text Analysis Generated: 3245 characters
📊 Final Visualizations: 2
```

### 🤖 Claude API Calls
```log
🤖 CLAUDE API REQUEST
Model: claude-sonnet-4-5-20250929
Input Tokens: 1245
Output Tokens: 387
```

### 🗄️ Neo4j Queries
```log
🗄️  NEO4J QUERY EXECUTION
Cypher Query: MATCH (e:Event)...
Records Returned: 85
```

---

## Filter Specific Logs

```bash
# Only Claude API interactions
python main.py 2>&1 | grep "CLAUDE"

# Only Neo4j queries
python main.py 2>&1 | grep "NEO4J"

# Only agent reasoning
python main.py 2>&1 | grep "Agent"

# Only errors
python main.py 2>&1 | grep "ERROR"

# Save to file
python main.py 2>&1 | tee backend.log
```

---

## Emoji Legend

| Emoji | Meaning |
|-------|---------|
| 🚀 | New query started |
| 🧠 | Planning phase |
| ⚙️ | Execution phase |
| ✨ | Rendering phase |
| 🤖 | Claude API |
| 🗄️ | Neo4j query |
| 📝 | Text content |
| 📊 | Data/stats |
| ✅ | Success |
| ⚠️ | Warning |
| ❌ | Error |
| ⏳ | In progress |
| 🎯 | Intent/goal |
| 🔍 | Search/query |
| 📈 | Visualization |

---

## Key Information Logged

### For Every Query:
- ✅ User's original question
- ✅ How it's interpreted (intent)
- ✅ What queries are planned
- ✅ What visualizations are planned
- ✅ Cypher queries executed
- ✅ Records retrieved
- ✅ Claude prompts sent
- ✅ Claude responses received
- ✅ Token usage (cost tracking)
- ✅ Final response details

---

## Troubleshooting

### No logs appearing?
Check log level in `main.py`:
```python
logging.basicConfig(level=logging.INFO)
```

### Too much noise?
Change to WARNING:
```python
logging.basicConfig(level=logging.WARNING)
```

### Want more detail?
Change to DEBUG:
```python
logging.basicConfig(level=logging.DEBUG)
```

---

## Cost Tracking

Monitor Claude API costs:
```log
Input Tokens: 1245    # ≈ $0.003
Output Tokens: 387    # ≈ $0.006
Total: ≈ $0.009 per call
```

---

## Full Documentation

- `LOGGING_GUIDE.md` - Complete guide
- `LOGGING_EXAMPLE.md` - Example output
- `LOGGING_SUMMARY.md` - What was added

---

## Quick Test

```bash
# Test query via API
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me events in Syria 2011"}'

# Watch logs in another terminal
tail -f backend.log
```

---

**That's it!** Start the backend and watch the complete agentic workflow unfold in the logs. 🎉
