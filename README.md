# <img src="viewer/static/images/semiotweet.jpg" width="60" height="60" alt = "Logo"/> Semiotweet
Tweets analysis from politics.

## What's the goal

_Semiotweet_ aims to better understand the tweets posted by politics.
It shows what are the most commons words in those tweets, and what are the different semantic fields related to them.


## How it works
Stack is subjects to know changes.

### Back-end :
 - Django,
 - SQLite,
 - Twitter API,

### Front-end ; to be chosen between :
 - D3.js
 - chart.js
 - vis.js

## Architecture, data structures & models

There's just one app called `viewer` yet. `urls.py` directly redirects to this app.
`extraction.py` contains functions that are used in the views.

There are only two models : `Tweet` and `User` :
![DataBase](UML.png)

Those models may change with new features.

Templates are directly put in `viewer/templates/` and not as usual in `viewer/templates/viewer` as it can be the case in most of Django apps.

## How to install

Clone it. Go to the folder and :
```
# For Python 3.6
$ virtualenv -p /usr/bin/python3 venv3
$ source venv3/bin/activate

# For Python 2.7
$ virtualenv venv
$ source venv/bin/activate

# Then install the requirements
$ pip install -r requirements.txt
# If you have the error 'pg_config not found' : sudo apt install libpq_dev
# If you have the error 'could not run curl-config' : sudo apt install libcurl4-openssl-dev
# Then re-install the requirements
```

You have to set some variables in yout virtual env.
First the "secret key" for the app (needed by Django).
```
$ export SECRET_KEY='someLongStringToImagine'
```
Then the credentials (for user and consumer)for your app in order to use Twitter API.
In order to have those string, you need to create a Twitter App (see [here](https://apps.twitter.com/app/13440041/show)) ; then you can copy-paste them to set them in your virtual env.
```
$ export CONSUMER_KEY='someLongStringToImagine'
$ export CONSUMER_SECRET='someLongStringToImagine'
$ export KEY='someLongStringToImagine'
$ export SECRET='someLongStringToImagine'
```
You have to create a `local_settings.py` in the same folder as `setting.py` in order to extend this file (see the end of `setting.py`) ; this is useful for managing different
data base between local development and deployement :
```
$ touch local_settings.py
$ pip install dj_database_url
```
In this file are the settings set to use the local database (`DEBUG` is set to True for dev', false for production.) :

```
# Local settings : used for local development.
from settings import PROJECT_ROOT, BASE_DIR
import os

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

```
Then you have to run this in order to set up the models and the database :
```
$ python manage.py makemigrations
$ python manage.py migrate
```
Finally, `$ python manage.py runserver` runs the server locally.

## Getting users data and tweets

Once the server is running, you can extact the data concerning the users and their tweets by clicking on `Update Data` or by getting to `http://127.0.0.1:8000/getData/`

## Project Progress

| Things done                                                         | Things to do                  |
| -------------                                                       | -------------                 |
| Connection to Twitter API (100%)                                    | Semantic fields (30%)         |
| Basic architecture (100%)                                           | JS libraries (70 %)           |
| Defining models (100%)                                              | Deployement on Heroku (80%)   |
| Defining Env' Variables (100%)                                      | README.md (60%)               |
| Extracting user info (100%)                                         ||
| Extracting old tweets (100%)                                        ||
| Extracting latest tweets (100%)                                     ||
| Modular code for extraction (100%)                                  ||
| Getting all the users at once (100%)                                ||
| Extract new tweet (100%)                                            || |


## Usefull Ressources

  - Logo from [graphicdesignblg](https://www.instagram.com/graphicdesignblg/ "graphicdesignblg on Instagram")
  - [Twitter API documentation](https://dev.twitter.com/ "Twitter API documentation")
  - [Map of a Twitter Status Object](http://www.slaw.ca/wp-content/uploads/2011/11/map-of-a-tweet-copy.pdf "Map of a Twitter Status"), Raffi Krikorian
  - Marco Bonzanini, [Mining Twitter Data with Python](https://marcobonzanini.com/2015/03/02/mining-twitter-data-with-python-part-1/ "Mining Twitter Data with Python")
  - [Migrating Your Django Project to Heroku](https://realpython.com/blog/python/migrating-your-django-project-to-heroku/ "Migrating Your Django Project to Heroku")
