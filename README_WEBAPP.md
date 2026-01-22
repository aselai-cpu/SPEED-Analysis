# SPEED Knowledge Graph - AI-Powered Query Interface

An intelligent web application that enables natural language queries to the SPEED (Social, Political and Economic Event Database) Knowledge Graph using a three-phase agentic workflow powered by Claude AI and interactive D3.js visualizations.

## Features

### 🤖 Agentic Workflow
- **Planning Agent** - Analyzes queries and creates execution plans using Claude
- **Execution Agent** - Executes Cypher queries against Neo4j
- **Rendering Agent** - Generates natural language analysis with Claude

### 📊 Interactive Visualizations
- **Timeline** - Temporal sequences with intensity markers (D3.js)
- **Network Graph** - Actor-event relationships (force-directed)
- **Bar Charts** - Comparative statistics
- **Line Charts** - Trend analysis

### 💬 Chat Interface
- Natural language query input
- Real-time streaming responses
- Markdown-formatted analysis
- Interactive D3.js charts embedded in responses

### 📚 Example Queries
Pre-built queries organized by research questions:
- Origins & Drivers
- Intensity Analysis
- Event Dynamics
- Temporal Analysis
- Precursor Events
- Actor Analysis

## Architecture

```
┌─────────────────────────────────────────┐
│   Frontend (React + D3.js + MUI)       │
│   - Chat interface                      │
│   - D3 visualizations                   │
│   - Example query sidebar               │
└─────────────────┬───────────────────────┘
                  │ HTTP/WebSocket
┌─────────────────┴───────────────────────┐
│   Backend (FastAPI + Python)            │
│   ┌──────────────────────────────────┐  │
│   │   Agentic Workflow Controller    │  │
│   │  Planning → Execution → Rendering│  │
│   └──────────────────────────────────┘  │
│   - Claude Service                      │
│   - Neo4j Service                       │
│   - Query Templates                     │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│   Neo4j Database (SPEED KG)             │
│   - Event nodes with temporal props     │
│   - Actor networks                      │
│   - Temporal relationships              │
└─────────────────────────────────────────┘
```

## Prerequisites

1. **Neo4j Database** - Running with SPEED data ingested
   ```bash
   docker-compose up -d
   ```

2. **Claude API Key** - From Anthropic
   - Sign up at https://console.anthropic.com
   - Get API key

3. **Python 3.10+** - For backend

4. **Node.js 18+** - For frontend

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Run backend
python main.py
```

Backend will start on `http://localhost:8000`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Run frontend
npm start
```

Frontend will start on `http://localhost:3000`

### 3. Access the Application

Open your browser to `http://localhost:3000`

## Configuration

### Backend (.env)

```bash
# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=speedkg123

# Claude API
ANTHROPIC_API_KEY=sk-ant-api03-...
CLAUDE_MODEL=claude-sonnet-4-5-20250929

# Server
PORT=8000
DEBUG=True

# CORS
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env)

```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

## Usage

### Ask Natural Language Questions

Simply type questions in the chat interface:

**Example Queries:**

```
"Show me event escalation patterns in Syria during 2011"

"What were the main drivers of civil unrest in the Middle East from 2000-2020?"

"Compare political violence vs state violence over time"

"Which groups were most active across the Arab Spring?"

"Find small protests that led to major conflicts"
```

### How It Works

1. **You ask a question** in natural language

2. **Planning Agent** analyzes your query and creates a plan:
   - Identifies research questions
   - Selects appropriate Cypher queries
   - Recommends visualizations

3. **Execution Agent** executes the plan:
   - Runs Cypher queries against Neo4j
   - Retrieves and processes data
   - Prepares D3.js visualization data

4. **Rendering Agent** generates the response:
   - Uses Claude to write analysis text
   - Formats visualizations
   - Combines text and charts

5. **You receive** a rich response with:
   - Markdown-formatted text analysis
   - Interactive D3.js visualizations
   - Metadata about the query

## API Endpoints

