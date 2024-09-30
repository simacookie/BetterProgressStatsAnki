
# import the "show info" tool from utils.py
from importlib import import_module
from xml.etree.ElementInclude import XINCLUDE_FALLBACK
from xml.etree.ElementTree import tostring
import aqt.stats
from aqt.utils import showInfo, qconnect
import aqt
import os
from aqt import gui_hooks
from aqt.webview import AnkiWebView
from aqt import mw;
from datetime import datetime,timedelta,date
from . import chartsJS
from aqt.qt import *
import time
from aqt.qt import sip, QMessageBox
from aqt.operations import QueryOp
load = True
daySinceFirsteReview = 0
webView : AnkiWebView
def myfunc2(web: AnkiWebView):
    global webView
    webView = web
    page = os.path.basename(web.page().url().path())
    if "graphs" not in page:
        return
    mw.col.db.execute("""
    CREATE TABLE IF NOT EXISTS betterProgress (
        day INTEGER PRIMARY KEY,
        interval1 INTEGER ,
        interval2 INTEGER ,
        interval3 INTEGER ,
        interval4 INTEGER ,
        interval5 INTEGER ,
        interval6 INTEGER ,
        interval7 INTEGER
    );
    """)
    lastTimestampInBetterProgress = mw.col.db.execute("""
        SELECT MAX(day) FROM betterProgress
    """)
    numberOfDaysToUpdate = 0
    replace = 0
    firstReviewDateTimestamp = mw.col.db.execute(""" 
    SELECT MIN(id) FROM revlog
    """)
    lastReviewTimestamp = mw.col.db.execute(""" 
    SELECT MAX(id) FROM revlog
    """)
    todayDate = date.today()
    rollover = mw.col.get_preferences().scheduling.rollover
    todayTimestamp = unix_time_millis(datetime.datetime.combine(todayDate, datetime.datetime.min.time())) + rollover * 3600000
    firstReviewDateTimestampFloat = float(firstReviewDateTimestamp[0][0])
    firstReviewDate = datetime.datetime.fromtimestamp(firstReviewDateTimestampFloat / 1000)
    daysSinceFirstReviewTimestamp = datetime.datetime.today() - firstReviewDate; 
    global daysSinceFirstReview
    daysSinceFirstReview = daysSinceFirstReviewTimestamp.days
       
    if(lastTimestampInBetterProgress[0][0] is None):
        showDialog(23)
        progressBar = PopUpProgressB()
        numberOfDaysToUpdate = daysSinceFirstReview + 1
    elif(lastTimestampInBetterProgress[0][0] != getNextTimestamp()):
        progressBar = PopUpProgressB()
        numberOfDaysToUpdate = (getNextTimestamp() - lastTimestampInBetterProgress[0][0]) / 86400000 
    elif(lastTimestampInBetterProgress[0][0] == getNextTimestamp()):
        replace = 1
    isDataGenerated = True
    if(load):
        rollover = mw.col.get_preferences().scheduling.rollover
        if(replace == 0):
            isDataGenerated = False
            generateDataWithProgress(numberOfDaysToUpdate, progressBar)
        else:
            updateLastEntry()  
        if(isDataGenerated): LoadGraph(web)
