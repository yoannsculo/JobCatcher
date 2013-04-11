#!/bin/bash

# http://www.apec.fr/fluxRss/XML/OffresCadre_F101833.xml

FILE=OffresCadre_F101810.xml
TMP0_FILE=./tmp
TMP_FILE=./toto
TMP_FILE2=./toto2
JOBS_DIR=./jobs
STAT_DIR=./stat
DL_DIR=./dl
CFG_FILE=./config

function usage()
{
	echo "add_entry"
	exit
}

function store_mkd()
{
	JOB_FILE=$1
	echo "----" > $JOB_FILE
	echo "title: $TITLE" >> $JOB_FILE
	echo "date: $PUBDATE" >> $JOB_FILE
	echo "company: $COMPANY" >> $JOB_FILE
	echo "ref: APEC-$REF" >> $JOB_FILE
	echo "contract: $CONTRACT" >> $JOB_FILE
	echo "location: $LOCATION" >> $JOB_FILE
	echo "salary: $SALARY" >> $JOB_FILE
	echo "experience: $EXPERIENCE" >> $JOB_FILE
	echo "url: $URL" >> $JOB_FILE
	echo -e "---\n" >> $JOB_FILE
	echo "$CONTENT" >> $JOB_FILE
}

function store_db()
{
	echo ./db_add_entry.sh 'APEC' "$REF" "$PUBDATE" "$COMPANY" "$CONTRACT" "$LOCATION" "$SALARY" "$URL" "$CONTENT"
}

# $1 : html input
function parse_html()
{
	if [[ ! -f $1 ]]; then
		echo "parse_html error : wrong parameters ($1) ";
		exit 1
	fi

	INPUT_FILE=$1

	html2text $INPUT_FILE > $TMP_FILE
	if [ $? -ne 0 ]; then
		echo "html2text error "
		exit 1
	fi

	# Remove remaining HTML chars
	sed -i 's/\&amp;/\&/' $TMP_FILE

	# Locate what's interesting
	BEGIN=`grep -n '^\[Submit .*rien.jpg\]$' $TMP_FILE | cut -d':' -f1`
	END=`grep -n '^Postuler_à_cette_offre$' $TMP_FILE | tail -n 1 | cut -d':' -f1`
	BEGIN=$(( $BEGIN + 3 ))
	END=$(( $END - 1 ))

	# Parsing error
	[[ $BEGIN -eq 0 || $END -eq 0 ]] && exit 1

	# Remove the rest of the content
	cat $TMP_FILE | awk 'NR >= '$BEGIN' && NR <= '$END > $TMP_FILE2

	# Retrieve information
	REF=`grep "^Référence Apec :" $TMP_FILE2 | cut -d':' -f2 | sed 's/^ *\(.*\) *$/\1/'`
	CONTRACT=`grep "^Type de contrat :" $TMP_FILE2 | cut -d':' -f2 | sed 's/^ *\(.*\) *$/\1/'`
	LOCATION=`grep "^Lieu :" $TMP_FILE2 | cut -d':' -f2 | sed 's/^ *\(.*\) *$/\1/'`
	SALARY=`grep "^Salaire :" $TMP_FILE2 | cut -d':' -f2 | sed 's/^ *\(.*\) *$/\1/'`
	EXPERIENCE=`grep "^Expérience :" $TMP_FILE2 | cut -d':' -f2 | sed 's/^ *\(.*\) *$/\1/'`
	PUBDATE=`grep "^Date de publication :" $TMP_FILE2 | cut -d':' -f2 | sed 's/^ *\(.*\) *$/\1/'`

	# Is there a logo ?
	grep "\/.*logo_[0-9]*" $INPUT_FILE &> /dev/null
	if [ $? -eq 0 ]; then
		# yes
		COMPANY=`grep '^Société :.*\[\(.*\)\]$' $TMP_FILE | sed 's/^Société :.*\[\(.*\)\]$/\1/'`
	else
		# no
		COMPANY=`grep "^Société :" $TMP_FILE | cut -d':' -f2 | sed 's/^ *\(.*\) *$/\1/'`
	fi

	# Some clean-up
	# Remove non-breaking space (ugh!)
	sed -i -e '/^\[Submit\]$/d' \
	       -e 's/\xc2\xa0//' $TMP_FILE2

	# Remove multiple blank lines (TODO : it seems we can't use the 3 sed commands together...)
	sed -i '/^$/N;/^\n$/D' $TMP_FILE2

	# Retrieve content of the job offer
	BEGIN=`grep -n '^Sauvegarder_cette_offre$' $TMP_FILE2 | cut -d':' -f1`
	BEGIN=$(($BEGIN + 1))

	# Parsing error
	[[ $BEGIN -eq 0 || $END -eq 0 ]] && exit 1


	# echo "cat $TMP_FILE2 | awk 'NR >= $BEGIN'"
	CONTENT=`cat $TMP_FILE2 | awk 'NR >= '$BEGIN`
	# cat $TMP_FILE2 | awk 'NR >= '$BEGIN >> $JOB_FILE
	# echo "$CONTENT"
}

