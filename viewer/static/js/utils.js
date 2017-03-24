function createBarChart(graphName,words, labelName ){
  // sorting desc by word.occur
  words.sort(function(a, b) {
      return b.occur - a.occur
  });
  let word = [];
  let occur = [];
  for (i = 0; i < words.length; i++) {
      word.push(words[i].word);
      occur.push(words[i].occur);
  }
  let colors = [];
  for (let i=0; i < words.length ; i++)
    colors[i] = 'rgba(54, 162, 235, 1)';

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
                              data: occur,
                            }
                        ]
            },
    options: {
                animation:{animateScale:true}
              }
  });
}


function createBarChartHours(graphName,hours, labelName ){
  new Chart(graphName, {
    type: 'bar',
    data: {
              labels: [0, 1, 2, 3, 4, 5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23],
              datasets: [
                            {
                              label: labelName,
                              backgroundColor: ['#060709', '#0e1420', '#13182c', '#162640', '#22345c', '#2c4e8d', '#4673b6', '#68a1d8', '#98cfee', '#b7e2f5', '#a9d5f2', '#9fcaed',
                                                    '93bde3', '#87aed9', '#789ccc', '#7399c6', '#7080bb' , '#5d6ab0', '#364392', '#272e64', '#272e64', '#0f1221', '#0f1221', '#0f1221' ],
                              borderColor: ['#060709', '#0e1420', '#13182c', '#162640', '#22345c', '#2c4e8d', '#4673b6', '#68a1d8', '#98cfee', '#b7e2f5', '#a9d5f2', '#9fcaed',
                                                    '93bde3', '#87aed9', '#789ccc', '#7399c6', '#7080bb' , '#5d6ab0', '#364392', '#272e64', '#272e64', '#0f1221', '#0f1221', '#0f1221' ],
                              borderWidth: 1,
                              data: hours,
                            }
                        ]
            },
    options: {
                animation:{animateScale:true}
              }
  });
}


function createDonut(graphName, sources, num,){
  new Chart(graphName, {
      type: 'doughnut',
      data: {
        labels: sources,
        datasets: [
            {
                data: num,
                backgroundColor: ["#FF6384","#36A2EB","#FFCE56","#FFBA49","#20A39E","#EF5B5B","#23001E","#A4A9AD","#8CDFD6","#5A716A"],
                hoverBackgroundColor: ["#FF6384","#36A2EB","#FFCE56","#FFBA49","#20A39E","#EF5B5B","#23001E","#A4A9AD","#8CDFD6","#5A716A"]
            }]
      },
      options: {
          animation:{
              animateScale:true
          },
      }
  });
}