def LoadGraph(web: AnkiWebView):                 
    progressToday = getProgressForToday()

    web.eval(
        chartsJS.addChartsJS() + 
        """
        div = document.createElement("div");
        div.innerHTML = `


        <table style="width: 100%; border-collapse: collapse; text-align: center;">
            <tr>
                <th style="background-color: #ffc02b; padding: 10px;">&gt;120 days</th>
                <th style="background-color: #b5820b; padding: 10px;">&gt;60 days</th>
                <th style="background-color: #7acaff; padding: 10px;">&gt;30 days</th>
                <th style="background-color: #3377c4; padding: 10px;">&gt;15 days</th>
                <th style="background-color: #cfcfcf; padding: 10px;">&gt;7 days</th>
                <th style="background-color: #7d7d7d; padding: 10px;">&gt;3 days</th>
                <th style="background-color: #505050; padding: 10px;">&ge;1 day</th>
            </tr>
            <tr>
                <td style="padding: 10px;" id="interval120display"></td>
                <td style="padding: 10px;" id="interval60display"></td>
                <td style="padding: 10px;" id="interval30display"></td>
                <td style="padding: 10px;" id="interval15display"></td>
                <td style="padding: 10px;" id="interval7display"></td>
                <td style="padding: 10px;" id="interval3display"></td>
                <td style="padding: 10px;" id="interval1display"></td>
            </tr>
        </table>
        <form name="progressToday">
            <div style="margin-top: 20px; text-align: center;">
                <label for="3DaysAgo" style="margin-right: 10px;">
                    <input type="radio" id="3DaysAgo" name="daySelection" value="3DaysAgo"> -3 Days
                </label>

                <label for="2DaysAgo" style="margin-right: 10px;">
                    <input type="radio" id="2DaysAgo" name="daySelection" value="2DaysAgo"> -2 Days
                </label>

                <label for="yesterday" style="margin-right: 10px;">
                    <input type="radio" id="yesterday" name="daySelection" value="yesterday"> Yesterday
                </label>

                <label for="today" style="margin-right: 10px;">
                    <input type="radio" id="today" name="daySelection" value="today" checked> Today
                </label>
        </form>

        </div>


    <canvas id="myChart" width="400" height="400"></canvas>
    <form name="betterProgressForm">
    <fieldset style = "text-align: center; padding-top: 10px;"> 
        <label>
        <input type="radio" value="All" name = "selectRange" id="BetterProgressAllDays"> All
        </label>
        <label>
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
        
        createProgressLabelsToday();




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
        function createProgressLabelsToday()
        {

        var interval1 = document.getElementById("interval1display");
        interval1.innerHTML = "";
        var text = document.createTextNode('""" + addPlus(str(progressToday[4][0])) + """');
        interval1.appendChild(text);

        var interval3 = document.getElementById("interval3display");
        interval3.innerHTML = "";
        var text1 = document.createTextNode('""" + addPlus(str(progressToday[4][1])) + """');
        interval3.appendChild(text1);

        var interval7 = document.getElementById("interval7display");
        interval7.innerHTML = "";
        var text2 = document.createTextNode('""" + addPlus(str(progressToday[4][2])) + """');
        interval7.appendChild(text2);

        var interval15 = document.getElementById("interval15display");
        interval15.innerHTML = "";
        var text3 = document.createTextNode('""" + addPlus(str(progressToday[4][3])) + """');
        interval15.appendChild(text3);

        var interval30 = document.getElementById("interval30display");
        interval30.innerHTML = "";
        var text4 = document.createTextNode('""" + addPlus(str(progressToday[4][4])) + """');
        interval30.appendChild(text4);

        var interval60 = document.getElementById("interval60display");
        interval60.innerHTML = "";
        var text5 = document.createTextNode('""" + addPlus(str(progressToday[4][5])) + """');
        interval60.appendChild(text5);

        var interval120 = document.getElementById("interval120display");
        interval120.innerHTML = "";
        var text6 = document.createTextNode('""" + addPlus(str(progressToday[4][6])) + """');
        interval120.appendChild(text6);

    }
    function createProgressLabelsYesterday()
    {
        var interval1 = document.getElementById("interval1display");
        interval1.innerHTML = "";
        var text = document.createTextNode('""" + addPlus(str(progressToday[3][0])) + """');
        interval1.appendChild(text);

        var interval3 = document.getElementById("interval3display");
        interval3.innerHTML = "";
        var text1 = document.createTextNode('""" + addPlus(str(progressToday[3][1])) + """');
        interval3.appendChild(text1);

        var interval7 = document.getElementById("interval7display");
        interval7.innerHTML = "";
        var text2 = document.createTextNode('""" + addPlus(str(progressToday[3][2])) + """');
        interval7.appendChild(text2);

        var interval15 = document.getElementById("interval15display");
        interval15.innerHTML = "";
        var text3 = document.createTextNode('""" + addPlus(str(progressToday[3][3])) + """');
        interval15.appendChild(text3);

        var interval30 = document.getElementById("interval30display");
        interval30.innerHTML = "";
        var text4 = document.createTextNode('""" + addPlus(str(progressToday[3][4])) + """');
        interval30.appendChild(text4);

        var interval60 = document.getElementById("interval60display");
        interval60.innerHTML = "";
        var text5 = document.createTextNode('""" + addPlus(str(progressToday[3][5])) + """');
        interval60.appendChild(text5);

        var interval120 = document.getElementById("interval120display");
        interval120.innerHTML = "";
        var text6 = document.createTextNode('""" + addPlus(str(progressToday[3][6])) + """');
        interval120.appendChild(text6);

    }
    function createProgressLabelsTwoDaysAgo()
    {
        var interval1 = document.getElementById("interval1display");
        interval1.innerHTML = "";
        var text = document.createTextNode('""" + addPlus(str(progressToday[2][0])) + """');
        interval1.appendChild(text);

        var interval3 = document.getElementById("interval3display");
        interval3.innerHTML = "";
        var text1 = document.createTextNode('""" + addPlus(str(progressToday[2][1])) + """');
        interval3.appendChild(text1);

        var interval7 = document.getElementById("interval7display");
        interval7.innerHTML = "";
        var text2 = document.createTextNode('""" + addPlus(str(progressToday[2][2])) + """');
        interval7.appendChild(text2);

        var interval15 = document.getElementById("interval15display");
        interval15.innerHTML = "";
        var text3 = document.createTextNode('""" + addPlus(str(progressToday[2][3])) + """');
        interval15.appendChild(text3);

        var interval30 = document.getElementById("interval30display");
        interval30.innerHTML = "";
        var text4 = document.createTextNode('""" + addPlus(str(progressToday[2][4])) + """');
        interval30.appendChild(text4);

        var interval60 = document.getElementById("interval60display");
        interval60.innerHTML = "";
        var text5 = document.createTextNode('""" + addPlus(str(progressToday[2][5])) + """');
        interval60.appendChild(text5);

        var interval120 = document.getElementById("interval120display");
        interval120.innerHTML = "";
        var text6 = document.createTextNode('""" + addPlus(str(progressToday[2][6])) + """');
        interval120.appendChild(text6);

    }
    function createProgressLabelsThreeDaysAgo()
    {
        var interval1 = document.getElementById("interval1display");
        interval1.innerHTML = "";
        var text = document.createTextNode('""" + addPlus(str(progressToday[1][0])) + """');
        interval1.appendChild(text);

        var interval3 = document.getElementById("interval3display");
        interval3.innerHTML = "";
        var text1 = document.createTextNode('""" + addPlus(str(progressToday[1][1])) + """');
        interval3.appendChild(text1);

        var interval7 = document.getElementById("interval7display");
        interval7.innerHTML = "";
        var text2 = document.createTextNode('""" + addPlus(str(progressToday[1][2])) + """');
        interval7.appendChild(text2);

        var interval15 = document.getElementById("interval15display");
        interval15.innerHTML = "";
        var text3 = document.createTextNode('""" + addPlus(str(progressToday[1][3])) + """');
        interval15.appendChild(text3);

        var interval30 = document.getElementById("interval30display");
        interval30.innerHTML = "";
        var text4 = document.createTextNode('""" + addPlus(str(progressToday[1][4])) + """');
        interval30.appendChild(text4);

        var interval60 = document.getElementById("interval60display");
        interval60.innerHTML = "";
        var text5 = document.createTextNode('""" + addPlus(str(progressToday[1][5])) + """');
        interval60.appendChild(text5);

        var interval120 = document.getElementById("interval120display");
        interval120.innerHTML = "";
        var text6 = document.createTextNode('""" + addPlus(str(progressToday[1][6])) + """');
        interval120.appendChild(text6);

    }

    function createData(datacount, numberOfDays)
    {
        return {
        labels: createLabels(datacount),
        datasets: [

            {
            barPercentage: 1.2,
            label: '>120 days',
            data: getIntervals(7, datacount),
            backgroundColor: "rgba(255, 192, 43,1)",
            },
            {
            barPercentage: 1.2,
            label: '>60 days',
            data: getIntervals(6, datacount),
            backgroundColor: "rgba(181, 130, 11,1",
            },
            {
            barPercentage: 1.2,
            label: '>30 days',
            data: getIntervals(5, datacount),
            backgroundColor: "rgba(122, 202, 255,1)",
            },
            {
            barPercentage: 1.2,
            label: '>15 days',
            data: getIntervals(4, datacount),
            backgroundColor: "rgba(51, 119, 196,1)",
            },
            {
            barPercentage: 1.2,
            label: '>7 days',
            data: getIntervals(3, datacount),
            backgroundColor: "rgba(207, 207, 207,1)",
            },
            {
            barPercentage: 1.2,
            label: '>3 days',
            data: getIntervals(2, datacount),
            backgroundColor: "rgba(125, 125, 125,1)",
            },
            {
            barPercentage: 1.2,
            label: '≥1 day',
            data: getIntervals(1, datacount),
            backgroundColor: "rgba(80, 80, 80,1)",
            }


            ]
        };
    }
    const myChart = new Chart(ctx, {
        type: 'bar',
        data: createData(7),
        options: {
            barPercentage: 1,

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
                    stacked: true,
                    max: """ + str(round(getNumberOfCards()[0][0],0)) + """
                }
                
            }

        },
    });
    var rad = document.betterProgressForm.selectRange;
    rad[0].addEventListener('click', function (event) {
        myChart.data = createData( """ +
        str(int(daysSinceFirstReview))
        + """);
    myChart.update();   
    });
    rad[1].addEventListener('click', function (event) {
        console.log('event triggered 1')
        myChart.data = createData(365);
        myChart.update();   
    });
    rad[2].addEventListener('click', function (event) {
        console.log('event triggered 2')
        myChart.data = createData(90);
        myChart.update();   
    });
    rad[3].addEventListener('click', function (event) {
        console.log('event triggered 3')
        myChart.data = createData(7);
        myChart.update();   
    });

    var progress = document.progressToday.daySelection; 
    progress[3].addEventListener('click', function (event) {
        console.log('progressChanged')
        createProgressLabelsToday()
    });
    progress[2].addEventListener('click', function (event) {
        console.log('progressChanged')
        createProgressLabelsYesterday()
    });
    progress[1].addEventListener('click', function (event) {
        console.log('progressChanged')
        createProgressLabelsTwoDaysAgo()
    });
    progress[0].addEventListener('click', function (event) {
        console.log('progressChanged')
        createProgressLabelsThreeDaysAgo()
    });

    

    function getIntervals(interval, numberOfDays)
    {
        if(numberOfDays == 7)
        {
            data = """ + str(getDataFor7Days()) + """;
        }
        else if(numberOfDays == 90)
        {
            data = """ + str(getDataFor90Days()) + """;
        }
        else if(numberOfDays == 365)
        {
            data = """ + str(getDataFor365Days()) + """;
        }
        else
        {
            data = """ + str(getDataForAllDays()) + """;
        }

        intervals = [];
        for (let x = 0; x < data.length; x++)
        {
            intervals.push(data[x][interval])
        }
        return intervals
    }
"""
            )
                
