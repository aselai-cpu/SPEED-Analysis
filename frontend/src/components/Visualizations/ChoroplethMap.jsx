import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

/**
 * Simplified Choropleth Map Component
 *
 * For a full implementation with actual geographic boundaries,
 * you would need to:
 * 1. Import GeoJSON data for world/regional boundaries
 * 2. Use d3.geoPath() with a projection
 * 3. Match data to geographic features
 *
 * This implementation shows a proportional symbol map as a fallback
 * that displays data with geographic context using circles sized by value.
 */
const ChoroplethMap = ({ data, width = 900, height = 600 }) => {
  const svgRef = useRef();

  useEffect(() => {
    if (!data || !data.regions || data.regions.length === 0) return;

    // Clear previous
    d3.select(svgRef.current).selectAll('*').remove();

    const margin = { top: 40, right: 120, bottom: 60, left: 60 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const regions = data.regions;

    // Since we don't have actual map data, we'll create a grid layout
    // showing countries/regions as sized circles (proportional symbol map)

    // Calculate grid dimensions
    const numRegions = regions.length;
    const cols = Math.ceil(Math.sqrt(numRegions));
    const rows = Math.ceil(numRegions / cols);

    const cellWidth = innerWidth / cols;
    const cellHeight = innerHeight / rows;

    // Add position to each region
    const regionsWithPos = regions.map((d, i) => ({
      ...d,
      col: i % cols,
      row: Math.floor(i / cols),
      cx: (i % cols + 0.5) * cellWidth,
      cy: (Math.floor(i / cols) + 0.5) * cellHeight
    }));

    // Scales
    const maxValue = d3.max(regions, d => d.value) || 1;
    const radiusScale = d3.scaleSqrt()
      .domain([0, maxValue])
      .range([5, Math.min(cellWidth, cellHeight) / 2.5]);

    const colorScale = d3.scaleSequential()
      .domain([0, maxValue])
      .interpolator(d3.interpolateYlOrRd);

    // Title
    svg.append('text')
      .attr('class', 'map-title')
      .attr('x', width / 2)
      .attr('y', 25)
      .attr('text-anchor', 'middle')
      .style('font-size', '16px')
      .style('font-weight', 'bold')
      .text('Geographic Distribution');

    // Tooltip
    const tooltip = d3.select('body')
      .append('div')
      .attr('class', 'tooltip')
      .style('opacity', 0);

    // Draw circles for regions
    g.selectAll('.region-circle')
      .data(regionsWithPos)
      .enter()
      .append('circle')
      .attr('class', 'region-circle')
      .attr('cx', d => d.cx)
      .attr('cy', d => d.cy)
      .attr('r', d => radiusScale(d.value))
      .attr('fill', d => colorScale(d.value))
      .attr('stroke', '#333')
      .attr('stroke-width', 1.5)
      .attr('opacity', 0.8)
      .on('mouseover', function(event, d) {
        d3.select(this)
          .attr('opacity', 1)
          .attr('stroke-width', 2.5);

        tooltip.transition()
          .duration(200)
          .style('opacity', 0.9);

        tooltip.html(`
          <strong>${d.location}</strong><br/>
          Events: ${d.value}<br/>
          ${d.casualties ? `Casualties: ${d.casualties}` : ''}<br/>
          ${d.avg_intensity ? `Avg Intensity: ${d.avg_intensity.toFixed(2)}` : ''}
        `)
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 28) + 'px');
      })
      .on('mouseout', function() {
        d3.select(this)
          .attr('opacity', 0.8)
          .attr('stroke-width', 1.5);

        tooltip.transition()
          .duration(500)
          .style('opacity', 0);
      });

    // Labels for regions
    g.selectAll('.region-label')
      .data(regionsWithPos)
      .enter()
      .append('text')
      .attr('class', 'region-label')
      .attr('x', d => d.cx)
      .attr('y', d => d.cy + radiusScale(d.value) + 15)
      .attr('text-anchor', 'middle')
      .style('font-size', '10px')
      .style('font-weight', 'bold')
      .text(d => d.location);

    // Color legend
    const legendWidth = 20;
    const legendHeight = 150;

    const legendScale = d3.scaleLinear()
      .domain([0, maxValue])
      .range([legendHeight, 0]);

    const legendAxis = d3.axisRight(legendScale)
      .ticks(5);

    const legend = svg.append('g')
      .attr('class', 'legend')
      .attr('transform', `translate(${width - margin.right + 20},${margin.top + 50})`);

    // Create gradient
    const defs = svg.append('defs');
    const linearGradient = defs.append('linearGradient')
      .attr('id', 'choropleth-gradient')
      .attr('x1', '0%')
      .attr('y1', '100%')
      .attr('x2', '0%')
      .attr('y2', '0%');

    linearGradient.selectAll('stop')
      .data(d3.range(0, 1.1, 0.1))
      .enter()
      .append('stop')
      .attr('offset', d => `${d * 100}%`)
      .attr('stop-color', d => colorScale(d * maxValue));

    legend.append('rect')
      .attr('width', legendWidth)
      .attr('height', legendHeight)
      .style('fill', 'url(#choropleth-gradient)');

    legend.append('g')
      .attr('transform', `translate(${legendWidth}, 0)`)
      .call(legendAxis);

    legend.append('text')
      .attr('x', legendWidth / 2)
      .attr('y', -10)
      .attr('text-anchor', 'middle')
      .style('font-size', '11px')
      .text('Events');

    // Add note about proportional symbols
    svg.append('text')
      .attr('x', margin.left)
      .attr('y', height - 10)
      .style('font-size', '10px')
      .style('font-style', 'italic')
      .style('fill', '#666')
      .text('Circle size represents event count');

    // Cleanup
    return () => {
      d3.selectAll('.tooltip').remove();
    };

  }, [data, width, height]);

  return (
    <div className="visualization-container choropleth-map">
      <svg ref={svgRef}></svg>
      <div style={{
        fontSize: '11px',
        color: '#666',
        marginTop: '10px',
        fontStyle: 'italic'
      }}>
        Note: This is a proportional symbol representation. For actual geographic boundaries,
        GeoJSON map data would be required.
      </div>
    </div>
  );
};

export default ChoroplethMap;
