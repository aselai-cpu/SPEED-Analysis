import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

const ForceDirectedGraph = ({ data, width = 900, height = 600 }) => {
  const svgRef = useRef();

  useEffect(() => {
    if (!data || !data.nodes || !data.links) return;
    if (data.nodes.length === 0) return;

    // Clear previous
    d3.select(svgRef.current).selectAll('*').remove();

    const margin = { top: 20, right: 20, bottom: 20, left: 20 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Deep copy to avoid mutating original data
    const nodes = data.nodes.map(d => ({ ...d }));
    const links = data.links.map(d => ({ ...d }));

    // Color scale by node type
    const nodeTypes = [...new Set(nodes.map(d => d.type))];
    const colorScale = d3.scaleOrdinal()
      .domain(nodeTypes)
      .range(d3.schemeCategory10);

    // Create force simulation
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links)
        .id(d => d.id)
        .distance(100)
      )
      .force('charge', d3.forceManyBody()
        .strength(-300)
      )
      .force('center', d3.forceCenter(innerWidth / 2, innerHeight / 2))
      .force('collision', d3.forceCollide()
        .radius(d => (d.size || 10) + 5)
      );

    // Tooltip
    const tooltip = d3.select('body')
      .append('div')
      .attr('class', 'tooltip')
      .style('opacity', 0);

    // Draw links
    const link = g.append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(links)
      .enter()
      .append('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', d => Math.sqrt(d.value || 1));

    // Draw nodes
    const node = g.append('g')
      .attr('class', 'nodes')
      .selectAll('circle')
      .data(nodes)
      .enter()
      .append('circle')
      .attr('r', d => d.size || 10)
      .attr('fill', d => colorScale(d.type))
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .on('mouseover', function(event, d) {
        d3.select(this)
          .attr('stroke', '#333')
          .attr('stroke-width', 3);

        tooltip.transition()
          .duration(200)
          .style('opacity', 0.9);

        tooltip.html(`
          <strong>${d.label || d.id}</strong><br/>
          Type: ${d.type}<br/>
          ${d.size ? `Size: ${d.size}` : ''}
        `)
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 28) + 'px');
      })
      .on('mouseout', function() {
        d3.select(this)
          .attr('stroke', '#fff')
          .attr('stroke-width', 2);

        tooltip.transition()
          .duration(500)
          .style('opacity', 0);
      })
      .call(d3.drag()
        .on('start', dragStarted)
        .on('drag', dragged)
        .on('end', dragEnded)
      );

    // Add labels
    const label = g.append('g')
      .attr('class', 'labels')
      .selectAll('text')
      .data(nodes)
      .enter()
      .append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', d => (d.size || 10) + 15)
      .style('font-size', '10px')
      .style('font-weight', 'bold')
      .text(d => {
        const text = d.label || d.id;
        return text.length > 20 ? text.substring(0, 17) + '...' : text;
      });

    // Update positions on each tick
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      node
        .attr('cx', d => {
          // Keep nodes within bounds
          d.x = Math.max(d.size || 10, Math.min(innerWidth - (d.size || 10), d.x));
          return d.x;
        })
        .attr('cy', d => {
          d.y = Math.max(d.size || 10, Math.min(innerHeight - (d.size || 10), d.y));
          return d.y;
        });

      label
        .attr('x', d => d.x)
        .attr('y', d => d.y);
    });

    // Drag functions
    function dragStarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragEnded(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    // Legend for node types
    const legend = svg.append('g')
      .attr('class', 'legend')
      .attr('transform', `translate(${width - 150}, 30)`);

    legend.append('text')
      .attr('x', 0)
      .attr('y', 0)
      .style('font-size', '12px')
      .style('font-weight', 'bold')
      .text('Node Types:');

    nodeTypes.forEach((type, i) => {
      const legendRow = legend.append('g')
        .attr('transform', `translate(0, ${20 + i * 20})`);

      legendRow.append('circle')
        .attr('cx', 10)
        .attr('cy', 0)
        .attr('r', 6)
        .attr('fill', colorScale(type))
        .attr('stroke', '#fff')
        .attr('stroke-width', 1);

      legendRow.append('text')
        .attr('x', 25)
        .attr('y', 4)
        .style('font-size', '11px')
        .text(type);
    });

    // Cleanup
    return () => {
      simulation.stop();
      d3.selectAll('.tooltip').remove();
    };

  }, [data, width, height]);

  return (
    <div className="visualization-container force-directed-graph">
      <svg ref={svgRef}></svg>
      <div style={{
        fontSize: '11px',
        color: '#666',
        marginTop: '10px',
        fontStyle: 'italic'
      }}>
        Drag nodes to reposition. Physics simulation will stabilize automatically.
      </div>
    </div>
  );
};

export default ForceDirectedGraph;
