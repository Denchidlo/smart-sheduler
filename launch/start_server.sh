#!/bin/bash

ngrok http 8080 > /dev/null & 
sleep 3
curl  http://localhost:4040/api/tunnels > ngrok_tmp.json
echo "ngrok server launched"

python get_domain.py
rm ngrok_tmp.json
echo "appconfig.json configured"

cd ../baseapp

python manage.py runserver 0:8080
echo "Server up"