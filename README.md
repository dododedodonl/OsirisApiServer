# OsirisApiServer
## Description
This repo contains the source code for the unofficial API of Osiris at TU/e. It has two parts: `OsirisAPI.py` conaining the OsirisAPI. This handles all interaction with Osiris itself located on [https://osiris.tue.nl/](https://osiris.tue.nl/). The other part is `OsirisApiServer.py` which is a simple wrapper written using the [Flask framework](http://flask.pocoo.org/).

The Flask app is an example on how to use the API. It utilizes caching and the OsirisAPI class to provide a full fledged REST API experience. Please note that the API is read only and unauthenticated.

## Usage
To host the API install python as well as the dependencies listed in `requirements.txt` with pip. Read the flask documentation on deploying Flask apps to production. The Flask cache uses a redis instance, this is the only extra dependency besides python. For a local instance of the api it is enough to run `python OsirisApiServer.py` while also having a redis server up on localhost.

## Endpoints
The API endpoints are documented on the index html page. This will render to:
![image of endpoints](https://i.imgur.com/qZXPGU8.png)

## Real world uses
The Osiris API is used in the Master Marketplace of the TU/e to grab reliable course data. It can be accessed at [https://osiristue.nl/osiris/](https://osiristue.nl/osiris/) or [https://master.ele.tue.nl/osiris/](https://master.ele.tue.nl/osiris/), both point to the same hosted instance. The marketplace system is build in the [Django framework](https://www.djangoproject.com/) but uses the same OsirisAPI class as in this repo.

The interface on [https://osiristue.nl/](https://osiristue.nl/) also uses this API. In the background it connects to the API hosted on the Master Marketplace. This system is also open sources, see other repos of Kolibri Solutions.

## Technical details
The API uses the public catalog of Osiris and manipulates the GET arguments in the link to query information from it. It then parses the results with beautiful soup and compiles the information into a json object. It then caches the results.

## Acknowledgments
This API was developed for usage with the [Master Marketplace](https://master.ele.tue.nl/), created for the ELE department of the TU/e. Development and support done by Kolibri Solutions. For questions or inquiries contact info@kolibrisolutions.nl.

All rights reserved. All product names, logos, and brands are property of their respective owners.  Use of these names, logos, and brands does not imply endorsement.
