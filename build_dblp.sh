DIR=`dirname $0`
echo "creating database, if it doesn't already exist"
python $DIR/lib/mocs_database.py
echo "starting dump of dblp metadata into database"
(cat $DIR/header.xml; curl http://dblp.uni-trier.de/xml/dblp.xml 2> /dev/null | tail -n +3) | python $DIR/lib/build_dblp_database.py
echo "memoizing terms"
python $DIR/lib/memoize_terms.py
