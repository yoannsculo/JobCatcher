#! /bin/bash

function escape_var()
{
	VAR=`echo $@ | sed "s/'/''/g"`
	echo "$VAR"
}
source db_incl.sh

if [ $# -lt 9 ]
then
		echo "Please check input arguments"
		exit 1
fi

$DB_CLI "INSERT INTO offers VALUES('`escape_var $1`', '`escape_var $2`', '`escape_var $3`', '`escape_var $4`', '`escape_var $5`', '`escape_var $6`', '`escape_var $7`', '`escape_var $8`', '`escape_var $9`');"
