let formatDate = d3.timeFormat("%Y-%m-%d %H:%M:%S");

let parseTime = d3.timeParse("%a, %d %b %Y %H:%M:%S GMT");
let parseTime2 = d3.timeParse("%Y-%m-%d %H:%M:%S.%L");
let parseTime3 = d3.timeParse("%Y-%m-%d %H:%M:%S");

let selectedDataAggregationInput = "daily";

let xScaleMultiline, yScaleMultiline;
                    
let colorScheme = {
    temperature: "rgba(220, 20, 60, 0.99)",
    pH: "rgba(34, 139, 34, 0.99)",
    oxygen: "rgba(0, 191, 255, 0.99)",
    pressure: "rgba(218, 165, 32, 0.99)",
}

let filters = {
    startTime: parseTime2("2023-04-19 05:05:03.964"),
    endTime: parseTime2("2023-04-19 05:59:59.313"),
    data: {
        "daily": {temperature: temperatureData, pH: pHData, oxygen: oxygenData, pressure: pressureData },
        "15min": {temperature: temperatureData15Min, pH: pHData15Min, oxygen: oxygenData15Min, pressure: pressureData15Min },
        "30min": {temperature: temperatureData30Min, pH: pHData30Min, oxygen: oxygenData30Min, pressure: pressureData30Min },
    },
    selectedType: {
        "temperature": true, "pH": true, "oxygen": true, "pressure": true
    }
}

let brush = null;

drawAggregateChart();
plotSubGraphs();


function handleLegendClick(legendNumber) {
  const legendItem = document.querySelector(`.legend-circle-${legendNumber}`);
  
  // Log the class name
    let r = legendItem.style.backgroundColor.split(")")[0].split("rgba(")[1].split(",")[0]
    let g = legendItem.style.backgroundColor.split(")")[0].split("rgba(")[1].split(",")[1]
    let b = legendItem.style.backgroundColor.split(")")[0].split("rgba(")[1].split(",")[2]
    let a = legendItem.style.backgroundColor.split(")")[0].split("rgba(")[1].split(",")[3]
  // Change background color to white
    if (a === " 0.99") {
        legendItem.style.backgroundColor = `rgba(${r},${g},${b},${0})`
    } else {
        legendItem.style.backgroundColor = `rgba(${r},${g},${b},${0.99})`
    }
    
    filters.selectedType[legendItem.className.split(" ")[2]] = !filters.selectedType[legendItem.className.split(" ")[2]];

    drawAggregateChart(true);
    plotSubGraphs();
}



function plotSubGraphs() {
    let dataAggregationInput = document.getElementById("seedSelect");
    selectedDataAggregationInput = String(dataAggregationInput.selectedOptions[0].value)

    drawTemperatureChart();
    drawPHChart();
    drawOxygenChart();
    drawPressureChart();
}

function standardizeTimeSeriesData(data, applyFilter=false) {
    data = data.map(function (d) {
        let dt = parseTime(d[0])
        let val = +d[1];
        if (applyFilter) {
            if ((filters.startTime <= dt) && (dt <= filters.endTime)) {
                return { date: dt, value: val };
            }  
        } else {
            return {date: dt, value: val};
        }
        
    });
    data = data.filter(item => item !== undefined);
    return data
}

function drawAggregateChart(updateOnly=false) {
    let multilineSvg = d3.select("#multilineSvg")
    data1 = standardizeTimeSeriesData(normalizedTemperatureData);
    data2 = standardizeTimeSeriesData(normalizedPHData);
    data3 = standardizeTimeSeriesData(normalizedOxygenData);
    data4 = standardizeTimeSeriesData(normalizedPressureData);

    if(updateOnly){
        renderMultilineData(multilineSvg, data1, data2, data3, data4)
    }else{
        drawMultiLineChart(data1, data2, data3, data4, multilineSvg)
    }


}   