### REST API

- `GET /` - API information
- `GET /api/health` - Health check
- `POST /api/query` - Process a natural language query
- `GET /api/examples` - Get example queries

### WebSocket

- `WS /ws/query` - Streaming query responses with real-time updates

## Development

### Backend Structure

```
backend/
├── main.py                  # FastAPI application
├── agents/
│   ├── planning_agent.py    # Query planning with Claude
│   ├── execution_agent.py   # Cypher execution
│   └── rendering_agent.py   # Response generation
├── services/
│   ├── claude_service.py    # Claude API integration
│   ├── neo4j_service.py     # Neo4j connection
│   └── query_templates.py   # Cypher templates
└── models/
    └── query_models.py      # Pydantic models
```

### Frontend Structure

```
frontend/src/
├── App.js                   # Main application
├── components/
│   ├── ChatInterface/       # Chat UI
│   ├── Visualizations/      # D3.js components
│   ├── ResponseCard/        # Message display
│   └── UI/                  # Header, Sidebar
├── hooks/
│   └── useQuery.js          # Query management
└── services/
    └── apiService.js        # Backend API calls
```

### Adding New Visualizations

1. Create component in `frontend/src/components/Visualizations/`
2. Implement D3.js visualization logic
3. Add to `MessageCard.jsx` renderer
4. Update `Execution Agent` to prepare data format

### Adding New Query Templates

1. Add Cypher template to `backend/services/query_templates.py`
2. Update `Planning Agent` to recognize new query types
3. Update `Execution Agent` to prepare visualization data

## Troubleshooting

### Backend Issues

**"Claude API error"**
- Check `ANTHROPIC_API_KEY` in `.env`
- Verify API key is valid

**"Neo4j connection failed"**
- Ensure Neo4j is running: `docker ps`
- Check `NEO4J_URI` and credentials
- Verify SPEED data is ingested

**"Module not found"**
- Activate virtual environment
- Run `pip install -r requirements.txt`

### Frontend Issues

**"Cannot connect to backend"**
- Check backend is running on port 8000
- Verify `REACT_APP_API_URL` in `.env`

**"Visualizations not rendering"**
- Check browser console for errors
- Verify D3.js data format
- Ensure data is not empty

**"npm start fails"**
- Delete `node_modules` and run `npm install` again
- Check Node.js version (18+)

## Performance Tips

1. **Limit query results** - Use smaller `limit` values for faster responses
2. **Specific queries** - More specific queries execute faster
3. **Cache responses** - Backend could cache common queries
4. **Batch processing** - Group similar queries together

## Security Notes

- Never commit `.env` files with API keys
- Use environment variables for all secrets
- Enable CORS only for trusted origins
- Validate user inputs on backend

## Deployment

### Docker Compose (Full Stack)

```yaml
version: '3.8'
services:
  neo4j:
    image: neo4j:5.16-community
    # ... (existing config)

  backend:
    build: ./backend
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
```

### Production Considerations

1. **Backend**
   - Use `uvicorn` with multiple workers
   - Add rate limiting
   - Enable logging to files
   - Use production ASGI server

2. **Frontend**
   - Build for production: `npm run build`
   - Serve with nginx
   - Enable compression
   - Add caching headers

3. **Security**
   - Use HTTPS
   - Implement authentication
   - Add API rate limiting
   - Sanitize user inputs

## License

This application interfaces with the SPEED dataset. Please consult SPEED dataset licensing terms.

## Support

For issues or questions:
- Check logs in `backend/` console output
- Review API responses in browser DevTools
- Examine Neo4j query execution in Neo4j Browser

## Contributing

To extend functionality:
1. Add new query templates in backend
2. Create new D3.js visualizations
3. Enhance Planning Agent prompts
4. Add more example queries

## Acknowledgments

- **SPEED Dataset** - Social, Political and Economic Event Database
- **Anthropic Claude** - AI language model for analysis
- **D3.js** - Data visualization library
- **Neo4j** - Graph database platform
