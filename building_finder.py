"""
buildingsfa12.db last updated: 08/01/2012
"""

import urllib2
import string
import time
from string import Template
import sqlite3
#from bs4 import BeautifulSoup

"""
Gets the source code of a web page
"""
def get_page(url):
    try:
        return urllib2.urlopen(url).read()
    except:
        return ""

"""
Returns 2 lists of building names: full names and abbreviations

full_name, abbr = building_lists()
"""
def building_lists():
    source = get_page("http://registrar.berkeley.edu/Default.aspx?PageID=bldgabb.html")
    #make 2 lists
    full_name = []
    abbr = []

    #look for tags starting with <td valign
    target = "<td valign"
    target_index = source.find(target)
    content = source[target_index:]

    #extract building names
    while target_index != -1:
        word_start = content.find(">") + 1
        word = content[word_start:content.find("</td>")]
        if word.isupper() or word == "FOOTHILL 1" or word == "FOOTHILL 4":
            abbr.append(word)
        else:
            full_name.append(word)
        content = content[content.find("/td"):]
        target_index = content.find(target)
        content = content[target_index:]
    full_name.append("Li Ka Shing Center")
    abbr.append("LI KA SHING")
    return full_name, abbr

"""
Gets the source code of the web page, and checks whether it's an additional page
or not. For fall FL, spring SP, summer SU.
"""
def get_source(building, page, total):
    if " " in building:
        building = building.replace(" ", "+")
    if page > 0: #for search results >100
        url = Template("http://osoc.berkeley.edu/OSOC/osoc?p_term=FL&p_deptname=--+Choose+a+Department+Name+--&p_dept=&p_course=&p_presuf=--%20Choose%20a%20Course%20Prefix/Suffix%20--&p_title=&p_instr=&p_exam=&p_ccn=&p_day=&p_hour=&p_bldg=$bldg&p_units=&p_restr=&p_info=&p_updt=&p_classif=--+Choose+a+Course+Classification+--&p_session=&p_start_row=$nextstart&p_total_rows=$searchtotal")
        url = url.substitute(bldg = building, nextstart = page*100+1, searchtotal = total)
    else:
        url = Template("http://osoc.berkeley.edu/OSOC/osoc?y=0&p_term=FL&p_bldg=$bldg&p_deptname=--+Choose+a+Department+Name+--&p_classif=--+Choose+a+Course+Classification+--&p_presuf=--+Choose+a+Course+Prefix%2fSuffix+--&x=0")
        url = url.substitute(bldg = building)
    return get_page(url)

"""
>>> abbr[85]
'SODA'

soda = find_times(abbr[85])
"""
def find_times(building):
    source = get_source(building, 0, 0)
    times = []
    
    #check for additional page results
    target = " match"
    num_index = source.find(target) - 1
    char = source[num_index]
    num = ''
    while char.isdigit():
        num = char + num
        num_index-=1
        char = source[num_index]
    if num:
        total = int(num)
    else:
        total = 0
    if total > 100: #if there are more than 100 results
        times += extract(source, building)
        pages = total // 100
        while pages > 0:
            source = get_source(building, pages, total)
            times += extract(source, building)
            pages-=1
    else:
        times += extract(source, building)
    return times

"""
Extract times from web page
"""
def extract(source, building):
    classes = []
    content = source[source.find(building) + len(building):]
    while content.find(building) != -1:
        initial_index = content.find(building)
        index = initial_index
        char = content[index]
        while char not in '>;:=': #searches backwards until encounters one of these symbols
            char = content[index]
            index-=1
        data = content[index + 2:initial_index + len(building)].strip()     
        if len(data) > len(building) + 1 and len(data) < len('MTuWThF 1230-1230P, 0000 ') + len(building): #filters invalid entries
            classes.append(data)
        content = content[initial_index + len(building):]
    return classes

"""
Gets times and locations of decal classes

def decal():
    bs = BeautifulSoup(get_page('http://www.decal.org/courses/'))
    link_list = bs.find_all('a')
    full_links = []
    for link in link_list:
        if link.get('href')[-4:].isdigit() and 'facebook' not in link.get('href'):
            full_links.append('http://www.decal.org/courses/' + link.get('href')[-4:])
    info = []
    for link in full_links:
        src = BeautifulSoup(get_page(link))
        td_list = src.find_all('td')
        index = -1
        for td in td_list:
            try:
                if 'maps' in td.find('a').get('href'):
                    index = td_list.index(td)
                    break
            except:
                continue
        if index != -1:
            room = td_list[index].string
            time = td_list[index+1].string
            startdate = td_list[index+2].string
            info.append((room, time, startdate))
    return info
"""
"""
Organizes in to a workable data structure. {Classroom and Building: {Day:
[Hours]}}
#Still need to abstract further, into {Building: {Classroom: {Day: [Hours]}}}

soda_dictionary = times_dictionary(soda)
"""
def times_dictionary(times_list):
    result1 = {}
    for e in times_list:
        comma = e.find(",")
        classroom = e[comma + 2:]
        day_and_hours = e[:comma]
        if classroom in result1:
                result1[classroom].append(day_and_hours)
        else:
                result1[classroom] = [day_and_hours]
    result2 = {}
    every_day = ["M", "Tu", "W", "Th", "F"]
    for classroom in result1:
        result2[classroom] = {}
        for day_hour in result1[classroom]:
            for week_day in every_day:
                if week_day in day_hour:
                    whitespace = day_hour.find(" ")
                    hours = day_hour[whitespace+1:]
                    if week_day in result2[classroom]:
                        result2[classroom][week_day].append(hours)
                    else:
                        result2[classroom][week_day] = [hours]
    return result2

