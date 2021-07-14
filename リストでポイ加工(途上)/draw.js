var ctx = document.getElementById('mychart-scatter');
var myChart = new Chart(ctx, {
    type: 'bubble',
    data: {
            datasets: [{
            label: 'Dataset#1',
            data: [
                {x:10, y:6}, {x:4, y:12}, {x:5, y:10},
                {x:8, y:13}, {x:6, y:8}, {x:9, y:13},
                {x:7, y:12}, {x:8, y:6}, {x:6, y:12},
            ],
            backgroundColor: '#f88',
        }],
    },
    options: {
        scales: {
            y: { min: 0, max: 16 },
            x: { min: 0, max: 12 },
        },
    },
});