#!/bin/bash

LOLIX_RSS=http://back.fr.lolix.org/backend.php

wget -q $LOLIX_RSS -O lolix

for i in {0..9}; do
	LINE_INDEX=$(( $i * 4 + 2 ))
	OFFER=`sed -n $LINE_INDEX,$((LINE_INDEX + 2))p lolix`
	PUBDATE=`echo "$OFFER" | tail -n1`
	EPOCH_DATE=`date -d "$PUBDATE" +%s`
	TITLE=`echo "$OFFER" | head -n1`
	LINK=`echo "$OFFER" | head -n2 | tail -n1`

	ID="LOLIX-"`echo $LINK | sed 's/.*?id=\([0-9]*\)$/\1/'`

	wget -q $LINK -O $ID
	html2text $ID > $ID.mkd

	# echo $TITLE
	# echo $PUBDATE
	# echo $LINK
	echo $ID
	echo "--"
done
