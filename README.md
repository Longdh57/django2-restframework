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
`git clone git@gitlab.com:long.daohai4894/sale-portal-v2.git sale_portal_v2`

**Install and create virtualenv**  
`cd sale_portal_v2`
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
`sudo -u postgres psql      # Login to postgres-cli`
`CREATE DATABASE sp;`
`CREATE USER sp_user;`
`ALTER USER sp_user with encrypted password 'secret';`
`ALTER USER sp_user WITH SUPERUSER;`
`GRANT ALL PRIVILEGES ON DATABASE sp TO sp_user;`

**Re-check connection to database in .env file and run migrate**  
```python manage.py migrate```

**Create a superuser**  
`python manage.py createsuperuser`

**Run project**  
For Backend: `python manage.py runserver`
For Frontend: `python manage.py runserver --setting=sale_portal.setting_fe`  

## Make demo data
**Link to download file sql to import [sp.sql](https://drive.google.com/drive/folders/1HIuoYAJH17lKmBL1Qa2ZvMsaKaESzLVV?usp=sharing)


# Author
Maintainer: Dinh Huy Binh
Developer: [Hai Long Dao](http://longblog.info)
Developer: Nguyen The Chi Dung
_============VNpay Sale Portal 04/11/2019============_
