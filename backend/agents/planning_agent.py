"""Planning Agent - Analyzes queries and creates execution plans"""

from services.claude_service import ClaudeService
from typing import Dict
import json
import logging

logger = logging.getLogger(__name__)


class PlanningAgent:
    """
    Analyzes user queries and creates execution plans
    Uses Claude to understand intent and recommend visualizations
    """

    def __init__(self, claude_service: ClaudeService):
        self.claude = claude_service

    async def create_plan(self, user_query: str) -> Dict:
        """
        Create an execution plan for the user's query

        Args:
            user_query: Natural language query from user

        Returns:
            Execution plan dictionary with query specs and visualization recommendations
        """

        planning_prompt = f"""You are a SPEED Knowledge Graph query planning agent. Analyze the user's question and create a detailed execution plan.

User Question: "{user_query}"

Available Research Questions:
1. Origins and Drivers - What causes civil unrest? (anti-government, socio-cultural, class conflict, etc.)
2. Intensity - How severe are events? (casualties, violence levels, participants)
3. Dynamics - How do events escalate? (event chains, reactions, linkages)
4. Temporal Boundaries - When do episodes begin/end? (time periods, durations)
5. Precursor Events - Role of small events? (symbolic acts, protests leading to violence)
6. Actors - Who participates in unrest? (groups, individuals, governments)

Available Visualization Types:
- timeline: Shows events over time with intensity markers (best for temporal analysis)
- network_graph: Shows relationships between events/actors (best for dynamics, actors)
- bar_chart: Compares categories or metrics (best for distributions, comparisons)
- line_chart: Shows trends over time (best for temporal trends)
- choropleth_map: Geographic distribution (best for location-based queries)
- sankey_diagram: Flow between categories (best for driver/outcome flows)
- force_directed_graph: Actor-event networks (best for complex actor relationships)
- heatmap: Intensity patterns by time/location (best for patterns)

Available Query Templates:
- event_escalation_chain: Event sequences and linkages
- temporal_intensity_trend: Violence/intensity trends over time
- actor_network: Initiator-target relationships
- driver_distribution: Distribution of event drivers
- geographic_distribution: Events by location
- precursor_events: Small events leading to major ones
- intensity_by_event_type: Intensity by event category
- temporal_event_distribution: Events over time
- actor_involvement_by_role: Actor participation patterns
- event_outcomes_analysis: Results and impacts

Query Template Parameters (extract from user query):
- country: Country name (e.g., "Syria", "Egypt", "Lebanon")
- year: Specific year (e.g., 2011)
- start_year, end_year: Year range (e.g., 2000-2020)
- region: World region (e.g., "Middle East")
- limit: Number of results (default 50)
- casualty_threshold: Minimum casualties for filtering
- min_interactions: Minimum actor interactions

Analyze the query and return ONLY a valid JSON object (no other text) with this structure:
{{
  "query_intent": "brief description of what user wants",
  "research_questions": ["Q1", "Q2", ...],
  "cypher_queries": [
    {{
      "purpose": "description",
      "template": "template_name",
      "parameters": {{"param": "value"}}
    }}
  ],
  "visualizations": [
    {{
      "type": "viz_type",
      "title": "Visualization Title",
      "data_source": "query_purpose_matching_above"
    }}
  ],
  "text_sections": ["summary", "temporal_analysis", "actor_analysis", etc.]
}}

Example for "Show me event escalation in Syria 2011":
{{
  "query_intent": "Analyze event escalation patterns in Syria during 2011",
  "research_questions": ["Q3"],
  "cypher_queries": [
    {{
      "purpose": "event_chains",
      "template": "event_escalation_chain",
      "parameters": {{"country": "Syria", "year": 2011, "limit": 30}}
    }},
    {{
      "purpose": "intensity_trend",
      "template": "temporal_intensity_trend",
      "parameters": {{"country": "Syria", "start_year": 2011, "end_year": 2011}}
    }}
  ],
  "visualizations": [
    {{
      "type": "timeline",
      "title": "Syria Event Timeline 2011",
      "data_source": "intensity_trend"
    }},
    {{
      "type": "network_graph",
      "title": "Event Linkage Network",
      "data_source": "event_chains"
    }}
  ],
  "text_sections": ["summary", "temporal_analysis", "escalation_patterns", "intensity_assessment"]
}}

Return ONLY the JSON object, no markdown, no other text."""

        try:
            logger.info("🎯 Sending planning request to Claude...")

            response = await self.claude.generate(
                prompt=planning_prompt,
                max_tokens=2000,
                temperature=0.3  # Lower temperature for more consistent JSON
            )

            logger.info("📋 Processing Claude's planning response...")

            # Clean response - remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
                logger.info("  Removed JSON markdown wrapper")
            if response.startswith("```"):
                response = response[3:]
                logger.info("  Removed code block wrapper")
            if response.endswith("```"):
                response = response[:-3]
                logger.info("  Removed closing markdown")
            response = response.strip()

            # Parse JSON
            logger.info("  Parsing JSON execution plan...")
            plan = json.loads(response)

            logger.info("✅ Planning Agent Reasoning:")
            logger.info("-"*60)
            logger.info(f"🎯 Intent Identified: {plan.get('query_intent', 'N/A')}")
            logger.info(f"📚 Research Questions: {plan.get('research_questions', [])}")

            logger.info("\n📊 Execution Plan Details:")
            logger.info(f"  • Cypher queries to execute: {len(plan.get('cypher_queries', []))}")
            for i, q in enumerate(plan.get('cypher_queries', []), 1):
                logger.info(f"    {i}. {q.get('purpose')} → {q.get('template')}")
                logger.info(f"       Params: {q.get('parameters', {})}")

            logger.info(f"\n  • Visualizations to create: {len(plan.get('visualizations', []))}")
            for i, v in enumerate(plan.get('visualizations', []), 1):
                logger.info(f"    {i}. {v.get('type')} - {v.get('title')}")
                logger.info(f"       Data from: {v.get('data_source')}")

            logger.info(f"\n  • Text sections to include: {plan.get('text_sections', [])}")
            logger.info("-"*60)

            return plan

        except json.JSONDecodeError as e:
            logger.warning("⚠️  JSON Parse Error")
            logger.warning("-"*60)
            logger.warning(f"Error: {str(e)}")
            logger.warning("Response received was not valid JSON")
            logger.warning("Falling back to template-based plan")
            logger.warning("-"*60)
            return self._create_fallback_plan(user_query)
        except Exception as e:
            logger.error("❌ Planning Error")
            logger.error("-"*60)
            logger.error(f"Error: {str(e)}")
            logger.error("Falling back to template-based plan")
            logger.error("-"*60)
            return self._create_fallback_plan(user_query)

    def _create_fallback_plan(self, query: str) -> Dict:
        """Create a basic fallback plan if Claude response is invalid"""
        logger.info("Creating fallback plan")
        logger.info(f"  Original query: {query}")
        logger.info("  Using default template-based plan")

        return {
            "query_intent": "General SPEED data query",
            "research_questions": ["Q1"],
            "cypher_queries": [{
                "purpose": "recent_events",
                "template": "recent_events",
                "parameters": {"limit": 50}
            }],
            "visualizations": [{
                "type": "bar_chart",
                "title": "Event Distribution",
                "data_source": "recent_events"
            }],
            "text_sections": ["summary", "key_findings"]
        }
