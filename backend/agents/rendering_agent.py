"""Rendering Agent - Generates final response with text and visualizations"""

from services.claude_service import ClaudeService
from models.query_models import (
    QueryResponse, ResponseContent, ResponseMetadata,
    VisualizationSpec
)
from typing import Dict, List
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class RenderingAgent:
    """
    Generates natural language analysis and final response
    Combines Claude-generated text with visualization specifications
    """

    def __init__(self, claude_service: ClaudeService):
        self.claude = claude_service

    async def render(
        self,
        user_query: str,
        execution_plan: Dict,
        execution_results: Dict
    ) -> QueryResponse:
        """
        Generate final response with text and visualizations

        Args:
            user_query: Original user query
            execution_plan: Plan from Planning Agent
            execution_results: Results from Execution Agent

        Returns:
            QueryResponse with text analysis and visualizations
        """

        try:
            logger.info("✨ Rendering Agent: Generating final response...")
            logger.info("-"*60)

            # Generate text analysis
            logger.info("📝 Step 1: Generating natural language analysis with Claude...")
            text_content = await self._generate_text_analysis(
                user_query,
                execution_plan,
                execution_results
            )
            logger.info(f"  ✅ Text analysis generated: {len(text_content)} characters")

            # Format visualizations
            logger.info("\n📊 Step 2: Formatting visualizations for frontend...")
            visualizations = self._format_visualizations(
                execution_results.get("visualizations_data", [])
            )
            logger.info(f"  ✅ Formatted {len(visualizations)} visualizations:")
            for i, viz in enumerate(visualizations, 1):
                logger.info(f"    {i}. {viz.type} - {viz.title}")

            # Create response
            logger.info("\n📦 Step 3: Creating response object...")
            response = QueryResponse(
                message_id=str(uuid.uuid4()),
                response_type="analysis",
                content=ResponseContent(
                    text=text_content,
                    visualizations=visualizations
                ),
                metadata=ResponseMetadata(
                    data_points=execution_results.get("statistics", {}).get("total_records", 0),
                    visualizations_count=len(visualizations)
                ),
                timestamp=datetime.now()
            )

            logger.info("\n✅ Rendering Agent Complete:")
            logger.info(f"  • Message ID: {response.message_id}")
            logger.info(f"  • Response Type: {response.response_type}")
            logger.info(f"  • Text Length: {len(text_content)} chars")
            logger.info(f"  • Visualizations: {len(visualizations)}")
            logger.info(f"  • Data Points: {response.metadata.data_points}")
            logger.info("-"*60)

            return response

        except Exception as e:
            logger.error("❌ Rendering Agent Error")
            logger.error("-"*60)
            logger.error(f"Error: {str(e)}", exc_info=True)
            logger.error("-"*60)
            # Return error response
            return self._create_error_response(str(e))

    async def _generate_text_analysis(
        self,
        query: str,
        plan: Dict,
        results: Dict
    ) -> str:
        """
        Use Claude to generate natural language analysis

        Args:
            query: User query
            plan: Execution plan
            results: Execution results

        Returns:
            Markdown-formatted text analysis
        """

        # Build data summary
        logger.info("  📊 Building data summary for Claude...")
        data_summary = self._build_data_summary(results)
        logger.info(f"  ✅ Data summary prepared ({len(data_summary)} chars)")

        logger.info("  🤖 Preparing analysis prompt for Claude...")
        analysis_prompt = f"""You are analyzing civil unrest data from the SPEED Knowledge Graph.

User Query: "{query}"

Query Intent: {plan.get("query_intent", "General analysis")}

Research Questions Addressed: {', '.join(plan.get("research_questions", []))}

Data Retrieved:
{data_summary}

Statistics:
- Total Records: {results.get("statistics", {}).get("total_records", 0)}
- Queries Executed: {results.get("statistics", {}).get("queries_executed", 0)}

Provide a comprehensive analysis using markdown formatting. Include:

# Analysis Title (based on the query)

## Executive Summary
[2-3 sentences highlighting the most important findings]

## Key Findings
[Bullet points with specific numbers and insights from the data]

## Detailed Analysis
[Deeper analysis organized by relevant sections - choose from: temporal patterns, actor involvement, intensity assessment, geographic distribution, drivers analysis, outcomes]

## Context and Insights
[Broader contextual understanding and implications]

## Data Notes
[Any limitations or notes about the data]

**Note:** Interactive visualizations appear below to illustrate these findings.

Use specific numbers from the data. Be analytical and objective. Keep the total response under 1000 words.
"""

        try:
            logger.info("  ⏳ Sending analysis request to Claude...")

            text = await self.claude.generate(
                prompt=analysis_prompt,
                max_tokens=2500,
                temperature=0.7
            )

            logger.info(f"  ✅ Claude analysis received ({len(text)} chars)")

            return text

        except Exception as e:
            logger.error(f"  ❌ Text generation error: {str(e)}")
            logger.warning("  ⚠️  Using fallback text response")
            return self._create_fallback_text(query, results)

    def _build_data_summary(self, results: Dict) -> str:
        """Create a text summary of the retrieved data"""
        summary_lines = []

        for query_result in results.get("query_results", []):
            purpose = query_result.get("purpose", "Unknown")
            count = query_result.get("record_count", 0)
            data = query_result.get("data", [])

            summary_lines.append(f"\n{purpose}:")
            summary_lines.append(f"  - {count} records retrieved")

            # Add sample data insights
            if data and len(data) > 0:
                sample = data[0]

                # Temporal data
                if "year" in sample:
                    years = [r.get("year") for r in data if "year" in r]
                    if years:
                        summary_lines.append(f"  - Time range: {min(years)} to {max(years)}")

                # Event counts
                if "event_count" in sample:
                    total_events = sum(r.get("event_count", 0) for r in data)
                    summary_lines.append(f"  - Total events: {total_events}")

                # Casualties
                if "total_casualties" in sample:
                    total_casualties = sum(r.get("total_casualties", 0) for r in data)
                    summary_lines.append(f"  - Total casualties: {total_casualties}")

                # Countries
                if "country" in sample:
                    countries = set(r.get("country") for r in data if r.get("country"))
                    summary_lines.append(f"  - Countries: {', '.join(list(countries)[:5])}")

        return "\n".join(summary_lines) if summary_lines else "No data summary available"

    def _create_fallback_text(self, query: str, results: Dict) -> str:
        """Create fallback text if Claude generation fails"""
        stats = results.get("statistics", {})

        return f"""# SPEED Knowledge Graph Analysis

## Query
{query}

## Summary
Analysis of {stats.get('total_records', 0)} records from the SPEED Knowledge Graph.

## Data Retrieved
- {stats.get('queries_executed', 0)} queries executed
- {stats.get('total_records', 0)} total records

## Findings
The data has been retrieved and visualized below. Interactive visualizations provide detailed insights into the patterns and trends.

## Note
For detailed textual analysis, please ensure the Claude API is properly configured.
"""

    def _format_visualizations(
        self,
        viz_data: List[Dict]
    ) -> List[VisualizationSpec]:
        """Format visualization specs for frontend"""
        formatted = []

        for viz in viz_data:
            if not viz:
                continue

            try:
                viz_spec = VisualizationSpec(
                    id=f"viz_{uuid.uuid4().hex[:8]}",
                    type=viz.get("type", "unknown"),
                    title=viz.get("title", "Visualization"),
                    spec={},  # D3 spec can be added here
                    data=viz.get("data", {})
                )
                formatted.append(viz_spec)
            except Exception as e:
                logger.warning(f"Failed to format visualization: {str(e)}")

        return formatted

    def _create_error_response(self, error: str) -> QueryResponse:
        """Create an error response"""
        return QueryResponse(
            message_id=str(uuid.uuid4()),
            response_type="error",
            content=ResponseContent(
                text=f"# Error\n\nAn error occurred while processing your query:\n\n{error}",
                visualizations=[]
            ),
            metadata=ResponseMetadata(
                data_points=0,
                visualizations_count=0
            ),
            timestamp=datetime.now()
        )
