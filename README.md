##Testing
	python batch.py test.osm
	
	#Verifying cleanup
	wget -O /dev/stdout "http://api06.dev.openstreetmap.org/api/0.6/map?bbox=42,42,42.25,42.25"
	
##DANGEROUS

	wget http://download.geofabrik.de/asia/taiwan-latest.osm.pbf
	python batch.py taiwan-latest.osm.pbf
