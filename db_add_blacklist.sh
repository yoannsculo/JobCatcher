#! /bin/bash

function escape_var()
{
	VAR=`echo $@ | sed "s/'/''/g"`
	echo "$VAR"
}
source db_incl.sh

if [ $# -lt 1 ]
then
		echo "Please check input arguments"
		exit 1
fi

$DB_CLI "INSERT INTO blacklist VALUES('`escape_var $1`');"
