cd ../../
source ./telebot-env/bin/activate

echo "Enviroment setup complete"

cd /source/launch
cd /launch
ngrok http --config=ngrok.yml 8000
curl  http://localhost:4040/api/tunnels > ngrok_tmp.jsom
echo "ngrok server launched"

python get_domain.py
rm ngrok_tmp.json
echo "appconfig.json configured"

cd ../baseapp

python -m django makemigrations
python -m django migrate
echo "migrations resolved"

python manage.py runserver
echo "Server up"