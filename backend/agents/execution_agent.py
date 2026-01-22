"""Execution Agent - Executes Cypher queries and prepares visualization data"""

from services.neo4j_service import Neo4jService
from services.query_templates import QUERY_TEMPLATES, DEFAULT_PARAMETERS
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class ExecutionAgent:
    """
    Executes Cypher queries and prepares data for visualizations
    Transforms raw graph data into D3.js-ready formats
    """

    def __init__(self, neo4j_service: Neo4jService):
        self.neo4j = neo4j_service

    async def execute(self, execution_plan: Dict) -> Dict:
        """
        Execute all queries in the plan and prepare data

        Args:
            execution_plan: Plan from Planning Agent

        Returns:
            Dictionary with query results, visualization data, and statistics
        """
        results = {
            "query_results": [],
            "visualizations_data": [],
            "statistics": {}
        }

        try:
            logger.info("⚙️  Execution Agent: Processing execution plan...")
            logger.info("-"*60)

            # Execute each Cypher query
            total_queries = len(execution_plan.get("cypher_queries", []))
            logger.info(f"📊 Total queries to execute: {total_queries}")

            for i, query_spec in enumerate(execution_plan.get("cypher_queries", []), 1):
                template_name = query_spec.get("template")
                params = query_spec.get("parameters", {})
                purpose = query_spec.get("purpose", "unknown")

                logger.info(f"\n🔍 Query {i}/{total_queries}: {purpose}")
                logger.info(f"  Template: {template_name}")
                logger.info(f"  Parameters: {params}")

                # Merge with defaults
                full_params = {**DEFAULT_PARAMETERS, **params}

                if template_name in QUERY_TEMPLATES:
                    cypher = QUERY_TEMPLATES[template_name]

                    logger.info(f"  ⏳ Executing Neo4j query...")

                    data = await self.neo4j.execute_query(cypher, full_params)

                    results["query_results"].append({
                        "purpose": purpose,
                        "template": template_name,
                        "data": data,
                        "record_count": len(data)
                    })

                    logger.info(f"  ✅ Retrieved {len(data)} records")
                else:
                    logger.warning(f"  ⚠️  Template not found: {template_name}")

            logger.info("\n" + "-"*60)
            logger.info("📊 Preparing visualization data...")

            # Prepare visualization data
            total_viz = len(execution_plan.get("visualizations", []))
            logger.info(f"  Visualizations to prepare: {total_viz}")

            for i, viz_spec in enumerate(execution_plan.get("visualizations", []), 1):
                viz_type = viz_spec.get("type")
                viz_title = viz_spec.get("title")
                data_source = viz_spec.get("data_source")

                logger.info(f"\n  📈 Viz {i}/{total_viz}: {viz_type}")
                logger.info(f"    Title: {viz_title}")
                logger.info(f"    Data Source: {data_source}")

                viz_data = self._prepare_visualization_data(
                    viz_spec,
                    results["query_results"]
                )

                if viz_data:
                    results["visualizations_data"].append(viz_data)
                    logger.info(f"    ✅ Prepared successfully")
                else:
                    logger.warning(f"    ⚠️  Failed to prepare visualization")

            # Calculate statistics
            logger.info("\n" + "-"*60)
            logger.info("📊 Calculating statistics...")

            results["statistics"] = self._calculate_statistics(
                results["query_results"]
            )

            logger.info(f"✅ Execution Agent Complete:")
            logger.info(f"  • Total records: {results['statistics'].get('total_records', 0)}")
            logger.info(f"  • Queries executed: {results['statistics'].get('queries_executed', 0)}")
            logger.info(f"  • Visualizations prepared: {len(results['visualizations_data'])}")
            logger.info("-"*60)

        except Exception as e:
            logger.error("❌ Execution Agent Error")
            logger.error("-"*60)
            logger.error(f"Error: {str(e)}", exc_info=True)
            logger.error("-"*60)
            # Return partial results
            results["error"] = str(e)

        return results

    def _prepare_visualization_data(
        self,
        viz_spec: Dict,
        query_results: List[Dict]
    ) -> Dict:
        """
        Transform query results into D3-ready format

        Args:
            viz_spec: Visualization specification
            query_results: Results from Cypher queries

        Returns:
            Visualization data dictionary
        """
        viz_type = viz_spec.get("type")
        data_source = viz_spec.get("data_source")
        title = viz_spec.get("title", "")

        # Find matching query result
        source_data = None
        for result in query_results:
            if result["purpose"] == data_source:
                source_data = result["data"]
                break

        if not source_data:
            logger.warning(f"No data found for source: {data_source}")
            return None

        # Route to appropriate preparation method
        if viz_type == "timeline":
            return self._prepare_timeline(source_data, title)
        elif viz_type == "network_graph":
            return self._prepare_network_graph(source_data, title)
        elif viz_type == "bar_chart":
            return self._prepare_bar_chart(source_data, title)
        elif viz_type == "line_chart":
            return self._prepare_line_chart(source_data, title)
        elif viz_type == "sankey_diagram":
            return self._prepare_sankey(source_data, title)
        elif viz_type == "choropleth_map":
            return self._prepare_choropleth(source_data, title)
        elif viz_type == "heatmap":
            return self._prepare_heatmap(source_data, title)
        elif viz_type == "force_directed_graph":
            return self._prepare_force_directed(source_data, title)
        else:
            logger.warning(f"Unknown visualization type: {viz_type}")
            logger.warning(f"  Falling back to bar_chart for visualization")
            # Fallback to bar chart
            return self._prepare_bar_chart(source_data, title)

    def _prepare_timeline(self, data: List[Dict], title: str) -> Dict:
        """Prepare data for D3 timeline visualization"""
        events = []

        for record in data:
            # Handle different data structures
            if "year" in record:
                # Temporal data
                date_str = f"{record.get('year', 2000)}-{record.get('month', 1):02d}-01"
                events.append({
                    "date": date_str,
                    "value": record.get("event_count", 0),
                    "intensity": record.get("avg_political_violence", 0),
                    "casualties": record.get("total_casualties", 0),
                    "label": f"{record.get('year')}-{record.get('month', 1):02d}"
                })

        if not events:
            return None

        return {
            "type": "timeline",
            "title": title,
            "data": {
                "events": sorted(events, key=lambda x: x["date"]),
                "timeRange": {
                    "start": min(e["date"] for e in events),
                    "end": max(e["date"] for e in events)
                }
            }
        }

    def _prepare_network_graph(self, data: List[Dict], title: str) -> Dict:
        """Prepare data for D3 network graph"""
        nodes = []
        links = []
        node_ids = set()

        for record in data:
            # Actor network
            if "initiator" in record and "target" in record:
                init_id = record.get("initiator_id", record.get("initiator"))
                targ_id = record.get("target_id", record.get("target"))

                if init_id not in node_ids:
                    nodes.append({
                        "id": init_id,
                        "label": record.get("initiator", "Unknown"),
                        "type": "initiator",
                        "size": 10
                    })
                    node_ids.add(init_id)

                if targ_id not in node_ids:
                    nodes.append({
                        "id": targ_id,
                        "label": record.get("target", "Unknown"),
                        "type": "target",
                        "size": 10
                    })
                    node_ids.add(targ_id)

                links.append({
                    "source": init_id,
                    "target": targ_id,
                    "value": record.get("interaction_count", 1)
                })

        if not nodes:
            return None

        return {
            "type": "network_graph",
            "title": title,
            "data": {
                "nodes": nodes,
                "links": links
            }
        }

    def _prepare_bar_chart(self, data: List[Dict], title: str) -> Dict:
        """Prepare data for D3 bar chart"""
        categories = []

        # Handle driver distribution
        if len(data) > 0 and "anti_government" in data[0]:
            record = data[0]
            categories = [
                {"category": "Anti-Government", "value": record.get("anti_government", 0)},
                {"category": "Socio-Cultural", "value": record.get("sociocultural", 0)},
                {"category": "Class-Based", "value": record.get("class_based", 0)},
                {"category": "Economic", "value": record.get("economic", 0)},
                {"category": "Political Rights", "value": record.get("political_rights", 0)}
            ]
        # Handle event type distribution
        elif "event_type" in data[0]:
            for record in data:
                categories.append({
                    "category": record.get("event_type", "Unknown"),
                    "value": record.get("event_count", 0),
                    "intensity": record.get("avg_violence", 0)
                })
        # Generic case
        else:
            for record in data:
                if "country" in record:
                    categories.append({
                        "category": record.get("country", "Unknown"),
                        "value": record.get("event_count", 0)
                    })

        if not categories:
            return None

        return {
            "type": "bar_chart",
            "title": title,
            "data": {
                "categories": categories
            }
        }

    def _prepare_line_chart(self, data: List[Dict], title: str) -> Dict:
        """Prepare data for D3 line chart"""
        series = []

        for record in data:
            if "year" in record:
                point = {
                    "x": record.get("year"),
                    "y": record.get("event_count", 0),
                    "violence": record.get("avg_political_violence", 0)
                }
                series.append(point)

        if not series:
            return None

        return {
            "type": "line_chart",
            "title": title,
            "data": {
                "series": sorted(series, key=lambda x: x["x"])
            }
        }

    def _prepare_sankey(self, data: List[Dict], title: str) -> Dict:
        """Prepare data for D3 Sankey diagram"""
        nodes = []
        links = []
        node_names = set()

        for record in data:
            # Sankey diagrams show flow from source to target
            # Handle precursor event flows
            if "precursor_type" in record and "result_type" in record:
                source = record.get("precursor_type", "Unknown")
                target = record.get("result_type", "Unknown")
                value = record.get("flow_count", 1)

                if source not in node_names:
                    nodes.append({"id": len(nodes), "name": source})
                    node_names.add(source)

                if target not in node_names:
                    nodes.append({"id": len(nodes), "name": target})
                    node_names.add(target)

                source_id = next(i for i, n in enumerate(nodes) if n["name"] == source)
                target_id = next(i for i, n in enumerate(nodes) if n["name"] == target)

                links.append({
                    "source": source_id,
                    "target": target_id,
                    "value": value
                })

            # Handle driver to outcome flows
            elif "driver" in record and "outcome" in record:
                source = record.get("driver", "Unknown")
                target = record.get("outcome", "Unknown")
                value = record.get("event_count", 1)

                if source not in node_names:
                    nodes.append({"id": len(nodes), "name": source})
                    node_names.add(source)

                if target not in node_names:
                    nodes.append({"id": len(nodes), "name": target})
                    node_names.add(target)

                source_id = next(i for i, n in enumerate(nodes) if n["name"] == source)
                target_id = next(i for i, n in enumerate(nodes) if n["name"] == target)

                links.append({
                    "source": source_id,
                    "target": target_id,
                    "value": value
                })

        if not nodes:
            logger.warning("No Sankey data available - no source/target pairs found")
            return None

        return {
            "type": "sankey_diagram",
            "title": title,
            "data": {
                "nodes": nodes,
                "links": links
            }
        }

    def _prepare_choropleth(self, data: List[Dict], title: str) -> Dict:
        """Prepare data for D3 choropleth map"""
        regions = []

        for record in data:
            if "country" in record or "location" in record:
                location = record.get("country") or record.get("location", "Unknown")
                value = record.get("event_count", 0) or record.get("intensity", 0)

                regions.append({
                    "location": location,
                    "value": value,
                    "casualties": record.get("total_casualties", 0),
                    "avg_intensity": record.get("avg_political_violence", 0)
                })

        if not regions:
            logger.warning("No geographic data available for choropleth")
            return None

        return {
            "type": "choropleth_map",
            "title": title,
            "data": {
                "regions": regions
            }
        }

    def _prepare_heatmap(self, data: List[Dict], title: str) -> Dict:
        """Prepare data for D3 heatmap"""
        cells = []

        for record in data:
            # Time-based heatmap (year x month)
            if "year" in record and "month" in record:
                cells.append({
                    "x": record.get("year"),
                    "y": record.get("month"),
                    "value": record.get("event_count", 0),
                    "intensity": record.get("avg_political_violence", 0)
                })

            # Category-based heatmap
            elif "category1" in record and "category2" in record:
                cells.append({
                    "x": record.get("category1"),
                    "y": record.get("category2"),
                    "value": record.get("value", 0)
                })

            # Country x event type heatmap
            elif "country" in record and "event_type" in record:
                cells.append({
                    "x": record.get("country"),
                    "y": record.get("event_type"),
                    "value": record.get("event_count", 0),
                    "intensity": record.get("avg_intensity", 0)
                })

        if not cells:
            logger.warning("No heatmap data available - no x/y coordinate pairs found")
            return None

        return {
            "type": "heatmap",
            "title": title,
            "data": {
                "cells": cells
            }
        }

    def _prepare_force_directed(self, data: List[Dict], title: str) -> Dict:
        """Prepare data for D3 force-directed graph (advanced network)"""
        nodes = []
        links = []
        node_ids = set()

        for record in data:
            # Actor-event network
            if "actor_id" in record and "event_id" in record:
                actor_id = f"actor_{record.get('actor_id')}"
                event_id = f"event_{record.get('event_id')}"

                if actor_id not in node_ids:
                    nodes.append({
                        "id": actor_id,
                        "label": record.get("actor_name", "Unknown Actor"),
                        "type": "actor",
                        "size": record.get("interaction_count", 5)
                    })
                    node_ids.add(actor_id)

                if event_id not in node_ids:
                    nodes.append({
                        "id": event_id,
                        "label": record.get("event_type", "Unknown Event"),
                        "type": "event",
                        "size": record.get("intensity", 5)
                    })
                    node_ids.add(event_id)

                links.append({
                    "source": actor_id,
                    "target": event_id,
                    "value": record.get("strength", 1),
                    "type": record.get("relationship", "participated")
                })

            # Generic node-node network
            elif "source" in record and "target" in record:
                source_id = str(record.get("source"))
                target_id = str(record.get("target"))

                if source_id not in node_ids:
                    nodes.append({
                        "id": source_id,
                        "label": record.get("source_label", source_id),
                        "type": record.get("source_type", "node"),
                        "size": 10
                    })
                    node_ids.add(source_id)

                if target_id not in node_ids:
                    nodes.append({
                        "id": target_id,
                        "label": record.get("target_label", target_id),
                        "type": record.get("target_type", "node"),
                        "size": 10
                    })
                    node_ids.add(target_id)

                links.append({
                    "source": source_id,
                    "target": target_id,
                    "value": record.get("weight", 1)
                })

        if not nodes:
            logger.warning("No force-directed graph data available")
            return None

        return {
            "type": "force_directed_graph",
            "title": title,
            "data": {
                "nodes": nodes,
                "links": links
            }
        }

    def _calculate_statistics(self, query_results: List[Dict]) -> Dict:
        """Calculate summary statistics"""
        stats = {
            "total_records": sum(r.get("record_count", 0) for r in query_results),
            "queries_executed": len(query_results)
        }

        # Add query-specific stats
        for result in query_results:
            purpose = result.get("purpose", "unknown")
            stats[f"{purpose}_count"] = result.get("record_count", 0)

        return stats