def isBeforeRollover():
    return 

def addPlus(input):
    if(int(input) > 0):
        return '+' + input
    else:
        return input

def getNumberOfCards():
    return mw.col.db.execute(""" SELECT COUNT(id) FROM cards """)
def getDataFor7Days():
    return mw.col.db.execute("""
    SELECT * FROM (
        SELECT *
        FROM betterProgress
        ORDER BY day DESC
        LIMIT 7
    )
    ORDER BY day ASC
    """)
def getDataFor90Days():
        return mw.col.db.execute("""
    SELECT * FROM (
        SELECT *
        FROM betterProgress
        ORDER BY day DESC
        LIMIT 90
    )
    ORDER BY day ASC
    """)
def getDataFor365Days():
        return mw.col.db.execute("""
    SELECT * FROM (
        SELECT *
        FROM betterProgress
        ORDER BY day DESC
        LIMIT 365
    )
    ORDER BY day ASC
    """)

def getProgressForToday():
    return mw.col.db.execute("""
    
    SELECT 	
        interval1 - LAG(interval1)
        OVER (ORDER BY day ) AS interval1Progress,
        interval2 - LAG(interval2)
        OVER (ORDER BY day ) AS interval2Progress,
        interval3 - LAG(interval3)
        OVER (ORDER BY day ) AS interval3Progress,
        interval4 - LAG(interval4)
        OVER (ORDER BY day ) AS interval4Progress,
        interval5 - LAG(interval5)
        OVER (ORDER BY day ) AS interval5Progress,
        interval6 - LAG(interval6)
        OVER (ORDER BY day ) AS interval6Progress,
        interval7 - LAG(interval7)
        OVER (ORDER BY day ) AS interval7Progress
    FROM 
        (SELECT * 
        FROM betterProgress
        ORDER BY day DESC
        LIMIT 5)




    """)

