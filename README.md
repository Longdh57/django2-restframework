# CMS Vnpay Sale Portal
 
# Main Function
*- Frontend:*  
Provide a System which helps Sale manager can manage sale staff. Application version 1 use framework Django version 2.2.7 to develop.  
*- Backend:*  
Provide backend system to connect and control action from UI to Database. Use framework Django version 2.2.7 to develop.

## Requirement
- [Python](https://www.python.org/) 3.6 or newer  
- [Postgres Sql](https://www.postgresql.org/) 10 or newer  
- [Virtualenv](https://virtualenv.pypa.io/en/latest/)

## Installation
**Clone from git**  
`git clone git@gitlab.com:long.daohai4894/sale-portal-v2.git`  

**Install and create virtualenv**  
`cd sales-portal`  
`virtualenv -p python3 .venv`  
`source .venv/bin/activate`  

**Pip Install in virtualenv**  
`pip install -r requirements.txt`  

**Copy & create .env**  
`cp .env.sample .env`  

**Setup Variable Environtment in .env, includes**   
`EMAIL_HOST_USER` 
`EMAIL_HOST_PASSWORD`  # both to send report email

`FRONTEND_URL`  # to disable CORS for api

`SOCIAL_AUTH_GOOGLE_OAUTH2_KEY`  
`SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET` # both to login via google oauth2 function 
 
`GEODATA_GOOGLE_ACCOUNT_TOKEN`  # to call Gmaps API to get Lon, Lat

**Create a Postgres Database in system**  
`sudo -u postgres psql`  
`CREATE DATABASE sms;`  
`CREATE USER sms_user;`  
`ALTER USER sms_user with encrypted password 'secret123';`  
`ALTER USER postgre_tutorial WITH SUPERUSER;`  
`GRANT ALL PRIVILEGES ON DATABASE sms TO sms_user;`  

**Re-check connection to database in .env file and run migrate**  
`python manage.py migrate --setting=sale_portal.setting_be`  

**Create a superuser**  
`python manage.py createsuperuser --setting=sale_portal.setting_be`

**Run project**  
For Backend: `python manage.py runserver --setting=sale_portal.setting_be`  
For Frontend: `python manage.py runserver --setting=sale_portal.setting_fe`  

## Clone data from server
**Make sure you can connection to MMS_DB_NAME (recheck in file .env and .env.sample)  
Run command:**
- `python manage.py qr_province_sync` 
- `python manage.py qr_district_sync` 
- `python manage.py qr_ward_sync` 

- `python manage.py first_time_synchronize_qr_department` 
- `python manage.py first_time_synchronize_qr_merchant` 
- `python manage.py first_time_synchronize_qr_staff` 
- `python manage.py first_time_synchronize_qr_terminal` 

- `python manage.py first_time_synchronize_staff` 
- `python manage.py first_time_synchronize_merchant` 
- `python manage.py first_time_synchronize_terminal` 

## Author
Developer: [Hai Long Dao](http://longblog.info)  
_============VNpay Sale Portal 04/11/2019============_