function drawTemperatureChart() {
    let temperatureDataSvg = d3.select("#temperatureDataSvg");
    transformedData = standardizeTimeSeriesData(filters.data[selectedDataAggregationInput].temperature, true);
    drawLineChart(transformedData, temperatureDataSvg, colorScheme.temperature, filters.selectedType.temperature)
}

function drawPHChart() {
    let pHDataSvg = d3.select("#pHDataSvg");
    transformedData = standardizeTimeSeriesData(filters.data[selectedDataAggregationInput].pH, true);
    drawLineChart(transformedData, pHDataSvg, colorScheme.pH, filters.selectedType.pH)
}

function drawOxygenChart() {
    let oxygenDataSvg = d3.select("#oxygenDataSvg");
    transformedData = standardizeTimeSeriesData(filters.data[selectedDataAggregationInput].oxygen, true);
    drawLineChart(transformedData, oxygenDataSvg, colorScheme.oxygen, filters.selectedType.oxygen)
}

function drawPressureChart() {
    let pressureDataSvg = d3.select("#pressureDataSvg");
    transformedData = standardizeTimeSeriesData(filters.data[selectedDataAggregationInput].pressure, true);
    drawLineChart(transformedData, pressureDataSvg, colorScheme.pressure, filters.selectedType.pressure)
}

function drawLineChart(transformedData, svg, lineColor, isActive) {
    if (!isActive) {
        transformedData = [];
    }

    svg.selectAll("g").remove();

    // Set the dimensions and margins of the graph
    let margin = { top: 20, right: 20, bottom: 30, left: 0 }
    width = svg.style('width').replace('px','')-100;
    height = svg.style('height').replace('px', '')-70;

    // Create scales
     let x = d3.scaleTime()
        .domain(d3.extent(transformedData, function(d) { return d.date; }))
        .range([ 0, width ]);
    let y = d3.scaleLinear()
        .domain([d3.min(transformedData, function(d) { return +d.value; }), d3.max(transformedData, function(d) { return +d.value; })])
        .range([height, 0]);
    
    svg.append("g")
        // .transition()
        .attr("transform", `translate(${margin.left},${height})`)
        .call(d3.axisBottom(x));

    svg.append("g")
        // .transition()
        .attr("transform", `translate(${margin.left},0)`)
        .call(d3.axisLeft(y));

    // Add the line
     svg
        .selectAll(".line")
        .data([transformedData])
        .join("path")
        .transition()
        .attr("class", "line")
        .attr("fill", "none")
        .attr("stroke", lineColor)
        .attr("stroke-width", 1)
        .attr("d", d3.line()
        .x(function(d) { return margin.left+x(d.date) })
        .y(function(d) { return y(d.value) })
    )

    // Create a tooltip
    let tooltip = d3.select("body")
        .append("div")
        .attr("class", "tooltip")
        .style("opacity", 0)
        .style("position", "absolute")
        .style("text-align", "center")
        .style("padding", "8px")
        .style("font", "12px sans-serif")
        .style("background", "lightsteelblue")
        .style("border", "0px")
        .style("border-radius", "8px")
        .style("pointer-events", "none");

    // Create crosshair lines
    let crosshairX = svg.append("line")
        .attr("class", "crosshair")
        .style("stroke", "gray")
        .style("stroke-dasharray", "3,3")
        .style("opacity", 0)
        .attr("y1", 0)
        .attr("y2", height);

    let crosshairY = svg.append("line")
        .attr("class", "crosshair")
        .style("stroke", "gray")
        .style("stroke-dasharray", "3,3")
        .style("opacity", 0)
        .attr("x1", 0)
        .attr("x2", width);

    // Add an overlay for the mouseover event
    svg.append("rect")
        .attr("class", "overlay")
        .attr("width", width)
        .attr("height", height)
        .attr("transform", `translate(${margin.left},${margin.top})`)
        .style("fill", "none")
        .style("pointer-events", "all")
        .on("mouseover", function() { tooltip.style("display", null); crosshairX.style("opacity", 1); crosshairY.style("opacity", 1); })
        .on("mouseout", function() { tooltip.style("display", "none"); crosshairX.style("opacity", 0); crosshairY.style("opacity", 0); })
        .on("mousemove", mousemove);

    // Mousemove function
    function mousemove(event) {
        let mouseX = d3.pointer(event, this)[0];
        let x0 = x.invert(mouseX),
            i = d3.bisector(function(d) { return d.date; }).left(transformedData, x0, 1),
            d0 = transformedData[i - 1],
            d1 = transformedData[i],
            d = x0 - d0.date > d1.date - x0 ? d1 : d0;

        tooltip
            .style("opacity", .9)
            .html("Value: " + d.value + "<br/>Date: " + d.date)
            .style("left", (event.pageX + 5) + "px")
            .style("top", (event.pageY - 28) + "px");

        crosshairX
            .attr("transform", `translate(${margin.left + x(d.date)},${margin.top})`);
        crosshairY
            .attr("transform", `translate(${margin.left},${y(d.value)})`);
    }
}


