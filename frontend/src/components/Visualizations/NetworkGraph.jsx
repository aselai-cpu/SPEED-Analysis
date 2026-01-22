import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

const NetworkGraph = ({ data, width = 900, height = 600 }) => {
  const svgRef = useRef();

  useEffect(() => {
    if (!data || !data.nodes || !data.links || data.nodes.length === 0) return;

    // Clear previous
    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    // Create a copy of data to avoid mutating props
    const nodes = data.nodes.map(d => ({ ...d }));
    const links = data.links.map(d => ({ ...d }));

    // Color scale for node types
    const colorScale = d3.scaleOrdinal()
      .domain(['initiator', 'target', 'victim', 'event'])
      .range(['#1976d2', '#dc004e', '#f57c00', '#388e3c']);

    // Create force simulation
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links)
        .id(d => d.id)
        .distance(120))
      .force('charge', d3.forceManyBody().strength(-400))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(35));

    // Create container for zoom
    const g = svg.append('g');

    // Add zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.3, 3])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom);

    // Create links
    const link = g.append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(links)
      .enter()
      .append('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', d => Math.sqrt(d.value || 1) * 2);

    // Create nodes
    const node = g.append('g')
      .attr('class', 'nodes')
      .selectAll('g')
      .data(nodes)
      .enter()
      .append('g')
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));

    node.append('circle')
      .attr('r', d => d.size || 12)
      .attr('fill', d => colorScale(d.type))
      .attr('stroke', '#fff')
      .attr('stroke-width', 2);

    node.append('text')
      .attr('dx', 15)
      .attr('dy', 5)
      .text(d => d.label)
      .style('font-size', '11px')
      .style('font-weight', '500');

    // Tooltip
    const tooltip = d3.select('body')
      .append('div')
      .attr('class', 'tooltip')
      .style('opacity', 0);

    node.on('mouseover', function(event, d) {
      d3.select(this).select('circle')
        .attr('stroke-width', 4);

      tooltip.transition()
        .duration(200)
        .style('opacity', 0.9);

      tooltip.html(`
        <strong>${d.label}</strong><br/>
        Type: ${d.type || 'N/A'}<br/>
        ${d.connections ? `Connections: ${d.connections}` : ''}
      `)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 28) + 'px');
    })
    .on('mouseout', function() {
      d3.select(this).select('circle')
        .attr('stroke-width', 2);

      tooltip.transition()
        .duration(500)
        .style('opacity', 0);
    });

    // Update positions on tick
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      node.attr('transform', d => `translate(${d.x},${d.y})`);
    });

    // Drag functions
    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    // Cleanup
    return () => {
      simulation.stop();
      d3.selectAll('.tooltip').remove();
    };

  }, [data, width, height]);

  return (
    <div className="visualization-container network-graph">
      <svg ref={svgRef}></svg>
    </div>
  );
};

export default NetworkGraph;
