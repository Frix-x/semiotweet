# <img src="viewer/static/images/semiotweet.jpg" width="60" height="60" alt = "Logo"/> Semiotweet
Tweets analysis from politics.

## What's the goal

_Semiotweet_ aims to better understand the tweets posted by politics.
It shows what are the most commons words in those tweets, and what are the different semantic fields related to them.


## How it works
Stack is subjects to know changes.

### Back-end :
 - Django,
 - SQLite
 - Twitter API,

### Front-end ; to be chosen between :
 - D3.js
 - chart.js
 - anychart
 - canvasjs
 - c3.js
 - chartist.js
 - flot
 - p5.js

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
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements
```

You have to set some variables in yout virtual env.
First the "secret key" the DEBUG variable for the app (needed by Django). DEBUG is set to True for dev', false for production.
```
$ export SECRET_KEY='someLongStringToImagine'
$ export DEBUG='True'
```
Then the credentials (for user and consumer)for your app in order to use Twitter API.
In order to have those string, you need to create a Twitter App (see [here](https://apps.twitter.com/app/13440041/show)) ; then you can copy-paste them to set them in your virtual env.
```
$ export CONSUMER_KEY='someLongStringToImagine'
$ export CONSUMER_SECRET='someLongStringToImagine'
$ export KEY='someLongStringToImagine'
$ export SECRET='someLongStringToImagine'
```
Then you can run :
```
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py runserver
```

## Things done
  - Connection to Twitter API (100%)
  - Basic architecture (100%)
  - Defining models (100%)
  - Defining Env' Variables (100%)
  - Extracting user info (80%)
  - Extracting old tweet (60%)

## Things to do :
  - Getting all the users at once
  - Extract new tweet (40%)
  - Semantic fields
  - JS libraries
  - Deployement on Heroku
  - README.md

## Ressources

  - Logo from [graphicdesignblg](https://www.instagram.com/graphicdesignblg/ "graphicdesignblg on Instagram")
  - [Twitter API documentation](https://dev.twitter.com/ "Twitter API documentation")
  - Marco Bonzanini, [Mining Twitter Data with Python](https://marcobonzanini.com/2015/03/02/mining-twitter-data-with-python-part-1/ "Mining Twitter Data with Python")
