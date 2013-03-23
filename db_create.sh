#! /bin/bash

source db_incl.sh

$DB_CLI 'DROP TABLE offers'
$DB_CLI 'CREATE TABLE offers(source TEXT, id TEXT, date INTEGER, company TEXT, contract TEXT, location TEXT, salary INTEGER, url TEXT, content TEXT, PRIMARY KEY(source, id));'
$DB_CLI 'CREATE TABLE blacklist(company TEXT, PRIMARY KEY(company));'
