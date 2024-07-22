function generate2DNormalDistribution(mean, sigma, numPoints) {
    let points = [];

    for (let i = 0; i < numPoints; i++) {
        // Generate two uniform random numbers
        let u1 = Math.random();
        let u2 = Math.random();

        // Box-Muller transform
        let z0 = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
        let z1 = Math.sqrt(-2.0 * Math.log(u1)) * Math.sin(2.0 * Math.PI * u2);

        // Scale and shift by mean and standard deviation (sigma)
        let x = mean + sigma * z0;
        let y = mean + sigma * z1;

        points.push([x, y]);
    }

    return points;
}

console.log('!!!')
var myPlot = document.getElementById('myDiv'),
    hoverInfo = document.getElementById('hoverinfo'),
    /*
    d3 = Plotly.d3,
    N = 16,
    x = d3.range(N),
    y1 = d3.range(N).map( d3.random.normal() ),
    y2 = d3.range(N).map( d3.random.normal() ),
    */
    let mean = 0;       // Mean of the distribution
    let sigma = 1;      // Standard deviation
    let numPoints = 100; // Number of points to generate
    let dataPoints = generate2DNormalDistribution(mean, sigma, numPoints);
    let x = dataPoints.map(point => point[0]);
    let y = dataPoints.map(point => point[1]);
    console.log(x)

    data = [ { x:x, y:y1, type:'scatter', name:'Trial 1',
        mode:'markers', marker:{size:16} }];
    layout = { 
        hovermode:'closest',
        title:'Hover on Points',
        template: 'plotly_dark', 
        paper_bgcolor: '#1e1e1e', // Background color of the outer canvas
        plot_bgcolor: '#1e1e1e', // Background color of the plotting area
        xaxis: {
            color: '#fff', // X-axis text color
            gridcolor: '#444', // X-axis grid line color
        },
        yaxis: {
            color: '#fff', // Y-axis text color
            gridcolor: '#444', // Y-axis grid line color
        },
        legend: {
            font: {
                color: '#fff' // Legend text color
            }
        },
    };

Plotly.plot('myDiv', data, layout, {template:'plotly_dark'},{showSendToCloud: true});

myPlot.on('plotly_hover', function(data){
    var infotext = data.points.map(function(d){
    return (d.data.name+': x= '+d.x+', y= '+d.y.toPrecision(3));
    });

    hoverInfo.innerHTML = infotext.join('<br/>');
})
.on('plotly_unhover', function(data){
    hoverInfo.innerHTML = '';
});

