#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = 'Yoann Sculo <yoann.sculo@gmail.com>'
__copyright__ = 'Copyright (C) 2013 Yoann Sculo'
__license__ = 'GPLv2'
__version__ = '0.1'

import os
import sys
import urllib2 as urllib
import sqlite3 as lite
import datetime
import time
import re

import codecs
import html2text

from optparse import OptionParser
from xml.dom import minidom

from HTMLParser import HTMLParser
from BeautifulSoup import BeautifulSoup

reload(sys)
sys.setdefaultencoding("utf-8")

class Jobboard():

    def load(self, file):
        self.name = "APEC"
        self.lastFetch = ""
        self.processingDir = "./test-dir"
        self.lastFetchDate = 0

    def fetch(self):

        url = "http://www.apec.fr/fluxRss/XML/OffresCadre_F101810.xml"
        filename = url.split('/')[-1]
        # download_file(url)

        xmldoc = minidom.parse(filename)

        MainPubDate = xmldoc.getElementsByTagName('pubDate')[0].firstChild.data
        epochPubDate = datetime.datetime.strptime(MainPubDate, "%a, %d %b %Y %H:%M:%S +0200").strftime('%s')

        # if (epochPubDate <= self.lastFetchDate):
        #     return 0

        itemlist = xmldoc.getElementsByTagName('item')

        for elt in itemlist :
            # TODO : Test object first
            title = elt.getElementsByTagName('title')[0].firstChild.data
            link = elt.getElementsByTagName('link')[0].firstChild.data
            pubDate = elt.getElementsByTagName('pubDate')[0].firstChild.data

            if (epochPubDate <= self.lastFetchDate):
                break

            print "Downloading %s" % (link)
            # download_file(link, self.processingDir)

        self.processOffers()

    def processOffers(self):
        for file in os.listdir(self.processingDir):
            print "Processing %s" % (file)
            offer = OfferApec()
            offer.loadFromHtml(os.path.join(self.processingDir, file))
            offer.date_add = time.time()
            offer.add_db()

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


class Offer():
    def load(self, src, ref, date_pub, date_add, title, company, contract, location, salary, url, content):
        # self.jobboard = Jobboard()
        self.src = src
        self.ref = ref

        self.date_pub = datetime.datetime.fromtimestamp(int(date_pub))
        self.date_add = datetime.datetime.fromtimestamp(int(date_add))
        self.title = title.encode("utf-8")
        self.company = company.encode("utf-8")
        self.contract = contract.encode("utf-8")
        self.location = location.encode("utf-8")
        self.salary = salary.encode("utf-8")
        self.url = url.encode("utf-8")
        self.content = content.encode("utf-8")

    def loadFromHtml(self, filename):
        ""

    def add_db(self):
        db_add_offer(self)

    #def set_from_row(row):
    #    self.src = row[0]
    #    self.ref = row[1]
    #    self.date_pub = datetime.datetime.fromtimestamp(int(row[2]))
    #    self.date_add = datetime.datetime.fromtimestamp(int(row[3]))
    #    self.title = row[4].encode("utf-8")
    #    self.company = row[5].encode("utf-8")
    #    self.contract = row[6].encode("utf-8")
    #    self.location = row[7].encode("utf-8")
    #    self.salary = row[8].encode("utf-8")
    #    self.url = row[9].encode("utf-8")
    #    self.content = row[10].encode("utf-8")

