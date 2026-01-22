"""Service for interacting with Neo4j SPEED Knowledge Graph"""

from neo4j import GraphDatabase
from typing import Dict, List, Any, Optional
import os
import logging

logger = logging.getLogger(__name__)


class Neo4jService:
    """
    Service for interacting with Neo4j SPEED Knowledge Graph
    Handles all database connections and query execution
    """

    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "speedkg123")

        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info(f"Connected to Neo4j at {self.uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            self.driver = None

    async def execute_query(
        self,
        cypher: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict]:
        """
        Execute a Cypher query and return results

        Args:
            cypher: The Cypher query string
            parameters: Query parameters

        Returns:
            List of result records as dictionaries
        """
        if not self.driver:
            raise Exception("Neo4j driver not initialized")

        try:
            logger.info("🗄️  NEO4J QUERY EXECUTION")
            logger.info("-"*60)

            # Log the Cypher query (formatted)
            cypher_preview = cypher[:500] + "..." if len(cypher) > 500 else cypher
            logger.info(f"Cypher Query:\n{cypher_preview}")

            # Log parameters
            if parameters:
                logger.info(f"Parameters: {parameters}")

            logger.info("-"*60)
            logger.info("⏳ Executing query against Neo4j...")

            with self.driver.session() as session:
                result = session.run(cypher, parameters or {})
                records = []

                for record in result:
                    # Convert Neo4j record to dict
                    record_dict = {}
                    for key in record.keys():
                        value = record[key]

                        # Handle Neo4j node/relationship objects
                        if hasattr(value, '__dict__'):
                            # It's a node or relationship
                            if hasattr(value, 'items'):
                                # It's a node
                                record_dict[key] = dict(value.items())
                            else:
                                record_dict[key] = str(value)
                        elif isinstance(value, list):
                            # Handle lists of nodes/relationships
                            record_dict[key] = [
                                dict(item.items()) if hasattr(item, 'items') else item
                                for item in value
                            ]
                        else:
                            record_dict[key] = value

                    records.append(record_dict)

                logger.info("✅ NEO4J QUERY RESULT")
                logger.info("-"*60)
                logger.info(f"Records Returned: {len(records)}")

                # Log sample data (first record if available)
                if records and len(records) > 0:
                    sample = records[0]
                    logger.info(f"Sample Record Keys: {list(sample.keys())}")
                    # Log first few key-value pairs as preview
                    for i, (key, value) in enumerate(list(sample.items())[:3]):
                        value_str = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                        logger.info(f"  {key}: {value_str}")
                    if len(sample) > 3:
                        logger.info(f"  ... and {len(sample) - 3} more fields")

                logger.info("-"*60)

                return records

        except Exception as e:
            logger.error("❌ NEO4J QUERY ERROR")
            logger.error("-"*60)
            logger.error(f"Query: {cypher[:200]}...")
            logger.error(f"Parameters: {parameters}")
            logger.error(f"Error: {str(e)}")
            logger.error("-"*60)
            raise Exception(f"Query execution error: {str(e)}")

    def is_connected(self) -> bool:
        """Check Neo4j connection"""
        if not self.driver:
            return False

        try:
            with self.driver.session() as session:
                session.run("RETURN 1")
            return True
        except:
            return False

    def close(self):
        """Close driver connection"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j driver closed")
