#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import urllib2 as urllib
from xml.dom import minidom
import sqlite3 as lite
import datetime

from jobcatcher import Offer
from jobcatcher import JobCatcher

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
        return 0

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

def blacklist_flush():
    conn = lite.connect("jobs.db")
    cursor = conn.cursor()
    sql = "DELETE FROM blacklist"
    cursor.execute(sql)
    conn.commit()
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

def statistics_generate():
    html_dir = "./www"

    conn = lite.connect("jobs.db")
    cursor = conn.cursor()

    stat = open(os.path.join(html_dir, 'statistics.html'), 'w')
    stat.write("<html><head>")
    stat.write("<link href=\"./bootstrap.css\" rel=\"stylesheet\">")
    stat.write("<link href=\"./bootstrap-responsive.css\" rel=\"stylesheet\">")
    stat.write("<style>table{font: 10pt verdana, geneva, lucida, 'lucida grande', arial, helvetica, sans-serif;}</style>")
    stat.write("<meta http-equiv=\"Content-type\" content=\"text/html\"; charset=\"utf-8\"></head>")
    stat.write("<body>")

    stat.write("<table class=\"table table-condensed\">")
    stat.write("<thead>")
    stat.write("<tr>")
    stat.write("<th>JobBoard</th>")
    stat.write("<th>Total Offers</th>")
    stat.write("<th>Offers not from blacklist</th>")
    stat.write("<th>Offers from blacklist</th>")
    stat.write("</tr>")
    stat.write("</thead>")

    jb = JobCatcher()
    jb.load_jobBoards()
    for item in jb.jobBoardList:
        data = item.fetchAllOffersFromDB()
        stat.write("<tr>")
        stat.write("<td><a href=\"%s\">%s</a></td>" %(item.url, item.name))
        stat.write("<td>%s</td>" %(len(data)))
        stat.write("<td></td>")
        stat.write("<td></td>")
        stat.write("</tr>")

    stat.write("</table>")
    stat.write("</html>")
    stat.close()

