#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import urllib2 as urllib
from xml.dom import minidom
import sqlite3 as lite
import datetime

from apecbot import Offer

def download_file(url, path="./"):
    filename = os.path.join(path, url.split('/')[-1])
    file = urllib.urlopen(url, filename);
    out = open(filename,'wb') #iso-8859-1
    #encoding=file.headers #['content-type'].split('charset=')[-1]
    #print encoding
    #ucontent = unicode(content, encoding)
    # Python sees "Content-Type: text/html" for Apec pages, no charset information...
    # Let's force encoding
    out.write(unicode(file.read(), 'iso-8859-1'))
    out.close()

def db_create():
    conn = None
    conn = lite.connect("jobs.db")
    cursor = conn.cursor()

    # create a table
    cursor.execute("""CREATE TABLE offers( \
                        source TEXT, \
                        ref TEXT, \
                        date_pub INTEGER, \
                        date_add INTEGER, \
                        title TEXT, \
                        company TEXT, \
                        contract TEXT, \
                        location TEXT, \
                        lat TEXT, \
                        lon TEXT, \
                        salary TEXT, \
                        url TEXT, \
                        content TEXT, \
                        PRIMARY KEY(source, ref))""")
    cursor.execute("""CREATE TABLE blacklist(company TEXT, PRIMARY KEY(company))""")

def db_add_offer(offer):
    conn = lite.connect("jobs.db")
    try:
        conn.text_factory = str
        cursor = conn.cursor()
        cursor.execute("INSERT INTO offers VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (offer.src, offer.ref,
                 offer.date_pub, offer.date_add,
                 offer.title, offer.company, offer.contract, offer.location, offer.lat, offer.lon, offer.salary, offer.url, offer.content))
        conn.commit()

    except lite.Error, e:
        """ TODO : Waiting for this ... http://bugs.python.org/issue16379
                lite.errorcode.get(e.sqlite_errorcode)
            USE pip
            In the meantime, let's do something realy dirty. let's catch errors
            by string ! ugh
        """
        if (e.args[0] == "columns source, ref are not unique"):
            return 0
        else:
            return 1
    finally:
        if conn:
            conn.close()

def blocklist_load():
    url = "http://raw.github.com/yoannsculo/emploi/master/ssii/ssii_extended.csv"
    filename = url.split('/')[-1]
    file = urllib.urlopen(url, filename);
    list = []
    for line in file:
        company = unicode(line.rstrip('\n'))
        list.append([company])

    # fp = open('/home/yoann/dev/emploi/ssii/ssii_extended.csv','r') #iso-8859-1
    # list = []
    # for line in fp:
    #     line = unicode(line.rstrip('\n'))
    #     list.append([line])

    print list

    try:
        conn = lite.connect("jobs.db")
        conn.text_factory = str
        cursor = conn.cursor()
        res = cursor.executemany("INSERT INTO blacklist VALUES(?)", list)
        conn.commit()

    except lite.Error, e:
        print "Error %s:" % e.args[0]

    finally:
        if conn:
            conn.close()

def report_generate(filtered=True):

    html_dir = "./www"

    conn = lite.connect("jobs.db")
    cursor = conn.cursor()

    if (filtered):
        sql = "SELECT * FROM offers WHERE company not IN (SELECT company FROM blacklist) ORDER BY date_pub DESC"
        report = open(os.path.join(html_dir, 'report_filtered.html'), 'w')
    else:
        sql = "SELECT * FROM offers ORDER BY date_pub DESC"
        report = open(os.path.join(html_dir, 'report_full.html'), 'w')
    
    #sql = "SELECT * FROM offers WHERE company IN (SELECT company FROM blacklist) ORDER BY date_pub DESC"
    cursor.execute(sql)
    data = cursor.fetchall()

    report.write("<html><head>")
    report.write("<link href=\"./bootstrap.css\" rel=\"stylesheet\">")
    report.write("<style>table{border:1px solid black; font: 10pt verdana, geneva, lucida, 'lucida grande', arial, helvetica, sans-serif;}</style>")
    report.write("<meta http-equiv=\"Content-type\" content=\"text/html\"; charset=\"utf-8\"></head>")
    report.write("<body><table class=\"table table-bordered\">")

    report.write("<p>There are <b>%s</b> offers</p>" %(len(data)))

    report.write("<thead>")
    report.write("<tr>")
    report.write("<th>Pubdate</th>")
    report.write("<th>Source</th>")
    report.write("<th>Title</th>")
    report.write("<th>Location</th>")
    report.write("<th>Company</th>")
    report.write("<th>Salary</th>")
    report.write("</tr>")
    report.write("</thead>")

    for row in data:
        offer = Offer()
        offer.load(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12])
        report.write("<tr>")
        report.write('<td>' + offer.date_pub.strftime('%Y-%m-%d') + '</a></td>')
        report.write('<td>' + offer.src + '</td>')
        report.write('<td><a href="'+offer.url+'">' + offer.title + '</a></td>')
        report.write('<td>' + offer.location + '</td>')
        report.write('<td>' + offer.company + '</td>')
        report.write('<td>' + offer.salary + '</td>')
        report.write("</tr>")
    report.write("</table></body></html>")
    report.close()


