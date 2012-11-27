Project: Open Classrooms @ UC Berkeley
Website: ucopenclass.herokuapps.com
Description: A web app to designed to find open classrooms at UC Berkeley. Uses schedule.berkeley.edu to as source.

Problem:
Originally I used SQLite3 as the database, but I wanted to put the application on Heroku, which supports PostgreSQL, but not SQLite3. So I converted the SQLite3 database into a PostgreSQL database on Heroku. But now my Flask application file can't read from the PostgreSQL database.

Attempts:
-Edit lines to access PostgreSQL database
-Use SQLAlchemy

Author: Harrison Tsai
Collaborators: Anthony Sutardja, Ryan Higgins