def report_generate(filtered=True):
    html_dir = "./www"

    conn = lite.connect("jobs.db")
    cursor = conn.cursor()

    sql_filtered = "SELECT * FROM offers WHERE company not IN (SELECT company FROM blacklist) ORDER BY date_pub DESC"
    sql_full = "SELECT * FROM offers ORDER BY date_pub DESC"

    cursor.execute(sql_filtered)
    data_filtered = cursor.fetchall()
    count_filtered = len(data_filtered)

    cursor.execute(sql_full)
    data_full = cursor.fetchall()
    count_full = len(data_full)

    #sql = "SELECT * FROM offers WHERE company IN (SELECT company FROM blacklist) ORDER BY date_pub DESC"

    # sql = "SELECT count(*)FROM offers"
    # cursor.execute(sql)
    # count = cursor.fetchone()[0]

    if (filtered):
        report = open(os.path.join(html_dir, 'report_filtered.html'), 'w')
        data = data_filtered
    else:
        report = open(os.path.join(html_dir, 'report_full.html'), 'w')
        data = data_full

    report.write('<!doctype html>\n')
    report.write('<html>\n')
    # html header
    report.write('<head>\n')
    report.write('\t<meta http-equiv="Content-type" content="text/html; charset=utf-8" />\n')
    report.write('\t<link rel="stylesheet" href="css/jquery-ui-1.10.3.custom.min.css">\n')
    report.write('\t<link rel="stylesheet" href="css/simplePagination.css">\n')
    report.write('\t<link rel="stylesheet" href="css/dynamic.css" />\n')
    report.write('\t<script type="text/javascript" src="js/jquery-2.0.3.min.js"></script>\n')
    report.write('\t<script type="text/javascript" src="js/jquery-ui-1.10.3.custom.min.js"></script>\n')
    report.write('\t<script type="text/javascript" src="js/jquery.tablesorter.js"></script>\n')
    report.write('\t<script type="text/javascript" src="js/jquery.simplePagination.js"></script>\n')
    report.write('\t<script type="text/javascript" src="js/persist-min.js"></script>\n')
    report.write('\t<script type="text/javascript" src="js/class.js"></script>\n')
    report.write('\t<script type="text/javascript" src="js/dynamic.js"></script>\n')
    report.write('</head>\n')
    # html body
    report.write('<body>\n')
    # page header
    report.write('\t<p id="header">\n')
    report.write('\t\t<a href=\"report_filtered.html\">%s filtered offers (%.2f%%)</a></li>\n' %(count_filtered, 100*(float)(count_filtered)/count_full))
    report.write('\t\t- %s blacklisted offers (%.2f%%)</li>\n' %(count_full-count_filtered, 100*(float)(count_full-count_filtered)/count_full))
    report.write('\t\t- <a href=\"report_full.html\">All %s offers</a></li>\n' %(count_full))
    report.write('\t\t- <a href=\"statistics.html\">Statistics</a></li>\n')
    report.write('\t</p>\n')
    # page body
    report.write('\t<table id="offers">\n')
    # table header
    report.write('\t\t<thead>\n')
    report.write('\t\t\t<tr id="lineHeaders">\n')
    report.write('\t\t\t\t<th>Pubdate</th>\n')
    report.write('\t\t\t\t<th>Type</th>\n')
    report.write('\t\t\t\t<th>Title</th>\n')
    report.write('\t\t\t\t<th>Company</th>\n')
    report.write('\t\t\t\t<th>Location</th>\n')
    report.write('\t\t\t\t<th>Contract</th>\n')
    report.write('\t\t\t\t<th>Salary</th>\n')
    report.write('\t\t\t\t<th>Source</th>\n')
    report.write('\t\t\t</tr>\n')
    report.write('\t\t\t<tr id="lineFilters">\n')
    report.write('\t\t\t\t<td class="pubdate"></td>\n')
    report.write('\t\t\t\t<td class="type"></td>\n')
    report.write('\t\t\t\t<td class="title"></td>\n')
    report.write('\t\t\t\t<td class="company"></td>\n')
    report.write('\t\t\t\t<td class="location"></td>\n')
    report.write('\t\t\t\t<td class="contract"></td>\n')
    report.write('\t\t\t\t<td class="salary"></td>\n')
    report.write('\t\t\t\t<td class="source"></td>\n')
    report.write('\t\t\t</tr>\n')
    report.write('\t\t</thead>\n')
    # table body
    report.write('\t\t<tbody>\n')

    s_date = ''

    for row in data:
        offer = Offer()
        offer.load(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12])

        if (s_date != offer.date_pub.strftime('%Y-%m-%d')):
            s_date = offer.date_pub.strftime('%Y-%m-%d')

        report.write('\t\t\t<tr>\n')
        report.write('\t\t\t\t<td class="pubdate">' + offer.date_pub.strftime('%Y-%m-%d') + '</td>\n')
        report.write('\t\t\t\t<td class="type">noSSII</td>\n')
        report.write('\t\t\t\t<td class="title"><a href="'+offer.url+'">' + offer.title + '</a></td>\n')
        report.write('\t\t\t\t<td class="company">' + offer.company + '</td>\n')
        report.write('\t\t\t\t<td class="location">' + offer.location + '</td>\n')
        report.write('\t\t\t\t<td class="contract">' + offer.contract +'</td>\n')
        report.write('\t\t\t\t<td class="salary">' + offer.salary + '</td>\n')
        report.write('\t\t\t\t<td class="source">' + offer.src + '</td>\n')
        report.write("\t\t\t</tr>")

    # closure
    report.write('\t</table>\n')
    report.write('</body>\n')
    report.write('</html>\n')
    report.close()


def filter_contract_fr(contract):
    contract = re.sub(ur'Perm', "CDI", contract)
    contract = re.sub(ur'[0-9]+ en (.*)', "\\1", contract, flags=re.DOTALL)
    contract = re.sub(ur'.*CDI.*', "CDI", contract, flags=re.DOTALL)
    contract = re.sub(ur'.*CDD.*de (.*)', "CDD de \\1", contract, flags=re.DOTALL)
    return contract

def filter_location_fr(location):
    location = re.sub(ur'IDF', "Île-de-France", location)
    return location