def getCurrentTimeAsTimestamp():
    return round(time.time()*1000)

def getYesterdaysTimestamp():
    rollover = mw.col.get_preferences().scheduling.rollover
    todayDate = date.today() - timedelta(days=1)
    return unix_time_millis(datetime.datetime.combine(todayDate, datetime.datetime.min.time())) + rollover * 3600000

def getTomorrowsTimestamp():
    rollover = mw.col.get_preferences().scheduling.rollover
    todayDate = date.today() - timedelta(days=-1)
    return unix_time_millis(datetime.datetime.combine(todayDate, datetime.datetime.min.time())) + rollover * 3600000

def getTodaysTimestamp():
    rollover = mw.col.get_preferences().scheduling.rollover
    todayDate = date.today()
    return unix_time_millis(datetime.datetime.combine(todayDate, datetime.datetime.min.time())) + rollover * 3600000

def getNextTimestamp():
    todaysTimestamp = getTodaysTimestamp()
    if(getCurrentTimeAsTimestamp() < todaysTimestamp): return todaysTimestamp
    else: return getTomorrowsTimestamp()

from aqt.operations import CollectionOp
from anki.collection import OpChanges

def generateData(numberOfDaysToGenerate, progressBarWindow)-> CollectionOp[OpChanges]:

    rollover = mw.col.get_preferences().scheduling.rollover
    startDay = -1
    if(getCurrentTimeAsTimestamp() < getTodaysTimestamp()): startDay = 0
    for i in range(startDay, int(numberOfDaysToGenerate)):
        dateForStats = date.today() - timedelta(days=i)
        dayInMS = unix_time_millis(datetime.datetime.combine(dateForStats, datetime.datetime.min.time())) + rollover * 3600000
        saveIntervals(dayInMS)
        if(i != int(numberOfDaysToGenerate)): aqt.mw.taskman.run_on_main(
            lambda: progressBarWindow.on_count_changed(i)
    )
    #aqt.mw.taskman.run_on_main(
            #lambda: LoadGraph(web))
    

