import json
import requests
import subprocess
from flask import Flask, request, View

app = Flask(__name__)

class YoutubeAutoComplete(View):
	def get(self):
		query = request.forms.get('q')
		return "coming soon"


class YoutubeSearch(View):
	def get(self):
		query = request.forms.get('query')
		limit = int(request.forms.get('limit',10))
		if limit > 30:
			limit = 30
		if limit <= 0:
			return {"err":"Limit can't be lower than 1"}
		resp = subprocess.run([
			"yt-dlp",
			f"ytsearch{limit}:{query}",
			"--dump-json",
			"--default-search","ytsearch",
			"--geo-bypass","--no-playlist","--no-check-certificate",
			"--flat-playlist","--skip-download","--quiet","--ignore-errors"
			],capture_output=True,text=True)
		if resp.returncode != 0:
			return {"err":resp.stderr,"results":[]}
		try:
			return {"results":[json.loads(line) for line in resp.stdout.strip().splitlines()]}
		except Exception as err:
			return {"err":err}

class YoutubeVideoInfo(View):
	def get(self):
		video_id = request.forms.get('id')


class YoutubeVideoFormats(View):
	"""
	 This class, returns the video formats from id.
	 	Usage:
	 		/api/v1/formats/:id
	"""
	def get(self):
		video_id = request.forms.get('id','')

		if not video_id or len(video_id) != 11:
			return {"err",f"{video_id} is not a valid youtube video id! "},400
		try:
			url = f"https://youtube.com/watch?v={video_id}"
			resp = subprocess.run(['yt-dlp','-JF',url],capture_output=True,text=True)
		
		except subprocess.CalledProcessError:
			return {"err":f"Subprocess call failed!"},500
		
		except Exception as err:
			return {"err":f"Unexpected error:{err}"},500


		if resp.returncode != 0:
			return {"err":f"Unexpected error:{resp.stderr}"},500
		
		json_start = resp.stdout.find('{')

		if json_start == -1:
			return {"err":"No format avaible"}
		
		try:

			return json.loads(resp.stdout[json_start:]),200

		except json.JSONDecodeError:
			return {"err":"Failed to decode JSON!"},500
		
		except Exception as err:
			return {"err":f"Unexpected error:{err}"},500


endpoints = [
	{"url":"/api/v1/search","func":YoutubeSearch,"name":"youtube_search"},
	{"url":"/api/v1/video","func":},
	{"url":"/api/v1/autocomplete","func":}
]



if __name__ == "__main__":
	for endpoint in endpoints:
		app.add_url_rule(endpoint['url'],endpoint['func'].as_view(endpoint['name']))
	app.run()
