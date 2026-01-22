"""
SPEED Knowledge Graph - AI-Powered Query Interface
FastAPI Backend with Agentic Workflow

This application enables natural language queries to the SPEED Knowledge Graph
using a three-phase agentic workflow powered by Claude AI.
"""

from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv

from agents.planning_agent import PlanningAgent
from agents.execution_agent import ExecutionAgent
from agents.rendering_agent import RenderingAgent
from services.neo4j_service import Neo4jService
from services.claude_service import ClaudeService
from models.query_models import QueryRequest, QueryResponse

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global services (will be initialized in lifespan)
neo4j_service = None
claude_service = None
planning_agent = None
execution_agent = None
rendering_agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    global neo4j_service, claude_service, planning_agent, execution_agent, rendering_agent

    # Startup
    logger.info("Initializing services...")

    neo4j_service = Neo4jService()
    claude_service = ClaudeService()

    planning_agent = PlanningAgent(claude_service)
    execution_agent = ExecutionAgent(neo4j_service)
    rendering_agent = RenderingAgent(claude_service)

    logger.info("Services initialized successfully")

    yield

    # Shutdown
    logger.info("Shutting down services...")
    if neo4j_service:
        neo4j_service.close()
    logger.info("Services shut down successfully")


# Create FastAPI application
app = FastAPI(
    title="SPEED Knowledge Graph Query API",
    description="AI-powered natural language interface for the SPEED dataset",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SPEED Knowledge Graph Query API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "neo4j": neo4j_service.is_connected() if neo4j_service else False,
        "claude": claude_service.is_available() if claude_service else False
    }


