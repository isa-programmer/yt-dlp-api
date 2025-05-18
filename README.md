# A Rest-api for yt-dlp written in Flask

- [x] Autocomplete search
- [x] Video information
- [x] Video formats
- [x] Searching
- [ ] channel information


- requiretmens
 - yt-dlp
 - Flask


```bash
git clone https://github.com/isa-programmer/yt-dlp-api
cd yt-dlp-api/src
flask run --debug --port=3000
```

API endpoints
```bash
curl "http://localhost:3000/autocomplete?q=Python%203.11"
curl "http://localhost:3000/formats?id=dQw4w9WgXcQ"
curl "http://localhost:3000/video?id=dQw4w9WgXcQ"

```

>This project still under beta