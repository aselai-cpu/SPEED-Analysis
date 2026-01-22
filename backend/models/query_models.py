"""Pydantic models for query requests and responses"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class QueryRequest(BaseModel):
    """Request model for natural language queries"""
    query: str = Field(..., description="Natural language query from user")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Optional context")


class VisualizationSpec(BaseModel):
    """Specification for a visualization"""
    id: str = Field(..., description="Unique visualization ID")
    type: str = Field(..., description="Type of visualization (timeline, network_graph, etc.)")
    title: Optional[str] = Field(None, description="Title for the visualization")
    spec: Dict[str, Any] = Field(default_factory=dict, description="D3.js spec")
    data: Dict[str, Any] = Field(..., description="Data for the visualization")


class ResponseContent(BaseModel):
    """Content of the response"""
    text: str = Field(..., description="Markdown-formatted text analysis")
    visualizations: List[VisualizationSpec] = Field(default_factory=list, description="List of visualizations")


class ResponseMetadata(BaseModel):
    """Metadata about the response"""
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    data_points: int = Field(0, description="Number of data points retrieved")
    visualizations_count: int = Field(0, description="Number of visualizations")
    confidence: Optional[float] = Field(None, description="Confidence score")


class QueryResponse(BaseModel):
    """Response model for queries"""
    message_id: str = Field(..., description="Unique message ID")
    response_type: str = Field(default="analysis", description="Type of response")
    content: ResponseContent = Field(..., description="Response content")
    metadata: ResponseMetadata = Field(..., description="Response metadata")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class ExecutionPlan(BaseModel):
    """Plan created by Planning Agent"""
    query_intent: str
    research_questions: List[str]
    cypher_queries: List[Dict[str, Any]]
    visualizations: List[Dict[str, Any]]
    text_sections: List[str]