class OfferApec(Offer):

    src="APEC"

    def loadFromHtml(self, filename):
        fd = open(filename, 'rb')
        html = fd.read()
        fd.close()

        soup = BeautifulSoup(html, fromEncoding="UTF-8")

        # Title
        res = soup.body.find('div', attrs={'class':'boxMain boxOffres box'})
        res = res.find("h2", attrs={'class':'borderBottom0'})
        self.title = HTMLParser().unescape(res.text)

        # Other information
        res = soup.body.find('div', attrs={'class':'content1_9ImbLeft'})
        res = res.findAll("tr")

        for elt in res:
            th = elt.find('th')
            td = elt.find('td')
            if (th.text == u'Référence Apec :'):
                self.ref = HTMLParser().unescape(td.text)
            if (th.text == u'Date de publication :'):
                apec_date = HTMLParser().unescape(td.text)
                self.date_pub = datetime.datetime.strptime(apec_date, "%d/%m/%Y").strftime('%s')
            if (th.text == u'Société :'):
                self.company = HTMLParser().unescape(td.text)
            if (th.text == u'Type de contrat :'):
                self.contract = HTMLParser().unescape(td.text)
            if (th.text == u'Lieu :'):
                self.location = HTMLParser().unescape(td.text)
            if (th.text == u'Salaire :'):
                self.salary = HTMLParser().unescape(td.text)
            if (th.text == u'Expérience :'):
                self.experience = HTMLParser().unescape(td.text)

        # Content
        res = soup.body.find('div', attrs={'class':'contentWithDashedBorderTop marginTop boxContent'})
        res = res.find('div', attrs={'class':'boxContentInside'})
        self.content = HTMLParser().unescape(res.text);

        self.url='http://toto.com'

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
                        salary TEXT, \
                        url TEXT, \
                        content TEXT, \
                        PRIMARY KEY(source, ref))""")
    # cursor.execute("""CREATE TABLE blacklist(company TEXT, PRIMARY KEY(company))""")

def db_add_offer(offer):
    try:
        conn = lite.connect("jobs.db")
        conn.text_factory = str
        cursor = conn.cursor()
        cursor.execute("INSERT INTO offers VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (offer.src, offer.ref,
                 offer.date_pub, offer.date_add,
                 offer.title, offer.company, offer.contract, offer.location, offer.salary, offer.url, offer.content))
        conn.commit()

    except lite.Error, e:
        print "Error %s:" % e.args[0]

    finally:
        if conn:
            conn.close()

def report_generate():
    report = open('full_report.html', 'w')
    conn = lite.connect("jobs.db")
    cursor = conn.cursor()
    sql = "SELECT * FROM offers ORDER BY date_pub DESC"
    cursor.execute(sql)
    data = cursor.fetchall()

    report.write("<html><head>")
    report.write("<link href=\"./bootstrap.css\" rel=\"stylesheet\">")
    report.write("<style>table{border:1px solid black; font: 10pt verdana, geneva, lucida, 'lucida grande', arial, helvetica, sans-serif;}</style>")
    report.write("<meta http-equiv=\"Content-type\" content=\"text/html\"; charset=\"utf-8\"></head>")
    report.write("<body><table class=\"table table-bordered\">")

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
        offer.load(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10])
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

if __name__ == '__main__':
    parser = OptionParser(usage = 'syntax: %prog [options] <from> [to]')
    args = sys.argv[1:]

    parser.set_defaults(version = False)
    parser.add_option('-v', '--version',
                          action = 'store_true', dest = 'version',
                          help = 'Output version information and exit')
    parser.add_option('-r', '--report',
                          action = 'store_true', dest = 'report',
                          help = 'Generate a full report')
    parser.add_option('-a', '--add',
                          action = 'store_true', dest = 'add',
                          help = 'add an offer')
    parser.add_option('-c', '--create',
                          action = 'store_true', dest = 'create',
                          help = 'create the databse')
    parser.add_option('-s', '--start',
                          action = 'store_true', dest = 'start',
                          help = 'start the fetch')

    (options, args) = parser.parse_args(args)

    if options.version:
        print 'apecbot version %s - %s (%s)' % (__version__,
                                                __copyright__,
                                                __license__)
        sys.exit(0)

    if options.report:
        print "Report generation..."
        report_generate()
        print "Done."
        sys.exit(0)

    if options.add:
        if len(args) == 11:
            print "%s" % args[10]
            offer = Offer()
            offer.load(args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9], args[10])
            db_add_offer(offer)

        sys.exit(0)

    if options.create:
        db_create()
        sys.exit(0)

    if options.start:
        jb = Jobboard()
        jb.load("apec.jb")
        jb.fetch()
        sys.exit(0)