def generateDataWithProgress(numberOfDaysToGenerate, progressBarWindow):
    op = QueryOp(
        # the active window (main window in this case)
        parent=mw,
        # the operation is passed the collection for convenience; you can
        # ignore it if you wish
        op=lambda col: generateData(numberOfDaysToGenerate, progressBarWindow),
        # this function will be called if op completes successfully,
        # and it is given the return value of the op
        success=on_success,
    )

    # if with_progress() is not called, no progress window will be shown.
    # note: QueryOp.with_progress() was broken until Anki 2.1.50
    op.run_in_background()


def on_success(count) -> None:
    LoadGraph(webView)

def getDataForAllDays():
    tomorrowDate = date.today() - timedelta(days=-1)
    tomorrowDateInMS = unix_time_millis(datetime.datetime.combine(tomorrowDate, datetime.datetime.min.time()))
    firstReviewDateTimestamp = mw.col.db.execute(""" 
    SELECT MIN(id) FROM revlog
    """)
    firstReviewDateTimestampFloat = float(firstReviewDateTimestamp[0][0])
    firstReviewDate = datetime.datetime.fromtimestamp(firstReviewDateTimestampFloat / 1000)
    daysSinceFirstReviewTimestamp = datetime.datetime.today() - firstReviewDate; 
    daysSinceFirstReview = daysSinceFirstReviewTimestamp.days

    return mw.col.db.execute("""
    SELECT * FROM (
        SELECT *
        FROM betterProgress
        ORDER BY day DESC
        LIMIT """ + 
        str(int(daysSinceFirstReview))
        + """
    )
    ORDER BY day ASC
    """)
