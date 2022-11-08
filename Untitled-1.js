div = document.createElement("div");
div.innerHTML = `
<canvas id="myChart" width="400" height="400"></canvas>
<form name="betterProgressForm">
 <fieldset style = "text-align: center; padding-top: 10px;"> 
    <input type="radio" value="1Year" name = "selectRange" id="BetterProgress1Year"> 1 Year
    </label>
    <label>
    <input type="radio" value="3Months" name = "selectRange" id="BetterProgress3Months" > 3 Months
    </label>
    <label>
    <input type="radio" value="7Days" name = "selectRange" id="BetterProgress7Days" checked> 7 Days
    </label>
 </fieldset>
 </form>
`;
    document.body.appendChild(div);

    const ctx = document.getElementById('myChart');
    





    function createLabels(datacount)
    {
        labels = []
        for (let i = 1; i < datacount - 1; i++) {
            labels.push(datacount - i +' days ago')
        }
        labels.push('Yesterday')
        labels.push('Today')
        return labels;
    }
    function createData(datacount, numberOfDays)
    {
        return {
        labels: createLabels(datacount),
        datasets: [
            {
            label: '>3 days',
            data: getIntervals(0, datacount),
            backgroundColor: "rgba(255, 192, 43,1)",
            },
            {
            label: '>7 days',
            data: getIntervals(1, datacount),
            backgroundColor: "rgba(122, 202, 255,1)",
            },
            {
            label: '>15 days',
            data: getIntervals(2, datacount),
            backgroundColor: "rgba(237, 237, 237,1)",
            },
            {
            label: '>30 days',
            data: getIntervals(3, datacount),
            backgroundColor: "rgba(245, 245, 245,1)",
            },
            {
            label: '>60 days',
            data: getIntervals(4, datacount),
            backgroundColor: "rgba(122, 202, 255,1",
            },
            {
            label: '>120 days',
            data: getIntervals(5, datacount),
            backgroundColor: "rgba(255, 192, 43,1)",
            },
            {
            label: 'New',
            data: getIntervals(6, datacount),
            backgroundColor: "rgba(123, 123, 123,.1)",
            },


            ]
        };
    }

    const myChart = new Chart(ctx, {
        type: 'line',
        data: createData(7),
        options: {
            plugins: {
                title: {
                    display: true,
                    text: 'Total Review Progress'
                },
            },
            responsive: true,
            scales: {
                x: {
                    stacked: true,
                },
                y: {
                    stacked: true
                }
            }
        }
    });
    var rad = document.betterProgressForm.selectRange;
    rad[0].addEventListener('click', function (event) {
        myChart.data = createData(365);
        myChart.update();   
    });
    rad[1].addEventListener('click', function (event) {
        myChart.data = createData(90);
        myChart.update();   
    });
    rad[2].addEventListener('click', function (event) {
        myChart.data = createData(7);
        myChart.update();   
    });
    function getIntervals(interval ,numberOfDays)
    {
        rows = """ + str(getRows()) + """;
        intervals = [];
        for (let x = rows.length - numberOfDays; x <= rows.length; x++)
        {
        if(x < 0)
            intervals.push(0)
        else
            intervals.push(rows[x][interval])

        }
         
        return intervals
    }