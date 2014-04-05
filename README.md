##Setting

	#setting.py
	username="_username_"
	password="_password_"

##Testing

	python batch.py test.osm

	#Data before update is in test.osm
	#Data after update is printed

	#Verifying cleanup
	wget -O /dev/stdout "http://api06.dev.openstreetmap.org/api/0.6/map?bbox=42,42,42.25,42.25"

##DANGEROUS

	disable testing
	wget http://download.geofabrik.de/asia/taiwan-latest.osm.pbf
	python batch.py taiwan-latest.osm.pbf

##Todo
	Sec./Rd.