function escape_var()
{
	VAR=`echo $@ | sed 's/\"/\\\"/g'`
	echo "$VAR"
}

function fetch_rss_feed()
{
	FILE=$1
	[[ ! -e $FILE ]] && return

	OLD_DATE=$2
	[[ -z $OLD_DATE ]] && return

	PUBDATE=`xmlstarlet sel -t -v "rss/channel/pubDate" $FILE`

	xmlstarlet sel -t -m //item -v "concat(title, ';;', link, ';;', pubDate)" -n $FILE > $TMP0_FILE

	# xmlstarlet leaves an empty line at the end of the file. Let's remove it
	# Some offers begin with '* Title', lets remove the star
	# Some offers begin with '/ Title', lets remove the '/'
	sed -i -e '/^$/d' \
	       -e 's/^\* //' \
	       -e 's/^\/ //' $TMP0_FILE

	COUNT=0

	while read line
	do
		JOB_PUBDATE=`echo "$line" | awk -F';;' '{print $3}'`
		EPOCH_DATE=`date -d "$JOB_PUBDATE" +%s`

		# If we already parsed this, don't go further
		[[ $(($EPOCH_DATE)) -le $(($OLD_DATE)) ]] && break

		TITLE=`echo "$line" | awk -F';;' '{print $1}'`
		URL=`echo "$line" | awk -F';;' '{print $2}' | awk -F'?' '{print $1}'`
		REF_SHORT=`echo "$line" | sed 's/^.*_*\([0-9]\{8\}[a-Z]\)_*\.html.*/\1/'`
		DATE_PATH=`date -d "$JOB_PUBDATE" +%Y/%m/%d`
		JOB_DIR=$JOBS_DIR/$DATE_PATH

		# Remove remaining HTML chars
		TITLE=`echo $TITLE | sed 's/\&amp;/\&/'`

		echo "- Fetching \"$TITLE\""

		if [ ! -e $JOB_DIR ]; then
			mkdir -p $JOB_DIR
		fi

		if [ -z $URL ]; then
			echo "error: missing url for $TITLE - $line"
			exit 1
		fi

		if [ ! -e "$JOB_DIR/$REF_SHORT" ]; then
			wget -q $URL -O $JOB_DIR/$REF_SHORT
		fi

		parse_html $JOB_DIR/$REF_SHORT
		store_mkd $JOB_DIR/$REF.mkd
		rm "$JOB_DIR/$REF_SHORT"
		#store_bdd

		# rm $JOB_DIR/$REF

		REF=`escape_var $REF`
		PUBDATE=`escape_var $PUBDATE`
		COMPANY=`escape_var $COMPANY`
		CONTRACT=`escape_var $CONTRACT`
		LOCATON=`escape_var $LOCATION`
		SALARY=`escape_var $SALARY`
		URL=`escape_var $URL`
		CONTENT=`escape_var $CONTENT`

		COUNT=$(($COUNT + 1))

		#./db_add_entry.sh \"APEC\" \"$REF\" \"$PUBDATE\" \"$COMPANY\" \"$CONTRACT\" \"$LOCATION\" \"$SALARY\" \"$URL\" \"$CONTENT\"
		./db_add_entry.sh 'APEC' "$REF" "$PUBDATE" "$COMPANY" "$CONTRACT" "$LOCATION" "$SALARY" "$URL" "$CONTENT"
	
	done < $TMP0_FILE
	rm $TMP0_FILE

	echo "$COUNT job offers fetched since the last checkout."
}

[ ! -e $STAT_DIR ] && mkdir $STAT_DIR
[ ! -e $DL_DIR ] && mkdir $DL_DIR

# parse_html ./jobs/2013/03/15/42543852W
# exit 0

if [ ! -e $CFG_FILE ]; then
	echo "config file missing."
	exit 1
fi

# Open the config file
while read line
do
	# We parse uncommented lines
	echo $line | grep "^#.*" > /dev/null
	if [ ! $? -eq 0 ]; then
		NAME=`echo $line | cut -d' ' -f1`
		URL=`echo $line | cut -d' ' -f2`
		FREQ=`echo $line | cut -d' ' -f3`

		echo "Querying channel $NAME - $URL"

		wget -q $URL -O $DL_DIR/$NAME.xml
		PUBDATE=`xmlstarlet sel -t -v "rss/channel/pubDate" $DL_DIR/$NAME.xml`
		NEW_DATE=`date -d "$PUBDATE" +%s`
		if [ -e $STAT_DIR/$NAME.stat ]; then
			OLD_DATE=`cat $STAT_DIR/$NAME.stat`
		else
			OLD_DATE=0
		fi
		
		# Is there something new ?
		if [ $(($NEW_DATE)) -le $(($OLD_DATE)) ]; then
			# nope
			echo - channel $NAME is up to date !
			continue
		fi

		fetch_rss_feed $DL_DIR/$NAME.xml $OLD_DATE
		echo $NEW_DATE > $STAT_DIR/$NAME.stat
	fi
done < $CFG_FILE

exit 0

