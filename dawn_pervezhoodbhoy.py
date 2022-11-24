"""
This program scrapes the Pervez Hoodbhoy columns from dawn.com website.
It stores the column ids in an MySQL database. When a new column is published, the program
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

req = Request( "https://www.dawn.com/authors/2286/pervez-hoodbhoy", headers = { "User-Agent": "Mozilla/5.0" } )

connection = pymysql.connect( host = DB_HOST, user = DB_USER, passwd = DB_PASSWORD, db = DB_NAME, charset = "utf8mb4", cursorclass = pymysql.cursors.DictCursor )
cursor = connection.cursor()
cursor.execute( "USE " + DB_NAME )
numberOfRowsReturned = cursor.execute( "SELECT column_id FROM pervez_hoodbhoy" )

results = cursor.fetchall()
results_list = createList( results, "column_id" )

try:
    html = urlopen( req )
except HTTPError as e:
    print( e )
except URLError as e:
    print( e ) 
    print( "Either server is not responding or domain name doesn't exists." )
else:    
    soup = BeautifulSoup( html, 'html.parser' ) #BeautifulSoup can use the file object directly returned by urlopen
    container_div = soup.select_one( "body > .container" )
    articles_div = container_div.find( "div", class_ = "mr-4 m-2" ) #exact string value of the class attribute
    articles = articles_div.select( "article" )
    for article in articles:
        published = article.find( "span", class_ = "timestamp--time")
        column_publish_datetime = published[ "title" ]
        column_data_id = int( article[ "data-id" ] )
        column_title = article.h2.a.get_text().strip()
        if len( results ) != 0:
            if column_data_id not in results_list:
                query = 'INSERT INTO pervez_hoodbhoy (column_id, column_title, column_publish_date) VALUES (%s, %s, %s)'
                cursor.execute( query, ( column_data_id, column_title, column_publish_datetime ) )
                email_body = column_title + " published on " + column_publish_datetime
                commandLine = 'echo "' + email_body + '" | mail -s "New Pervez Hoodbhoy Column" "' + NOTIFY_EMAIL + '"'
                print( "Now sending email" )
                os.system( commandLine )
        else: #the case when database table is empty
            query = 'INSERT INTO pervez_hoodbhoy (column_id, column_title, column_publish_date) VALUES (%s, %s, %s)'
            cursor.execute( query, ( column_data_id, column_title, column_publish_datetime ) )

cursor.connection.commit()
cursor.close()
connection.close()
