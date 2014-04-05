import os
import sys
import re
import osmapi
from imposm.parser import OSMParser
from TestData import TestData

cjk=ur"\u3400-\u4DB5\u4E00-\u9FA5\u9FA6-\u9FBB\uF900-\uFA2D\uFA30-\uFA6A\uFA70-\uFAD9\U00020000-\U0002A6D6\U0002F800-\U0002FA1D\uFF00-\uFFEF\u2E80-\u2EFF\u3000-\u303F\u31C0-\u31EF"
common=ur"0-9,. _-"
containZh = re.compile(u"^.*?[" + cjk + common + u"]+.*$")
containEn = re.compile(u"^.*?[^" + cjk + u"]{3,}.*$")
allEn = re.compile(u"^[^" + cjk + u"]+$", re.UNICODE)
allZh = re.compile(u"^[" + cjk + common + u"]+$")
zh_q_en=re.compile(u"^([" + cjk + common + u"]+) *\\(([^" + cjk + u"()]+)\\)$")
zh_en=re.compile(u"^([" + cjk + common + u"]+) *([^" + cjk + u"()]+)$")
en_q_zh=re.compile(u"^([^" + cjk + u"()]+) *\\(([" + cjk + common + u"]+)\\)$")
en_zh=re.compile(u"^([^" + cjk + u"()]+) *([" + cjk + common + u"]+)$")

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

# DANGEROUS
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
	if not ways:
		continue

	api.ChangesetCreate({u"comment": u"multilingual update #https://github.com/buganini/osm-batch-tw-multilingual"})

	for way_id in ways:
		updated=False

		if not updated:
			r=allEn.match(ways[way_id][u"tag"][u"name"])
			if r:
				if u"name:en" not in ways[way_id][u"tag"]:
					updated=True
					if testing:
						ways[way_id][u"tag"][u"rule"]="1"
					ways[way_id][u"tag"][u"name:en"]=ways[way_id][u"tag"][u"name"].strip()

		if not updated:
			r=allZh.match(ways[way_id][u"tag"][u"name"])
			if r:
				if u"name:zh" not in ways[way_id][u"tag"]:
					updated=True
					if testing:
						ways[way_id][u"tag"][u"rule"]="2"
					ways[way_id][u"tag"][u"name:zh"]=ways[way_id][u"tag"][u"name"].strip()

		if not updated:
			r=zh_q_en.match(ways[way_id][u"tag"][u"name"])
			if r:
				updated=True
				if testing:
					ways[way_id][u"tag"][u"rule"]="3"
				ways[way_id][u"tag"][u"name"]=r.group(1).strip()
				if u"name:zh" not in ways[way_id][u"tag"]:
					ways[way_id][u"tag"][u"name:zh"]=r.group(1).strip()
				if u"name:en" not in ways[way_id][u"tag"]:
					ways[way_id][u"tag"][u"name:en"]=r.group(2).strip()

		if not updated:
			r=zh_en.match(ways[way_id][u"tag"][u"name"])
			if r:
				updated=True
				if testing:
					ways[way_id][u"tag"][u"rule"]="4"
				ways[way_id][u"tag"][u"name"]=r.group(1).strip()
				if u"name:zh" not in ways[way_id][u"tag"]:
					ways[way_id][u"tag"][u"name:zh"]=r.group(1).strip()
				if u"name:en" not in ways[way_id][u"tag"]:
					ways[way_id][u"tag"][u"name:en"]=r.group(2).strip()

		if not updated:
			r=en_q_zh.match(ways[way_id][u"tag"][u"name"])
			if r:
				updated=True
				if testing:
					ways[way_id][u"tag"][u"rule"]="5"
				ways[way_id][u"tag"][u"name"]=r.group(2).strip()
				if u"name:en" not in ways[way_id][u"tag"]:
					ways[way_id][u"tag"][u"name:en"]=r.group(1).strip()
				if u"name:zh" not in ways[way_id][u"tag"]:
					ways[way_id][u"tag"][u"name:zh"]=r.group(2).strip()

		if not updated:
			r=en_zh.match(ways[way_id][u"tag"][u"name"])
			if r:
				updated=True
				if testing:
					ways[way_id][u"tag"][u"rule"]="6"
				ways[way_id][u"tag"][u"name"]=r.group(2).strip()
				if u"name:en" not in ways[way_id][u"tag"]:
					ways[way_id][u"tag"][u"name:en"]=r.group(1).strip()
				if u"name:zh" not in ways[way_id][u"tag"]:
					ways[way_id][u"tag"][u"name:zh"]=r.group(2).strip()

		if updated:
			api.WayUpdate(ways[way_id])
		else:
			print "NOOP: "+str(ways[way_id])

	api.ChangesetClose()

if testing:
	print TestData.fetchosm()
	TestData.clean()