def updateLastEntry():
    mw.col.db.execute("""
        DELETE FROM betterProgress
        WHERE day in
        (
        SELECT day FROM betterProgress ORDER BY day DESC LIMIT 1
        )
    """)
    saveIntervals(getNextTimestamp())



def saveIntervals(day):
    mw.col.db.execute(""" 
WITH filtered_logs AS (
    SELECT 
        ROW_NUMBER () OVER (
            PARTITION BY cid
            ORDER BY id DESC
        ) AS rownum,
        id,
        cid,
        ivl
    FROM revlog
    WHERE id < """ + str(day) + """
)
INSERT INTO betterProgress
SELECT
    """ + str(day) + """ AS day,
    COUNT(CASE WHEN ivl <= 3 THEN id END) AS interval7,
    COUNT(CASE WHEN ivl > 3 AND ivl <= 7 THEN id END) AS interval6,
    COUNT(CASE WHEN ivl > 7 AND ivl <= 15 THEN id END) AS interval5,
    COUNT(CASE WHEN ivl > 15 AND ivl <= 30 THEN id END) AS interval4,
    COUNT(CASE WHEN ivl > 30 AND ivl <= 60 THEN id END) AS interval3,
    COUNT(CASE WHEN ivl > 60 AND ivl <= 120 THEN id END) AS interval2,
    COUNT(CASE WHEN ivl > 120 THEN id END) AS interval1
FROM filtered_logs
WHERE rownum = 1 AND cid IN(SELECT id FROM cards);
    """ )

import datetime



epoch = datetime.datetime.utcfromtimestamp(0)

def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0



gui_hooks.webview_did_inject_style_into_page.append(myfunc2)

from aqt.qt import QWidget, QProgressBar, QVBoxLayout
class PopUpProgressB(QWidget):

    def __init__(self):
        super().__init__()
        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(30, 40, 500, 75)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.pbar)
        self.setLayout(self.layout)
        self.setGeometry(300, 300, 550, 100)
        self.setWindowTitle('Generating data')

        self.show()
        self.pbar.setRange(0, 1300)

    def on_count_changed(self, value):
        self.pbar.setValue(value)

def showDialog(minutes):
    msgBox = QMessageBox()
    msgBox.setText("Do you want to generate interval history? This process may take a couple of minutes if you have been using anki for many years. This process is only necessary when using BetterProgress for the first time.")
    msgBox.setWindowTitle("BetterProgress Initialization")
    msgBox.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
    returnValue = msgBox.exec()
    global load
    if returnValue == QMessageBox.StandardButton.Cancel:
        load = False