"""
Edit data to be SQL-friendly. Each entry will be [room, day, start, end]
"""
def db_format_list(building):
    times = find_times(building)
    db_list = []
    for time in times:
        if "UNSCHED" in time:
            db_list.append([time[time.find(" "):-len(building)].strip(), "UNSCHED", "0", "0"])
        else:
            entry = db_format_entry(time, building)
            for indv_entry in entry:
                if indv_entry not in db_list: #prevents repeated entries
                    db_list.append(indv_entry)
    building = building.lower()
    if " " in building:
        building = building.replace(" ", "_")
        building = building.replace("\'", "")
    return building, tuple(db_list)

"""
Split each entry into individual entries corresponding to just one day
"""
def db_format_entry(time, building):
    entries = []
    weekdays = ["M", "Tu", "W", "Th", "F"]
    for day in weekdays:
        if day in time[:time.find(" ")]:
            num1 = time[time.find(" "):time.find("-")].strip()
            num2 = time[time.find("-")+1:time.find(",")]
            num1, num2 = time_of_day(num1, num2)
            indv_ent = (time[time.find(",")+1:-len(building)].strip(), day, num1, num2)
            entries.append(indv_ent)
    return entries

"""
Finds time of day and assigns an 'A' or 'P' to the first number

>>> time_of_day('1130', '130P')
('1130A', '130P')
"""
def time_of_day(num1, num2):
	hour1, hour2 = "", ""
	if len(num1) == 3 or len(num1) == 1:
		hour1 = num1[0]
	if len(num1) == 4 or len(num1) == 2:
		hour1 = num1[:2]
	if len(num2[:-1]) == 3 or len(num2[:-1]) == 1:
		hour2 = num2[0]
	if len(num2[:-1]) == 4 or len(num2[:-1]) == 2:
		hour2 = num2[:2]
	if int(hour1) < int(hour2) and hour2 != "12":
		num1 += num2[-1:]
	else:
		if hour1 == "12":
			num1 += "P"
		else:
			num1 += "A"
	num1 = convert(num1)
	num2 = convert(num2)
	return int(num1), int(num2)
"""
Converts a time to military time

>>> convert('530P')
'1730'
"""
def convert(num):
    converted = num
    if num[-1:] == "A":
        if len(num[:-1]) < 3:
            converted = num[:-1] + "00"
        if len(num[:-1]) > 2:
            converted = num[:-1]
    if num[-1:] == "P":
        if len(num[:-1]) == 1:
            converted = str(int(num[:-1]) + 12) + "00"
        if len(num[:-1]) == 2:
            if num[:-1] == "12":
                converted = num[:-1] + "00"
            else:
                converted = str(int(num[:-1]) + 12) + "00"
        if len(num[:-1]) == 3:
            converted = str(int(num[:1]) + 12) + num[1:len(num)-1]
        if len(num[:-1]) == 4:
            if num[:2] == "12":
                converted = num[:-1]
            else:
                converted = str(int(num[:2]) + 12) + num[2:len(num)-1]
    return converted

#creates lists
full_name, abbr = building_lists()
abbr_safe = []
for building in abbr:
    building = building.lower()
    if " " in building:
        building = building.replace(" ", "_")
        building = building.replace("\'", "")
    abbr_safe.append(building)

"""
#Putting list into database
conn = sqlite3.connect('buildingsfa12.db')
start = time.time()
with conn:
    c = conn.cursor()
    for building in abbr:
        name, times = db_format_list(building)
        c.execute("CREATE TABLE " + name + "(Room TEXT, Day TEXT, Start INT, End INT)")
        print "Table created: " + name
        c.executemany("INSERT INTO " + name + " VALUES(?, ?, ?, ?)", times)
print time.time() - start
"""

"""
$sqlite3 buildingsfa12.db
sqlite> .headers on
sqlite> .mode column
sqlite> select * from soda where room=310 and start<1214 and end>1214;
sqlite> select * from soda where room=310 and not (start<1214 and end>1214) order by start asc;
"""
