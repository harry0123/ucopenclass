import sqlite3
import building_finder
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing
import building_finder, urllib, datetime
import dateutil.parser as p

#configuration
DATABASE = './buildingsfa12.db'
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    full_name = building_finder.full_name
    abbr = building_finder.abbr
    abbr_safe = building_finder.abbr_safe
    buildings = []
    for building in full_name:
        index = full_name.index(building)
        buildings.append({'full':building, 'abbr':abbr[index], 'abbr_safe':abbr_safe[index]})
    if request.method == 'POST':
        building = request.form['building']
        if building in full_name or building in abbr or building in abbr_safe:
            try:
                index = full_name.index(building)
            except:
                try:
                    index = abbr.index(building)
                except:
                    index = abbr_safe.index(building)
            building = abbr_safe[index]
            return redirect(url_for('building_page', building=building))
        else:
            return render_template('index.html', buildings=buildings, success=False)
    return render_template('index.html', buildings=buildings, success=True)

@app.route('/<building>', methods=['GET', 'POST'])
def building_page(building):
    if request.method == 'POST':
        building = request.form['building']
        room = request.form['room']
        time = request.form['time']
        date = urllib.quote_plus(request.form['datepicker'])
        return redirect(url_for('result', room=room, time=time, date=date, building=building))
    cur = g.db.execute('select distinct room from ' + building + ' order by room asc')
    rooms = [row[0] for row in cur.fetchall()]
    return render_template('building.html', rooms=rooms, building=building)

@app.route('/<room>/<time>/<date>/<building>')
def result(room, time, date, building):
    weekday_map = {0:'M', 1:'Tu', 2:'W', 3:'Th', 4:'F', 5:'S', 6:'Su'}
    #fix time
    if time == 'NOW':
        minute = str(datetime.datetime.now().minute)
        if minute == 0:
            minute = '00'
        when = int(str(datetime.datetime.now().hour) + minute)
    else:
        when = time
    
    #find day
    date=urllib.unquote_plus(date)
    if date == 'TODAY':
        weekday_num = datetime.date.today().weekday()
    else:
        weekday_num = p.parse(date).weekday()
    weekday = weekday_map[weekday_num]
    
    rooms_cur = g.db.execute('select distinct room from ' + building + ' order by room asc')
    rooms = [row[0] for row in rooms_cur.fetchall()]
    if room == 'ALL':
        room_selected = False
        occupied = g.db.execute('select * from ' + building + ' where day=\"' + weekday + '\" and start<=' + str(when) + ' and end>' + str(when) + ' order by room asc')
        entries = [row[0] for row in occupied.fetchall()]
        for occupied_room in entries:
            if occupied_room in rooms:
                rooms.remove(occupied_room)
    else:
        room_selected = True
        occupied = g.db.execute('select * from ' + building + ' where room=' + str(room) + ' and day=\"' + weekday + '\" and start<=' + str(when) + ' and end>' + str(when))
        entries = [row[0] for row in occupied.fetchall()]
        if len(entries) == 0:
            rooms = True
        else:
            rooms = False
    return render_template('building_complete.html', room=room, time=time, date=date, building=building, rooms=rooms, room_selected=room_selected)

if __name__ == '__main__':
    app.run()
