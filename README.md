# password-flask
##
## Notes:
 
This is a password safe, written in python, templated and served using flask, and done as a learning excercise for myself; there is  room for great improvement.

The use cases are very simple:

1) allow for storing passwords for a user 
2) allow for storing team passwordsfor a group
3) allow for grouping of passwords by groups
4) audit access and password modifications

## Some concepts:
1) we  use sqlalchemy to access our database, and we try to leverage this to make the program database agnostic.

the configuration of our database is found in loadAlchemy.py, and by default it is using sqlite:///database.db
MS SQL has been tested as well, so you can change it to an MS SQL database uri pointing to an existing database, and it will create the tables there.

2) to create and manage all the db tables, we use alembic.  After defining the sqlalchemy configuration, on can run

manage.py and it will create all the tables defined in models.py

3) Because the application needs some basic management functions, like editing users, creating groups for users and secrets, when you start the program, it will create the following groups, which are defined in load_groups.py
  PWFlaskAdmin
  General
 
 users in PWFlaskAdmin group are administrators.
 
4) user creation is self-serve; 
The first user (id = 1) is an admin by default, so use a generic account for it.
 
5) subsquent new users go into the General group and don't have secrets.

6) with the first user, you can create some groups, and define what groups new users belong to, so that you can have multiple PWFlaskAdmin's and protect your team secrets.

7) secrets are stored in the db encrypted using rsa with a keylenght of 512. you can alter this in rsa_key_management.py.

it is very important to understand that the secrets that are created, are done so with the public.pem that is created upon first run.
These secrets can only be viewed with the private.pem.  If you corrupt or lose this pair, all the secrets stored in your db are pretty much lost forever.

these keys are the trick to the safekeeping of your password secrets in your database, so take good care of them and do not expose them.

TODO:
1) create assetgroup interface;   assetgroups are how secrets are grouped according to type ( asset types or however you group alike assets)
      Esentially I wrote this so that this information, is fed from our CMDB, so that part I'm leaving out of this project for  now (24/01/2023)

2) test password encryption for > 512 keylength. should be fairly easy to do, as the db.column type for Asset.assetpwd is Text.

3) see of a means to have the password keys stored in an encrypted database....or something that would leave the public.pem and private.pem so fragile

## Set up & Installation.


### 1 .Clone/Fork the git repo and create an environment 
                    
**Windows**
          
```bash
git clone https://github.com/josemiguelferreiraorg/password-flask.git
cd password-flask
py -3 -m venv venv

```
          
**macOS/Linux**
          
```bash
git clone https://github.com/josemiguelferreiraorg/password-flask.git
cd password-flask
python3 -m venv venv

```

### 2 .Activate the environment
          
**Windows** 

```venv\Scripts\activate```
          
**macOS/Linux**

```. venv/bin/activate```
or
```source venv/bin/activate```

### 3 .Install the requirements

Applies for windows/macOS/Linux

```
cd main
pip install -r requirements.txt
```
### 4 .Migrate/Create a database

```python manage.py```

### 5. Run the application 

python wsgi.py


for production, we install uvicorn and gunicorn and packaged it up using docker with the following docker file:

FROM centos/python-36-centos7

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

#CMD [ "python3", "-m" , "wsgi", "run", "--host=0.0.0.0"]
EXPOSE 8080
CMD [ "gunicorn",  "wsgi:app", "-b 0.0.0.0:8080", "--reload" ]




