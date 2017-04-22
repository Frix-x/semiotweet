'use strict'
function createBarChart (graphName, words, labelName) {
  // sorting desc by word.occur
  words.sort((a, b) => b.occur - a.occur)
  var word = words.map(w => w.word)
  var occur = words.map(w => w.occur)
  var colors = words.map(w => 'rgba(54, 162, 235, 1)')
  new Chart(graphName, {
    type: 'bar',
    data: {
      labels: word,
      datasets: [
        {
          label: labelName,
          backgroundColor: colors,
          borderColor: colors,
          borderWidth: 1,
          data: occur
        }
      ]
    },
    options: {
      animation: {
        animateScale: true
      }
    }
  })
}

function createBarChartHours (graphName, hours, labelName) {
  new Chart(graphName, {
    type: 'bar',
    data: {
      labels: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
      datasets: [
        {
          label: labelName,
          backgroundColor: [ '#060709', '#0e1420', '#13182c', '#162640', '#22345c', '#2c4e8d', '#4673b6', '#68a1d8', '#98cfee', '#b7e2f5', '#a9d5f2', '#9fcaed', '93bde3', '#87aed9', '#789ccc', '#7399c6', '#7080bb', '#5d6ab0', '#364392', '#272e64', '#272e64', '#0f1221', '#0f1221', '#0f1221' ],
          borderColor: [ '#060709', '#0e1420', '#13182c', '#162640', '#22345c', '#2c4e8d', '#4673b6', '#68a1d8', '#98cfee', '#b7e2f5', '#a9d5f2', '#9fcaed', '93bde3', '#87aed9', '#789ccc', '#7399c6', '#7080bb', '#5d6ab0', '#364392', '#272e64', '#272e64', '#0f1221', '#0f1221', '#0f1221' ],
          borderWidth: 1,
          data: hours
        }
      ]
    },
    options: {
      animation: {
        animateScale: true
      }
    }
  })
}

function createDonut (graphName, sources, num) {
  new Chart(graphName, {
    type: 'doughnut',
    data: {
      labels: sources,
      datasets: [
        {
          data: num,
          backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#FFBA49', '#20A39E', '#EF5B5B', '#23001E', '#A4A9AD', '#8CDFD6', '#5A716A'],
          hoverBackgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#FFBA49', '#20A39E', '#EF5B5B', '#23001E', '#A4A9AD', '#8CDFD6', '#5A716A']
        }]
    },
    options: {
      animation: {
        animateScale: true
      }
    }
  })
}

function makeSigmaNetwork(container, networkJson, callback) {
    var s = new sigma({
        graph: networkJson,
        renderer: {
            container: container,
            type: 'canvas'
        },
        settings: {
            animationsTime: 5000,
            defaultEdgeType: 'curve',
            drawLabels: true,
            labelColor: 'node',
            defaultLabelColor: '#37474f',
            labelSize: 'proportional',
            labelSizeRatio: 2,
            labelThreshold: 5,
            batchEdgesDrawing: true,
            hideEdgesOnMove: true,
            font: 'Roboto'
        }
    });
    var width = $('#keywordsNetwork').width();
    var height = $('#keywordsNetwork').height()
    s.graph.nodes().forEach(function(node) {
        node.x = Math.random() * width;
        node.y = Math.random() * height;
    });
    s.refresh();
    s.configForceAtlas2({
        worker: true,
        barnesHutOptimize: true,
        edgeWeightInfluence: 1,
        linLogMode: true,
        scalingRatio: 1
    });

    // Drag n Drop plugin init
    var dragListener = sigma.plugins.dragNodes(s, s.renderers[0]);

    // Binded event to show only nodes and neighbors on mouse over
    s.bind('clickNode', function(event) {
        var node = event.data.node.id;
        console.log(event);
        var neighbors = {};
        s.graph.edges().forEach(function(e) {
            if ((e.source) == node || (e.target) == node) {
                neighbors[e.source] = 1;
                neighbors[e.target] = 1;
            }
        });
        console.log(neighbors);
        s.graph.nodes().forEach(function(n) {
            if (!neighbors[n.id]) {
                n.hidden = 1;
            } else {
                n.hidden = 0;
            }
        });
        s.refresh();
    }).bind('clickStage', function() {
        s.graph.edges().forEach(function(e) {
            e.hidden = 0;
        });
        s.graph.nodes().forEach(function(n) {
            n.hidden = 0;
        });
        s.refresh();
    });

    callback(s);
}
