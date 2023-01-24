# password-flask
##
## Set up & Installation.
##

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
# syntax=docker/dockerfile:1

FROM centos/python-36-centos7

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

#CMD [ "python3", "-m" , "wsgi", "run", "--host=0.0.0.0"]
EXPOSE 8080
CMD [ "gunicorn",  "wsgi:app", "-b 0.0.0.0:8080", "--reload" ]