@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Main endpoint for processing natural language queries
    Implements the three-phase agentic workflow:
    1. Planning - Analyze query and create execution plan
    2. Execution - Execute Cypher queries and prepare data
    3. Rendering - Generate text analysis and visualizations
    """
    try:
        logger.info("="*80)
        logger.info("🚀 NEW QUERY RECEIVED")
        logger.info("="*80)
        logger.info(f"📝 User Query: {request.query}")
        logger.info("-"*80)

        # Phase 1: Planning
        logger.info("🧠 PHASE 1: PLANNING AGENT")
        logger.info("="*80)
        logger.info("Analyzing query intent and creating execution plan...")

        execution_plan = await planning_agent.create_plan(request.query)

        logger.info("✅ Planning Complete")
        logger.info(f"📊 Query Intent: {execution_plan.get('query_intent', 'N/A')}")
        logger.info(f"🔍 Research Questions: {', '.join(execution_plan.get('research_questions', []))}")
        logger.info(f"📈 Cypher Queries Planned: {len(execution_plan.get('cypher_queries', []))}")
        logger.info(f"📉 Visualizations Planned: {len(execution_plan.get('visualizations', []))}")

        # Log planned queries
        for i, query_spec in enumerate(execution_plan.get('cypher_queries', []), 1):
            logger.info(f"  Query {i}: {query_spec.get('purpose')} using template '{query_spec.get('template')}'")

        # Log planned visualizations
        for i, viz in enumerate(execution_plan.get('visualizations', []), 1):
            logger.info(f"  Viz {i}: {viz.get('type')} - {viz.get('title')}")

        logger.info("-"*80)

        # Phase 2: Execution
        logger.info("⚙️  PHASE 2: EXECUTION AGENT")
        logger.info("="*80)
        logger.info("Executing Cypher queries against Neo4j...")

        execution_results = await execution_agent.execute(execution_plan)

        logger.info("✅ Execution Complete")
        logger.info(f"📦 Total Records Retrieved: {execution_results['statistics'].get('total_records', 0)}")
        logger.info(f"🔢 Queries Executed: {execution_results['statistics'].get('queries_executed', 0)}")

        # Log results per query
        for result in execution_results.get('query_results', []):
            logger.info(f"  {result.get('purpose')}: {result.get('record_count', 0)} records")

        logger.info(f"📊 Visualizations Prepared: {len(execution_results.get('visualizations_data', []))}")
        logger.info("-"*80)

        # Phase 3: Rendering
        logger.info("✨ PHASE 3: RENDERING AGENT")
        logger.info("="*80)
        logger.info("Generating natural language analysis with Claude...")

        response = await rendering_agent.render(
            request.query,
            execution_plan,
            execution_results
        )

        logger.info("✅ Rendering Complete")
        logger.info(f"📝 Text Analysis Generated: {len(response.content.text)} characters")
        logger.info(f"📊 Final Visualizations: {len(response.content.visualizations)}")
        logger.info(f"🎯 Data Points: {response.metadata.data_points}")
        logger.info("="*80)
        logger.info("✅ QUERY PROCESSING COMPLETE")
        logger.info("="*80)

        return response

    except Exception as e:
        logger.error("="*80)
        logger.error("❌ ERROR PROCESSING QUERY")
        logger.error("="*80)
        logger.error(f"Error: {str(e)}", exc_info=True)
        logger.error("="*80)
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/query")
async def websocket_query(websocket: WebSocket):
    """
    WebSocket endpoint for streaming responses
    Sends real-time updates for each phase of the workflow
    """
    await websocket.accept()
    logger.info("WebSocket connection established")

    try:
        while True:
            # Receive query from client
            data = await websocket.receive_json()
            query = data.get("query")

            if not query:
                await websocket.send_json({
                    "error": "No query provided"
                })
                continue

            logger.info(f"WebSocket query: {query}")

            # Phase 1: Planning
            await websocket.send_json({
                "phase": "planning",
                "status": "in_progress",
                "message": "Analyzing your question and planning response strategy..."
            })

            try:
                execution_plan = await planning_agent.create_plan(query)

                await websocket.send_json({
                    "phase": "planning",
                    "status": "complete",
                    "plan": {
                        "intent": execution_plan.get("query_intent", ""),
                        "visualizations": len(execution_plan.get("visualizations", []))
                    }
                })
            except Exception as e:
                await websocket.send_json({
                    "phase": "planning",
                    "status": "error",
                    "error": str(e)
                })
                continue

            # Phase 2: Execution
            await websocket.send_json({
                "phase": "execution",
                "status": "in_progress",
                "message": "Querying the knowledge graph..."
            })

            try:
                execution_results = await execution_agent.execute(execution_plan)

                await websocket.send_json({
                    "phase": "execution",
                    "status": "complete",
                    "stats": {
                        "records": execution_results["statistics"].get("total_records", 0)
                    }
                })
            except Exception as e:
                await websocket.send_json({
                    "phase": "execution",
                    "status": "error",
                    "error": str(e)
                })
                continue

            # Phase 3: Rendering
            await websocket.send_json({
                "phase": "rendering",
                "status": "in_progress",
                "message": "Generating analysis and visualizations..."
            })

            try:
                response = await rendering_agent.render(
                    query,
                    execution_plan,
                    execution_results
                )

                await websocket.send_json({
                    "phase": "rendering",
                    "status": "complete",
                    "response": response.dict()
                })
            except Exception as e:
                await websocket.send_json({
                    "phase": "rendering",
                    "status": "error",
                    "error": str(e)
                })
                continue

    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}", exc_info=True)
        try:
            await websocket.send_json({
                "error": str(e)
            })
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass


@app.get("/api/examples")
async def get_example_queries():
    """Get example queries organized by category"""
    return {
        "categories": [
            {
                "category": "Origins & Drivers",
                "queries": [
                    "What are the main drivers of civil unrest in the Middle East from 2000-2020?",
                    "Compare anti-government vs socio-cultural drivers globally",
                    "Show me how drivers changed over time in Latin America"
                ]
            },
            {
                "category": "Intensity Analysis",
                "queries": [
                    "Which countries had the most intense events in 2011?",
                    "Show casualty trends in Syria from 2011-2015",
                    "Compare political violence vs state violence over time"
                ]
            },
            {
                "category": "Event Dynamics",
                "queries": [
                    "Show me event escalation chains in Syria 2011",
                    "How did the Arab Spring events link together?",
                    "What outcomes resulted from protests in Egypt?"
                ]
            },
            {
                "category": "Temporal Analysis",
                "queries": [
                    "When did major instability episodes occur in Lebanon?",
                    "Show me the timeline of events in Libya 2011",
                    "Identify peaks of unrest globally by decade"
                ]
            },
            {
                "category": "Precursor Events",
                "queries": [
                    "Find small protests that led to major conflicts",
                    "Show the progression from symbolic acts to violence",
                    "Which political expressions preceded coups?"
                ]
            },
            {
                "category": "Actor Analysis",
                "queries": [
                    "Who were the main actors in Syrian civil unrest?",
                    "Show me the network of initiators and targets in Egypt 2011",
                    "Which groups were most active across the Arab Spring?"
                ]
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
