import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

const LineChart = ({ data, width = 900, height = 400 }) => {
  const svgRef = useRef();

  useEffect(() => {
    if (!data || !data.series || data.series.length === 0) return;

    // Clear previous
    d3.select(svgRef.current).selectAll('*').remove();

    const margin = { top: 40, right: 100, bottom: 60, left: 80 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const series = data.series;

    // Scales
    const xScale = d3.scaleLinear()
      .domain(d3.extent(series, d => d.x))
      .range([0, innerWidth])
      .nice();

    const yScale = d3.scaleLinear()
      .domain([0, d3.max(series, d => d.y) || 10])
      .range([innerHeight, 0])
      .nice();

    // Line generator
    const line = d3.line()
      .x(d => xScale(d.x))
      .y(d => yScale(d.y))
      .curve(d3.curveMonotoneX);

    // Axes
    const xAxis = d3.axisBottom(xScale).tickFormat(d3.format('d'));
    const yAxis = d3.axisLeft(yScale);

    g.append('g')
      .attr('class', 'x-axis')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(xAxis)
      .style('font-size', '12px');

    g.append('g')
      .attr('class', 'y-axis')
      .call(yAxis)
      .style('font-size', '12px');

    // Axis labels
    g.append('text')
      .attr('class', 'axis-label')
      .attr('x', innerWidth / 2)
      .attr('y', innerHeight + 45)
      .attr('text-anchor', 'middle')
      .style('font-size', '13px')
      .text('Year');

    g.append('text')
      .attr('class', 'axis-label')
      .attr('transform', 'rotate(-90)')
      .attr('x', -innerHeight / 2)
      .attr('y', -55)
      .attr('text-anchor', 'middle')
      .style('font-size', '13px')
      .text('Event Count');

    // Grid lines
    g.append('g')
      .attr('class', 'grid')
      .attr('opacity', 0.1)
      .call(d3.axisLeft(yScale)
        .tickSize(-innerWidth)
        .tickFormat('')
      );

    // Draw line
    g.append('path')
      .datum(series)
      .attr('class', 'line')
      .attr('fill', 'none')
      .attr('stroke', '#1976d2')
      .attr('stroke-width', 3)
      .attr('d', line);

    // Tooltip
    const tooltip = d3.select('body')
      .append('div')
      .attr('class', 'tooltip')
      .style('opacity', 0);

    // Data points
    g.selectAll('.dot')
      .data(series)
      .enter()
      .append('circle')
      .attr('class', 'dot')
      .attr('cx', d => xScale(d.x))
      .attr('cy', d => yScale(d.y))
      .attr('r', 5)
      .attr('fill', '#1976d2')
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .on('mouseover', function(event, d) {
        d3.select(this)
          .attr('r', 7)
          .attr('fill', '#0d47a1');

        tooltip.transition()
          .duration(200)
          .style('opacity', 0.9);

        tooltip.html(`
          <strong>Year: ${d.x}</strong><br/>
          Events: ${d.y}<br/>
          ${d.violence ? `Violence Level: ${d.violence.toFixed(2)}` : ''}
        `)
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 28) + 'px');
      })
      .on('mouseout', function() {
        d3.select(this)
          .attr('r', 5)
          .attr('fill', '#1976d2');

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
    <div className="visualization-container line-chart">
      <svg ref={svgRef}></svg>
    </div>
  );
};

export default LineChart;
