"""
This program scrapes the Gul Bukhari columns from thequint.com website.
It stores the column titles in an MySQL database. When a new column is published, the program
sends a notification to email address.
Assumptions: The machine has mail server like Postfix set up.
Tested on: Ubuntu 20.04, Python 3.8.10
"""

from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
import os, pymysql
from utility_functions import createList
from mysql_connect import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, NOTIFY_EMAIL

req = Request( "https://www.thequint.com/author/616989/gul-bukhari", headers = { "User-Agent": "Mozilla/5.0" } )

connection = pymysql.connect( host = DB_HOST, user = DB_USER, passwd = DB_PASSWORD, db = DB_NAME, charset = "utf8mb4", cursorclass = pymysql.cursors.DictCursor )
cursor = connection.cursor()
cursor.execute( "USE " + DB_NAME )
numberOfRowsReturned = cursor.execute( "SELECT column_title FROM thequint_gulbukhari" )

results = cursor.fetchall()
results_list = createList( results, "column_title" )

try:
    html = urlopen( req )
except HTTPError as e:
    print( e )
except URLError as e:
    print( e ) 
    print( "Either server is not responding or domain name doesn't exists." )
else:
    soup = BeautifulSoup( html, 'html.parser' ) #BeautifulSoup can use the file object directly returned by urlopen
    twelve_story_div = soup.select_one( "body .twelve-story-mixed-design" )
    twelve_story_div_headlines = twelve_story_div.div.select( ".headline-type-4")
    for headline in twelve_story_div_headlines:
        column_title = headline.h2.get_text().strip()
        if len( results ) != 0:
            if column_title not in results_list:
                query = "INSERT INTO thequint_gulbukhari (column_title) VALUES (%s)"
                cursor.execute( query, ( column_title ) )
                email_body = column_title + " published."
                commandLine = 'echo "' + email_body + '" | mail -s "New Gul Bukhari Column" "' + NOTIFY_EMAIL + '"'
                print( "Now sending email" )
                os.system( commandLine )
        else: #the case when database table is empty
            query = "INSERT INTO thequint_gulbukhari (column_title) VALUES (%s)"
            cursor.execute( query, ( column_title ) )

cursor.connection.commit()
cursor.close()
connection.close()