def filter_salary_fr(salary):
    # TODO : use regexp once whe have a better view of possible combinations
    # TODO : use something similar as ^...$
    salary = re.sub(ur'Selon diplôme et expérience', "NA", salary)
    salary = re.sub(ur'fixe + variable selon profil', "NA", salary)
    salary = re.sub(ur'Fixe+Variable selon profil', "NA", salary)
    salary = re.sub(ur'Fixe + Variable selon profil', "NA", salary)
    salary = re.sub(ur'A définir selon profil', "NA", salary)
    salary = re.sub(ur'A DEFINIR SELON PROFIL', "NA", salary)
    salary = re.sub(ur'à défninir selon profil', "NA", salary)
    salary = re.sub(ur'à définir selon profils', "NA", salary)
    salary = re.sub(ur'à définir selon expérience', "NA", salary)
    salary = re.sub(ur'A négocier selon profil', "NA", salary)
    salary = re.sub(ur'A NEGOCIER SELON PROFIL', "NA", salary)
    salary = re.sub(ur'à négocier selon profil', "NA", salary)
    salary = re.sub(ur'à négocier selon le profil', "NA", salary)
    salary = re.sub(ur'à déterminer selon profil', "NA", salary)
    salary = re.sub(ur'A négocier selon expérience', "NA", salary)
    salary = re.sub(ur'à négocier selon expérience', "NA", salary)
    salary = re.sub(ur'à négocier selon exp', "NA", salary)
    salary = re.sub(ur'à negocier K€ brut/an', "NA", salary)
    salary = re.sub(ur'A voir selon profil', "NA", salary)
    salary = re.sub(ur'Attractive et selon profil', "NA", salary)
    salary = re.sub(ur'De débutant à confirmé', "NA", salary)
    salary = re.sub(ur'En fonction du profil', "NA", salary)
    salary = re.sub(ur'en fonction du profil', "NA", salary)
    salary = re.sub(ur'En fonction de votre profil', "NA", salary)
    salary = re.sub(ur'Fonction profil et expérience', "NA", salary)
    salary = re.sub(ur'Selon profil/expérience', "NA", salary)
    salary = re.sub(ur'Selon profil et expériences', "NA", salary)
    salary = re.sub(ur'Selon profil et expérience', "NA", salary)
    salary = re.sub(ur'selon profil et expérience +', "NA", salary)
    salary = re.sub(ur'selon niveau d\'expérience', "NA", salary)
    salary = re.sub(ur'selon profil et expérience', "NA", salary)
    salary = re.sub(ur'selon profil et exp', "NA", salary)
    salary = re.sub(ur'selon profil et avantages', "NA", salary)
    salary = re.sub(ur'Selon formation et/ou exp.', "NA", salary)
    salary = re.sub(ur'selon votre profil', "NA", salary)
    salary = re.sub(ur'Selon votre profil', "NA", salary)
    salary = re.sub(ur'selon le profil', "NA", salary)
    salary = re.sub(ur'Selon le profil', "NA", salary)
    salary = re.sub(ur'Selon profils', "NA", salary)
    salary = re.sub(ur'Selon profile', "NA", salary)
    salary = re.sub(ur'Selon profil', "NA", salary)
    salary = re.sub(ur'selon profil', "NA", salary)
    salary = re.sub(ur'selon Profil', "NA", salary)
    salary = re.sub(ur'Selon Profil', "NA", salary)
    salary = re.sub(ur'SELON PROFILS', "NA", salary)
    salary = re.sub(ur'SELON PROFIL', "NA", salary)
    salary = re.sub(ur'selo profil', "NA", salary)
    salary = re.sub(ur'Suivant profil', "NA", salary)
    salary = re.sub(ur'selon l\'expérience', "NA", salary)
    salary = re.sub(ur'selon experience', "NA", salary)
    salary = re.sub(ur'selon expérience', "NA", salary)
    salary = re.sub(ur'Selon expérience', "NA", salary)
    salary = re.sub(ur'Selon expérince', "NA", salary)
    salary = re.sub(ur'Selon Expérience', "NA", salary)
    salary = re.sub(ur'Selon experience', "NA", salary)
    salary = re.sub(ur'SELON EXPERIENCE', "NA", salary)
    salary = re.sub(ur'Selon compétences', "NA", salary)
    salary = re.sub(ur'Selon compétence', "NA", salary)
    salary = re.sub(ur'selon exp.', "NA", salary)
    salary = re.sub(ur'Selon exp.', "NA", salary)
    salary = re.sub(ur'selon exp', "NA", salary)
    salary = re.sub(ur'selon grille', "NA", salary)
    salary = re.sub(ur'selon grilles', "NA", salary)
    salary = re.sub(ur'cf. annonce', "NA", salary)
    salary = re.sub(ur'suivant profil', "NA", salary)
    salary = re.sub(ur'fixe + variable', "NA", salary)
    salary = re.sub(ur'grille fonction publique', "NA", salary)
    salary = re.sub(ur'Contrat Apprentissage', "NA", salary)
    salary = re.sub(ur'Salaire Attractif', "NA", salary)
    salary = re.sub(ur'Salaire à négocier', "NA", salary)
    salary = re.sub(ur'à déterminer', "NA", salary)
    salary = re.sub(ur'A déterminer', "NA", salary)
    salary = re.sub(ur'à convenir', "NA", salary)
    salary = re.sub(ur'A convenir', "NA", salary)
    salary = re.sub(ur'à débattre', "NA", salary)
    salary = re.sub(ur'à négocier', "NA", salary)
    salary = re.sub(ur'a négocier', "NA", salary)
    salary = re.sub(ur'a negocier', "NA", salary)
    salary = re.sub(ur'à negocier', "NA", salary)
    salary = re.sub(ur'A négocier', "NA", salary)
    salary = re.sub(ur'A NEGOCIER', "NA", salary)
    salary = re.sub(ur'A negocier', "NA", salary)
    salary = re.sub(ur'à définir', "NA", salary)
    salary = re.sub(ur'à défiinir', "NA", salary)
    salary = re.sub(ur'À définir', "NA", salary)
    salary = re.sub(ur'A définir', "NA", salary)
    salary = re.sub(ur'A DEFINIR', "NA", salary)
    salary = re.sub(ur'A DETERMINER', "NA", salary)
    salary = re.sub(ur'à determiner', "NA", salary)
    salary = re.sub(ur'A definir', "NA", salary)
    salary = re.sub(ur'A défnir', "NA", salary)
    salary = re.sub(ur'A discuter', "NA", salary)
    salary = re.sub(ur'à préciser', "NA", salary)
    salary = re.sub(ur'en fonction exp.', "NA", salary)
    salary = re.sub(ur'Negotiable', "NA", salary)
    salary = re.sub(ur'negotiable', "NA", salary)
    salary = re.sub(ur'Négociable', "NA", salary)
    salary = re.sub(ur'négociable', "NA", salary)
    salary = re.sub(ur'negociable', "NA", salary)
    salary = re.sub(ur'NEGOCIABLE', "NA", salary)
    salary = re.sub(ur'non indiqué', "NA", salary)
    salary = re.sub(ur'non communiqué', "NA", salary)
    salary = re.sub(ur'NON COMMUNIQUE', "NA", salary)
    salary = re.sub(ur'non précisé', "NA", salary)
    salary = re.sub(ur'Non précisé', "NA", salary)
    salary = re.sub(ur'Voir annonce', "NA", salary)
    salary = re.sub(ur'GRILLE DE LA FPT', "NA", salary)
    salary = re.sub(ur'Grille', "NA", salary)
    salary = re.sub(ur'variable', "NA", salary)
    salary = re.sub(ur'confidentiel', "NA", salary)
    salary = re.sub(ur'TBD', "NA", salary)
    salary = re.sub(ur'N.S.', "NA", salary)
    salary = re.sub(ur'ANNUEL', "NA", salary)
    salary = re.sub(ur'NC K€ brut/an', "NA", salary)
    salary = re.sub(ur'xx K€ brut/an', "NA", salary)
    # salary = re.sub(ur'0K€ brut/an', "NA", salary)
    salary = re.sub(ur'--K€ brut/an', "NA", salary)
    salary = re.sub(ur'- K€ brut/an', "NA", salary)
    salary = re.sub(ur'-K€ brut/an', "NA", salary)
    salary = re.sub(ur'XK€ brut/an', "NA", salary)
    salary = re.sub(ur'N/C', "NA", salary)
    salary = re.sub(ur'N.C', "NA", salary)
    salary = re.sub(ur'NC', "NA", salary)
    salary = re.sub(ur'nc', "NA", salary)

    return salary

