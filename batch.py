import sys
import re
from imposm.parser import OSMParser

cjk="\u3400-\u4DB5\u4E00-\u9FA5\u9FA6-\u9FBB\uF900-\uFA2D\uFA30-\uFA6A\uFA70-\uFAD9\u20000-\u2A6D6\u2F800-\u2FA1D\uFF00-\uFFEF\u2E80-\u2EFF\u3000-\u303F\u31C0-\u31EF"
containZh = re.compile(ur"^.*?[" + cjk + ur"]+.*$")
containEn = re.compile(ur"^.*?[^" + cjk + ur"]{3,}.*$")
allEn = re.compile(ur"^[^" + cjk + ur"]{3,}$")
allZh = re.compile(ur"^.*?[" + cjk + ur0-9"]+.*$")

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
				self.ways.append(osmid)
				name=tags[u"name"]

	def getWays(self):
		return self.ways

handler=Handler()
p = OSMParser(ways_callback=handler.waysHandler)
p.parse(sys.argv[1])

#print handler.getWays()
