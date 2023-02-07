document.getElementById("name").innerText = "Wenbo Tong";
document.getElementById("assignment_number").innerText = "3";
/////////////////////////////////////////////////////
import * as d3 from "d3";

document.getElementById("paraselect")
    .addEventListener("change", getData)

d3.json("./data/genres_average_playtime_3_hierarchy.json")
.then(function (data){
    console.log(data);
    init(data);
});

// this function enables interaction
function getData(){
    var index = document.getElementById("paraselect").selectedIndex;
    // console.log(index)

    if (index == 0)
    {
        d3.json("./data/genres_average_playtime_3_hierarchy.json")
        .then(function (data){       // asynchronous programming
            d3.select("#mysvg").remove()
            init(data);
        });
    }
    else if (index == 1)
    {
        d3.json("./data/genres_median_playtime_3_hierarchy.json")
        .then(function (data){
            d3.select("#mysvg").remove()
            init(data);
        });
    }
    else if (index == 2)
    {
        d3.json("./data/genres_positive_ratings_3_hierarchy.json")
        .then(function (data){
            d3.select("#mysvg").remove()
            init(data);
        });
    }
}

// partition the data
function partition(data){
    const root = d3.hierarchy(data)
        .sum(d => d.value)
        .sort((a, b) => b.value - a.value);
    // partition assign the properties x0 y0 x1 y1 to the root and its descendants
    return d3.partition()
        .size([2 * Math.PI, root.height + 1])   // set the partition size to [], in this case, it is a 2-round donut
        //.size([2 * Math.PI, root.height + 2])  // this is 1-round donut
    (root);
}

function init(data) {
    const color = d3.scaleOrdinal(d3.schemeCategory10);
    var width = window.innerWidth * 0.6;
    const radius = width / 6;
    const root = partition(data);
    console.log(root)
    root.each(d => d.current = d);

    const svg = d3.select("#map_container").append("svg").attr("id", "mysvg")
        .attr("width", window.innerWidth)
        .attr("height", width)
        .attr("viewBox", [0, 0, width, width])
        .style("font", "10px sans-serif");
        
    // set the svg to the middle of the screen
    const g = svg.append("g")
        .attr("transform", `translate(${width / 2},${width / 2})`);

    const arc = d3.arc()
        .startAngle(d => d.x0)
        // @ts-ignore
        .endAngle(d => d.x1)
        .padAngle(d => Math.min((d.x1 - d.x0) / 2, 0.005))
        .padRadius(radius * 1.5)
        .innerRadius(d => d.y0 * radius)
        .outerRadius(d => Math.max(d.y0 * radius, d.y1 * radius - 1))

    const path = g.append("g")
    .selectAll("path")
    .data(root.descendants().slice(1))   
    // root.descendants() returns an array of every descendant nodes(including nodes and leaves) of the given node
    .join("path")
        .attr("fill", d => { while (d.depth > 1) d = d.parent; return color(d.data.name); })
        .attr("fill-opacity", d => arcVisible(d.current) ? (d.children ? 0.6 : 0.4) : 0)
        .attr("d", d => arc(d.current))
        .style("cursor", "pointer")
        .on("click", clicked);

    // add tooltip when mouse on the section
    path.append("title")
        .text(d => `${d.ancestors().map(d => d.data.name).reverse().join("/")}\n${d.value}`);
    
    // add label for each section
    const label = g.append("g")
        .attr("text-anchor", "middle")
    .selectAll("text")
    .data(root.descendants().slice(1))
    .join("text")
        .attr("dy", "0.35em")
        .attr("fill-opacity", d => +labelVisible(d.current))  // only the labels on the current donut are visible
        .attr("transform", d => labelTransform(d.current))
        .text(d => d.data.name);
    
    // click in the middle to return to parent donut
    const parent = g.append("circle")
        .datum(root)
        .attr("r", radius)
        .attr("fill", "none")
        .attr("pointer-events", "all")
        .on("click", clicked);

    function clicked(event, p) {
      parent.datum(p.parent);

      root.each(d => d.target = {
        x0: Math.max(0, Math.min(1, (d.x0 - p.x0) / (p.x1 - p.x0))) * 2 * Math.PI,
        x1: Math.max(0, Math.min(1, (d.x1 - p.x0) / (p.x1 - p.x0))) * 2 * Math.PI,
        y0: Math.max(0, d.y0 - p.depth),
        y1: Math.max(0, d.y1 - p.depth)
    });

    // transition allows the smooth animation between two charts, duration is the time of transition in ms
    const t = g.transition().duration(800);

    // transition of the data on all arcs
    path.transition(t)
        .tween("data", d => {
            const i = d3.interpolate(d.current, d.target);
            return t => d.current = i(t);
        })
        .filter(function(d) {
        return +this.getAttribute("fill-opacity") || arcVisible(d.target);
        })
        .attr("fill-opacity", d => arcVisible(d.target) ? (d.children ? 0.6 : 0.4) : 0)
        .attrTween("d", d => () => arc(d.current));

    label.filter(function(d) {
        return +this.getAttribute("fill-opacity") || labelVisible(d.target);
        }).transition(t)
        .attr("fill-opacity", d => +labelVisible(d.target))
        .attrTween("transform", d => () => labelTransform(d.current));
    }
    
    // set only the arc on current donut is visible including parent arc
    function arcVisible(d) {
    return d.y1 <= 3 && d.x1 > d.x0;
    }

    // set only labels on the current arc are visible including parent label
    function labelVisible(d) {
    return d.y1 <= 3 && (d.y1 - d.y0) * (d.x1 - d.x0) > 0.01;
    }
    
    // transform the label for each arch
    // if it is the center (parent lable), do not transform
    function labelTransform(d) {
    const x = (d.x0 + d.x1) / 2 * 180 / Math.PI;
    const y = (d.y0 + d.y1) / 2 * radius;
    if (d.y0 >= 0.01){
        return `rotate(${x - 90}) translate(${y},0) rotate(${x < 180 ? 0 : 180})`;
    }
    }
}
