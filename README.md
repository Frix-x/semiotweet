# semiotweet
Tweets analysis from politics.
Uses Django and the twitter API and D3.js

# TODO : the next steps :
 1. extracts users ' info
 1. extracts users ' tweets
 2. stemming words from them
 3. front-end using D3.js

# To install

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

# How it works

This is a classic website using Django. There's just one app called `viewer` yet. `urls.py` directly redirects to this app.
`extraction.py` contains functions that are used in the views.

There are only two models : `Tweet` and `User` :
![DataBase](UML.png)

Templates are directly put in `viewer/templates/` and not as usual in `viewer/templates/viewer` as it can be the case in most of Django apps.
