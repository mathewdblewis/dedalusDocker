docker build -t app .
docker exec `docker run -dit app` /bin/bash -c \
'source activate dedalus2; cd files; python3 search.py; tar -czf temp.zip output; python3 disp.py temp.zip' > res.txt
python3 decode.py
rm res.txt
tar -xf res.zip
