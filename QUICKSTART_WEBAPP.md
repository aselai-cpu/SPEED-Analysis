# Quick Start Guide - SPEED Knowledge Graph Web App

Get the AI-powered SPEED Knowledge Graph query interface running in 5 minutes.

## Prerequisites Checklist

- [ ] Docker installed and running
- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed
- [ ] Claude API key from Anthropic
- [ ] SPEED data ingested into Neo4j (see README_INGESTION.md)

## Step-by-Step Setup

### Step 1: Start Neo4j (if not already running)

```bash
# From project root
docker-compose up -d

# Verify Neo4j is running
curl http://localhost:7474
```

### Step 2: Setup Backend

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your API key
# NEO4J_URI=bolt://localhost:7687
# NEO4J_USER=neo4j
# NEO4J_PASSWORD=speedkg123
# ANTHROPIC_API_KEY=your_key_here

# Start backend server
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Step 3: Setup Frontend (New Terminal)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Start development server
npm start
```

Browser should automatically open to `http://localhost:3000`

### Step 4: Verify Everything Works

1. **Check Backend Health:**
   - Open http://localhost:8000/api/health
   - Should see: `{"status": "healthy", "neo4j": true, "claude": true}`

2. **Test Frontend:**
   - Click on an example query in the sidebar
   - Wait for response (5-10 seconds)
   - Should see text analysis + visualizations

### Step 5: Try Your First Query

Type in the chat:
```
"Show me event escalation patterns in Syria during 2011"
```

Expected Response:
- Text analysis of Syrian events in 2011
- Timeline visualization
- Network graph of event linkages

## Common Issues & Solutions

### Issue: "ANTHROPIC_API_KEY not found"

**Solution:**
1. Get API key from https://console.anthropic.com
2. Add to `backend/.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-...
   ```
3. Restart backend

### Issue: "Neo4j connection failed"

**Solution:**
1. Check Docker is running: `docker ps`
2. Verify Neo4j container is running: `docker ps | grep neo4j`
3. Check credentials in `backend/.env` match docker-compose.yml
4. Restart Neo4j: `docker-compose restart neo4j`

### Issue: "No data found" responses

**Solution:**
1. Ensure SPEED data is ingested:
   ```bash
   python ingest_speed_to_neo4j.py --validate-only
   ```
2. Check Neo4j Browser: http://localhost:7474
3. Run query: `MATCH (e:Event) RETURN count(e)`
4. Should return > 0 events

### Issue: Frontend can't connect to backend

**Solution:**
1. Check backend is running on port 8000
2. Verify `REACT_APP_API_URL=http://localhost:8000` in `frontend/.env`
3. Check CORS settings in backend allow `http://localhost:3000`
4. Restart both servers

### Issue: Visualizations don't appear

**Solution:**
1. Open browser DevTools (F12)
2. Check Console for errors
3. Verify data is being returned by backend
4. Check Network tab for successful API responses

## Usage Examples

### Example 1: Driver Analysis
```
"What are the main drivers of civil unrest in the Middle East from 2000-2020?"
```

Expected:
- Bar chart of driver distribution
- Text analysis of patterns
- Statistics about event counts

### Example 2: Temporal Trends
```
"Compare political violence vs state violence over time"
```

Expected:
- Line chart showing trends
- Timeline of events
- Analysis of escalation patterns

### Example 3: Actor Networks
```
"Who were the main actors in Syrian civil unrest?"
```

Expected:
- Network graph of actors
- Text analysis of key players
- Event count by actor

### Example 4: Geographic Distribution
```
"Which countries had the most intense events in 2011?"
```

Expected:
- Bar chart by country
- Intensity metrics
- Geographic analysis

## Next Steps

1. **Explore Example Queries**
   - Click on examples in the sidebar
   - Modify them to ask related questions

2. **Try Custom Queries**
   - Ask about specific countries
   - Query specific time periods
   - Investigate particular actors

3. **Understand the Data**
   - Review `/data/Questions.txt` for research questions
   - Check `/design/IMPLEMENTATION_GUIDE.md` for ontology
   - Explore Neo4j Browser: http://localhost:7474

4. **Customize Visualizations**
   - Edit D3.js components in `frontend/src/components/Visualizations/`
   - Adjust colors, sizes, layouts
   - Add new chart types

5. **Extend Query Templates**
   - Add templates in `backend/services/query_templates.py`
   - Update Planning Agent to use new templates
   - Add corresponding data preparation in Execution Agent

## Development Workflow

### Making Changes to Backend

1. Edit files in `backend/`
2. Server auto-reloads (uvicorn in reload mode)
3. Test at http://localhost:8000

### Making Changes to Frontend

1. Edit files in `frontend/src/`
2. React auto-reloads
3. Changes appear immediately in browser

### Adding New Features

1. **New Query Type:**
   - Add Cypher template to `query_templates.py`
   - Update `planning_agent.py` to recognize query
   - Update `execution_agent.py` to prepare data
   - Update `rendering_agent.py` if needed

2. **New Visualization:**
   - Create component in `frontend/src/components/Visualizations/`
   - Implement D3.js rendering
   - Add to `MessageCard.jsx`
   - Update backend to prepare data format

## Performance Tips

- Start with small time ranges for faster queries
- Use specific countries rather than global queries
- Limit results to 50-100 for quick responses
- Clear browser cache if visualizations lag

## Monitoring

### Backend Logs
```bash
# Watch backend logs
tail -f backend/*.log
```

### Frontend Console
- Open DevTools (F12) → Console
- Watch for errors or warnings

### Neo4j Query Performance
- Open Neo4j Browser: http://localhost:7474
- Use PROFILE to analyze slow queries
- Check indexes exist

## Stopping the Application

### Stop Frontend
```bash
# In frontend terminal
Ctrl+C
```

### Stop Backend
```bash
# In backend terminal
Ctrl+C
deactivate  # Exit virtual environment
```

### Stop Neo4j
```bash
# From project root
docker-compose down
```

## Getting Help

1. Check `README_WEBAPP.md` for detailed documentation
2. Review error messages in console/logs
3. Verify all prerequisites are met
4. Check Neo4j data is loaded
5. Ensure API keys are valid

## Success Criteria

You're successfully running when:
- [ ] Backend health check returns healthy
- [ ] Frontend loads without errors
- [ ] Example queries return results
- [ ] Visualizations render correctly
- [ ] Custom queries work

Enjoy exploring the SPEED Knowledge Graph! 🎉
