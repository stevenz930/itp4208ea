email: admim
pw: admin

eaBackend:
python manage.py runserver 8080

check bug:
python manage.py check
py manage.py check

check models changes:
python manage.py makemigrations
py manage.py makemigrations

change models:
python manage.py migrate
py manage.py migrate

add random data:
python manage.py generate_data
py manage.py generate_data

clean data:
python manage.py cleanup_data 
py manage.py cleanup_data 

source venv/bin/activate