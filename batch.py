import os
import sys
import re
import osmapi
from imposm.parser import OSMParser
from TestData import TestData

cjk="\u3400-\u4DB5\u4E00-\u9FA5\u9FA6-\u9FBB\uF900-\uFA2D\uFA30-\uFA6A\uFA70-\uFAD9\u20000-\u2A6D6\u2F800-\u2FA1D\uFF00-\uFFEF\u2E80-\u2EFF\u3000-\u303F\u31C0-\u31EF"
containZh = re.compile(ur"^.*?[" + cjk + ur"]+.*$")
containEn = re.compile(ur"^.*?[^" + cjk + ur"]{3,}.*$")
allEn = re.compile(ur"^[^" + cjk + ur"]{3,}$")
allZh = re.compile(ur"^.*?[" + cjk + ur"0-9]+.*$")

def chunks(l, n):
	for i in xrange(0, len(l), n):
		yield l[i:i+n]

def name_en_zh(tags):
	tags_name = tags.get(u"name", "")
	tags_name_en = tags.get(u"name:en", "")
	tags_name_zh = tags.get(u"name:zh", "")

class Handler():
	def __init__(self):
		self.ways=[]
	def waysHandler(self, ways):
		for way in ways:
			osmid, tags, refs = way
			needUpdate=False
			if u"name" in tags and containZh.match(tags[u"name"]) and u"name:zh" not in tags:
				needUpdate=True
			if u"name" in tags and containEn.match(tags[u"name"]) and u"name:en" not in tags:
				needUpdate=True
			if needUpdate:
				self.ways.append(way)

	def getWays(self):
		return self.ways

if len(sys.argv)<2:
	sys.exit()

# DON'T CHANGE
testing=True

if testing:
	apiurl = "api06.dev.openstreetmap.org"
	TestData.gen()
	TestData.fetchosmfile(sys.argv[1])
else:
	apiurl = "api.openstreetmap.org"

handler=Handler()
p = OSMParser(ways_callback=handler.waysHandler)
p.parse(sys.argv[1])

from setting import *
api = osmapi.OsmApi(api=apiurl, username = username, password = password)
cap = int(api.Capabilities()[u"waynodes"][u"maximum"])

for chunk in chunks(handler.getWays(), 10):
	ways_id=[way[0] for way in chunk]
	ways=api.WaysGet(ways_id)
	print ways
	print ""
	if not ways:
		continue

	api.ChangesetCreate({u"comment": u"multilingual update #https://github.com/buganini/osm-batch-tw-multilingual"})

	for way_id in ways:
		ways[way_id][u"tag"][u"name"]="lala"
		api.WayUpdate(ways[way_id])

	api.ChangesetClose()

	for way_id in ways:
		print api.WayGet(way_id)

if testing:
	print TestData.fetchosm()
	TestData.clean()
