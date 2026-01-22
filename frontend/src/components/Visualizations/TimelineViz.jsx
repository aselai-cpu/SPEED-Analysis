import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

const TimelineViz = ({ data, width = 900, height = 400 }) => {
  const svgRef = useRef();

  useEffect(() => {
    if (!data || !data.events || data.events.length === 0) return;

    // Clear previous content
    d3.select(svgRef.current).selectAll('*').remove();

    const margin = { top: 40, right: 30, bottom: 60, left: 60 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    // Create SVG
    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Parse dates and prepare data
    const events = data.events.map(e => ({
      ...e,
      date: new Date(e.date),
      value: e.value || 0,
      intensity: e.intensity || 0
    }));

    // Scales
    const xScale = d3.scaleTime()
      .domain(d3.extent(events, d => d.date))
      .range([0, innerWidth]);

    const yScale = d3.scaleLinear()
      .domain([0, d3.max(events, d => Math.max(d.value, d.intensity)) || 10])
      .range([innerHeight, 0])
      .nice();

    const colorScale = d3.scaleSequential()
      .domain([0, d3.max(events, d => d.intensity) || 10])
      .interpolator(d3.interpolateYlOrRd);

    // Axes
    const xAxis = d3.axisBottom(xScale)
      .ticks(8)
      .tickFormat(d3.timeFormat('%b %Y'));

    const yAxis = d3.axisLeft(yScale)
      .ticks(6);

    g.append('g')
      .attr('class', 'x-axis')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(xAxis)
      .selectAll('text')
      .attr('transform', 'rotate(-45)')
      .style('text-anchor', 'end');

    g.append('g')
      .attr('class', 'y-axis')
      .call(yAxis);

    // Axis labels
    g.append('text')
      .attr('class', 'axis-label')
      .attr('x', innerWidth / 2)
      .attr('y', innerHeight + 50)
      .attr('text-anchor', 'middle')
      .text('Date');

    g.append('text')
      .attr('class', 'axis-label')
      .attr('transform', 'rotate(-90)')
      .attr('x', -innerHeight / 2)
      .attr('y', -45)
      .attr('text-anchor', 'middle')
      .text('Event Count / Intensity');

    // Line for event count
    const line = d3.line()
      .x(d => xScale(d.date))
      .y(d => yScale(d.value))
      .curve(d3.curveMonotoneX);

    g.append('path')
      .datum(events)
      .attr('fill', 'none')
      .attr('stroke', '#1976d2')
      .attr('stroke-width', 2)
      .attr('d', line);

    // Tooltip
    const tooltip = d3.select('body')
      .append('div')
      .attr('class', 'tooltip')
      .style('opacity', 0);

    // Events as circles
    g.selectAll('.event-circle')
      .data(events)
      .enter()
      .append('circle')
      .attr('class', 'event-circle')
      .attr('cx', d => xScale(d.date))
      .attr('cy', d => yScale(d.value))
      .attr('r', 5)
      .attr('fill', d => colorScale(d.intensity))
      .attr('stroke', '#333')
      .attr('stroke-width', 1)
      .on('mouseover', function(event, d) {
        d3.select(this)
          .attr('r', 8)
          .attr('stroke-width', 2);

        tooltip.transition()
          .duration(200)
          .style('opacity', 0.9);

        tooltip.html(`
          <strong>${d.label || d3.timeFormat('%Y-%m-%d')(d.date)}</strong><br/>
          Events: ${d.value}<br/>
          Intensity: ${d.intensity.toFixed(2)}<br/>
          ${d.casualties ? `Casualties: ${d.casualties}` : ''}
        `)
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 28) + 'px');
      })
      .on('mouseout', function() {
        d3.select(this)
          .attr('r', 5)
          .attr('stroke-width', 1);

        tooltip.transition()
          .duration(500)
          .style('opacity', 0);
      });

    // Cleanup
    return () => {
      d3.selectAll('.tooltip').remove();
    };

  }, [data, width, height]);

  return (
    <div className="visualization-container timeline-viz">
      <svg ref={svgRef}></svg>
    </div>
  );
};

export default TimelineViz;
