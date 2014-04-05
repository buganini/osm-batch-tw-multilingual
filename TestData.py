# -*- coding: utf-8 -*-

import os
import sys
import osmapi
import urllib
import pickle

class TestData():
	data = {
		"node":[
			{
				u"lat":42,
				u"lon":42,
				u"tag":{}
			},
			{
				u"lat":42.001,
				u"lon":42.001,
				u"tag":{}
			}
		],
		"way":[
			{
				u"nd":[0,1],
				u"tag":{
					u"test":u"1",
					u"name":u"te,.0st"
				}
			},
			{
				u"nd":[0,1],
				u"tag":{
					u"test":u"2",
					u"name":u"測,.0試"
				}
			},
			{
				u"nd":[0,1],
				u"tag":{
					u"test":u"3",
					u"name":u"測,-.0試 (te,-.s0t)"
				}
			},
			{
				u"nd":[0,1],
				u"tag":{
					u"test":u"4",
					u"name":u"測,-.0試 te,-.s0t"
				}
			},
			{
				u"nd":[0,1],
				u"tag":{
					u"test":u"5",
					u"name":u"te,-.0st (測,-.0試)"
				}
			},
			{
				u"nd":[0,1],
				u"tag":{
					u"test":u"6",
					u"name":u"te,-.0st 測,-.0試"
				}
			},
			{
				u"nd":[0,1],
				u"tag":{
					u"test":u"7",
					u"name":u"測,.0試 (ȁȅȉȍȑȕȀȄȈȌ,-.Ȑ0Ȕ)"
				}
			},
			{
				u"nd":[0,1],
				u"tag":{
					u"test":u"8",
					u"name":u"測,.0試 ȁȅȉȍȑȕȀȄȈȌ,.Ȑ0Ȕ"
				}
			},
			{
				u"nd":[0,1],
				u"tag":{
					u"test":u"9",
					u"name":u"ȁȅȉȍȑȕȀȄȈ0Ȍ,.0ȐȔ (測,.0試)"
				}
			},
			{
				u"nd":[0,1],
				u"tag":{
					u"test":u"10",
					u"name":u"ȁȅȉȍȑȕȀȄȈ0Ȍ,.ȐȔ 測,.0試"
				}
			},
		]
	}

	data_rt = {"node":[], "way":[]}

	devapi = "api06.dev.openstreetmap.org"

	picklefile = "testdata.dat"

	@classmethod
	def gen(cls):
		print "Generating test data..."
		if os.path.exists(cls.picklefile):
			cls.clean_pickle()
		from setting import username, password
		api = osmapi.OsmApi(api = cls.devapi, username = username, password = password)

		api.ChangesetCreate({u"comment": u"test data"})

		for node in cls.data["node"]:
			node_rt = api.NodeCreate(node)
			cls.data_rt["node"].append(node_rt)

		for way in cls.data["way"]:
			nd = [cls.data_rt["node"][node_sn][u"id"] for node_sn in way[u"nd"]]
			way_rt = api.WayCreate({u"nd":nd, u"tag":way[u"tag"]})
			cls.data_rt["way"].append(way_rt)

		api.ChangesetClose()
		pickle.dump(cls.data_rt, open(cls.picklefile, "w"))

	@classmethod
	def fetchosm(cls):
		u = urllib.urlopen("http://"+cls.devapi+"/api/0.6/map?bbox=42,42,42.25,42.25")
		osm = u.read()
		return osm

	@classmethod
	def fetchosmfile(cls, p):
		osm = cls.fetchosm()
		f=open(p, "w")
		f.write(osm)
		f.close()

	@classmethod
	def clean(cls):
		print "Cleanup test data..."
		from setting import username, password
		api = osmapi.OsmApi(api = cls.devapi, username = username, password = password)

		api.ChangesetCreate({u"comment": u"test data"})

		for way in cls.data_rt["way"]:
			while True:
				try:
					api.WayDelete(way)
					break
				except:
					way[u"version"]+=1
					continue

		for node in cls.data_rt["node"]:
			api.NodeDelete(node)

		api.ChangesetClose()
		os.remove(cls.picklefile)

	@classmethod
	def clean_pickle(cls):
		data_rt_bak=cls.data_rt
		cls.data_rt=pickle.load(open(cls.picklefile))
		cls.clean()
		cls.data_rt=data_rt_bak
