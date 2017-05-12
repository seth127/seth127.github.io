var newStatsWidth = 1000
var newStatsHeight = 390

var spreadX = newStatsWidth/12;
var spreadY = newStatsHeight/3;

//var epochLineScale = (newStatsWidth - spreadX) / maxEpochs

var newStatsDF;
function getNewStatsData(filename, maxEpochs) {
    //d3.csv('plotDataRF/epochStats-long.csv', function(d) {
    //d3.csv('plotData-epochs/epochStats-KDF.csv', function(d) {
    d3.csv(filename, function(d) {
        newStatsDF = d;
        drawNewStats(maxEpochs);
        drawEpochLine(maxEpochs);
    });
}

function drawNewStats(maxEpochs) {
    newStatsSVG = d3.select('#newStats');
    
    newStatsSVG.selectAll("circle").remove()
    newStatsSVG.selectAll("line").remove()
    
    console.log('maxEpochs: ' + maxEpochs)

    var circle = newStatsSVG.selectAll("circle")
        .data(newStatsDF.filter(function(d) { return /En|Re|Fa/.test(d.variable) }))
        .enter().append("circle")
            .attr ("cx",function(d) { return d.labels * spreadX; })
            .attr ("cy",function(d) { 
                    if (d.variable.includes("wolf")) {
                        return spreadY;
                    } else if (d.variable.includes("rabbit")) {
                        return spreadY*2;
                    } 
                })
            .attr ("opacity",function(d) { 
                    if (d.variable.includes("Re")) {
                        return 0.2;
                    } else {
                        return 1;
                    } 
                })
            .attr ("stroke-width", 1.5)
            .attr ("stroke", '#ccc')
            .attr ("r",function(d) { return d.value / 6.5; })
            .attr("fill",function(d) { 
                    if (d.variable.includes("grass")) {
                        return "green";
                    } else if (d.variable.includes("wolf")) {
                        return "purple";
                    } else if (d.variable.includes("rabbit")) {
                        return "blue";
                    } else {
                        return "gray";
                    }
                });

    var line = newStatsSVG.selectAll("line")
        .data(newStatsDF.filter(function(d) { return d.variable.includes("Num") }))
        .enter().append("line")
            .attr ("stroke-width", 3)
            .attr ("x1",function(d) { 
                    if (d.variable.includes("grass")) {
                        return (d.labels * spreadX) - 1.75 + spreadX/2;
                    } else if (d.variable.includes("wolf")) {
                        return (d.labels * spreadX) + 5.5 + spreadX/2;
                    } else if (d.variable.includes("rabbit")) {
                        return (d.labels * spreadX) + 1.75 + spreadX/2;
                    } else {
                        return d.labels * spreadX - 5.5 + spreadX/2;
                    }
                })
            .attr ("x2",function(d) { 
                    if (d.variable.includes("grass")) {
                        return (d.labels * spreadX) - 1.75 + spreadX/2;
                    } else if (d.variable.includes("wolf")) {
                        return (d.labels * spreadX) + 5.5 + spreadX/2;
                    } else if (d.variable.includes("rabbit")) {
                        return (d.labels * spreadX) + 1.75 + spreadX/2;
                    } else {
                        return d.labels * spreadX - 5.5 + spreadX/2;
                    }
                })
            .attr ("y1",function(d) { return spreadY*1.5 - d.value;})
            .attr ("y2",function(d) { return spreadY*1.5 + d.value/1;})
            .attr("stroke",function(d) { 
                    if (d.variable.includes("grass")) {
                        return "green";
                    } else if (d.variable.includes("wolf")) {
                        return "purple";
                    } else if (d.variable.includes("rabbit")) {
                        return "blue";
                    } else {
                        return "gray";
                    }
                });

    
}

function drawEpochLine(maxEpochs) {
    var epochLineScale = (newStatsWidth - spreadX) / maxEpochs
    
    newStatsSVG = d3.select('#newStats');
    newStatsSVG.select("#epochLine").remove();
    newStatsSVG.select("#deadWorldArea").remove();
    newStatsSVG.selectAll("text").remove();

    // line to show which epoch we're on
    newStatsSVG.append("line")
        .attr("id", "epochLine")
        .attr("stroke", '#a44')
        .attr("opacity", 0.4)
        .attr("stroke-width", 2)
        .attr("x1", spreadX/2 + (epochNum*epochLineScale))
        .attr("x2", spreadX/2 + (epochNum*epochLineScale))
        .attr("y1", 10)
        .attr("y2", 365)
    
    // make deadWorld area chart
    var area = d3.area()
        .x(function(d) { return d.labels * spreadX * 1.1 - (spreadX/2); })
        .y0(newStatsHeight - 17)
        .y1(function(d) { return newStatsHeight - 30 - d.value/(newStatsHeight/40); });
    
    newStatsSVG.append("path")
        .attr("id", "deadWorldArea")
        .datum(newStatsDF.filter(function(d) { return d.variable.includes("deadWorld");} ))
        .attr("fill", "steelblue")
        .attr("opacity", 0.4)
        .attr("d", area);
    
    // deadWorld ticks marks
    var text = newStatsSVG.selectAll("text")
        .data(newStatsDF.filter(function(d) { return d.variable.includes("deadWorld") }))
        .enter().append("text")
            .attr("font-size", 10)
            .attr('x', function(d) { return d.labels * spreadX; })
            .attr('y', newStatsHeight - 5)
            .text(function(d) { return parseInt(d.value); });
    
    // deadWorld label
    newStatsSVG.append("text")
        .attr("font-size", 10)
        .attr('x', 10)
        .attr('y', newStatsHeight - 36)
        .text("Avg.");
    newStatsSVG.append("text")
        .attr("font-size", 10)
        .attr('x', 10)
        .attr('y', newStatsHeight - 24)
        .text("Years of");
    newStatsSVG.append("text")
        .attr("font-size", 10)
        .attr('x', 10)
        .attr('y', newStatsHeight - 12)
        .text("Survival");
    
    newStatsSVG.append("text")
        .attr("font-size", 20)
        .attr('x', (newStatsWidth/2) - 100 )
        .attr('y', 30)
        .text(modelChoice);
    

}