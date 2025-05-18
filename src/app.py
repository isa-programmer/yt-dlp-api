import ast
import json
import requests
import subprocess
from flask import Flask, request
from flask.views import MethodView
app = Flask(__name__)

class YoutubeAutoComplete(MethodView):
	def get(self,):
		query = request.args.get('q','')
		if not query:
			return {"err":"Empty input"}
		headers = {
    		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
		}

		params = {
    		'client': 'youtube',
    		'q': query,
		}
		try:
			response = requests.get('https://suggestqueries-clients6.youtube.com/complete/search',
									params=params,headers=headers)
		except Exception as err:
			return {"err":err}
		if not response.ok:
			return {"err":"Request failed with {response.status_code}"}
		return [suggest[0] for suggest in ast.literal_eval(response.text[19:-1])[1]]

class YoutubeChannel(MethodView):
	def get(self,channel_id):


class YoutubeSearch(MethodView):
	def get(self):
		query = request.args.get('query')
		limit = int(request.args.get('limit',10))
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

class YoutubeVideoInfo(MethodView):
	def get(self):
		video_id = request.args.get('id')
		resp = subprocess.run(
			['yt-dlp','-J',f"https://youtube.com/watch?v={video_id}"],
			capture_output=True,
			text=True
			)
		print(f"https://youtube.com/watch?v={video_id}")
		if resp.returncode != 0:
			{"err":resp.stderr}
		try:
			json_data = json.loads(resp.stdout)
		except Exception as err:
			{"err":err}
		clean_response = {}
		for key in ["id","uploader","uploader_id",
					"title","tags","duration",
					"thumbnail","like_count",
					"comment_count","description","view_count",
					"categories","upload_date","chapters"]:
			clean_response[key] = json_data.get(key)
		return clean_response


class YoutubeVideoFormats(MethodView):
	"""
	 This class, returns the video formats from id.
	 	Usage:
	 		/api/v1/formats/:id
	"""
	def get(self):
		video_id = request.args.get('id')

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


app.add_url_rule("/autocomplete",view_func=YoutubeAutoComplete.as_view("autocomplete"))
app.add_url_rule("/formats",view_func=YoutubeVideoFormats.as_view("formats"))
app.add_url_rule("/video",view_func=YoutubeVideoInfo.as_view("video"))
if __name__ == "__main__":
	app.run()