// multilineSvg
function drawMultiLineChart(data1, data2, data3, data4, svg) {
    // Set the dimensions and margins of the graph
    let margin = { top: 20, right: 20, bottom: 30, left: 0 }

    width = svg.style('width').replace('px','')-100;
    height = svg.style('height').replace('px', '')-70;
    
    
    xScaleMultiline = d3.scaleTime()
        .domain(d3.extent(data1, function(d) { return d.date; }))
        .range([ 0, width+margin.left ]);
    yScaleMultiline = d3.scaleLinear()
        .domain([0, 1])
        .range([height, 0]);
    
    svg.append("g")
        .attr("transform", `translate(${margin.left},${height})`)
        .call(d3.axisBottom(xScaleMultiline));

    svg.append("g")
        .attr("transform", `translate(${margin.left},0)`)
        .call(d3.axisLeft(yScaleMultiline));

    renderMultilineData(svg, data1, data2, data3, data4)

    // Brush setup
    brush = d3.brushX()
    .extent([[margin.left, -10], [width, height]])
        .on("end", brushEnded);
    
    brush = d3.brushX()
    .extent([[margin.left, -10], [width, height]])
    .on("end", brushEnded);

    let brushG = svg.append("g")
    .attr("class", "brush")
    .call(brush);
    brushG.call(brush.move, [margin.left, width+margin.left]);

    function brushEnded(event) {
        if (!event.selection) {
            return;
        }

        let [x0, x1] = event.selection;

        let selectedStartDate = xScaleMultiline.invert(x0);
        let selectedEndDate = xScaleMultiline.invert(x1);

        filters.startTime = parseTime3(formatDate(selectedStartDate))
        filters.endTime = parseTime3(formatDate(selectedEndDate))
        plotSubGraphs();
        
    }
    
}

function renderMultilineData(svg, data1, data2, data3, data4){
    let margin = { top: 20, right: 20, bottom: 30, left: 0 };
    let paddingLeft = 2;
    let types = [["pressure", data4], ["temperature", data1], ["pH", data2], ["oxygen", data3]]

    types.forEach((type, i) => {
        let multiLineData = [];
        if (filters.selectedType[type[0]]){
            multiLineData = [type[1]];
        }
        svg.selectAll(`.${type[0]}Line`)
            .data(multiLineData)
            .join("path")
            .transition()
            .attr("class", `${type[0]}Line`)
            .attr("fill", "none")
            .attr("stroke", colorScheme[type[0]])
            .attr("stroke-width", 1)
            .attr("d", d3.line()
                .x(function(d) { return paddingLeft+margin.left+xScaleMultiline(d.date) })
                .y(function(d) { return yScaleMultiline(d.value) })
            )
    })

}
