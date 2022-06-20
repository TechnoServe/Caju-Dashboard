# Caju-Dashboard
> The Satellite Dashboard is a remote sensing dashboard created to map satellite growing areas in Benin, using satellite imagery and machine learning algorithms. The dashboard will help field teams improve operations and policy makers make better decisions

![GitHub](https://img.shields.io/github/license/Technoserve/Caju-Dashboard-v2)
![PyPI - Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9-blue)
![Maintenance](https://img.shields.io/maintenance/yes/2022)
![Website](https://img.shields.io/website?down_color=red&down_message=offline&up_message=online&url=https%3A%2F%2Fcajuboard.tnslabs.org)

![](https://i.ibb.co/zmSTb1N/Capture-d-cran-2022-06-02-120227.png)

## Requirements  (Prerequisites)
Tools and packages required to successfully install this project.
For example:
* Linux, Windows or MacOS
* [Python 3.9](https://www.python.org/downloads/release/python-3913/)
* [MySQL database](https://dev.mysql.com/doc/)

## Setup

The first thing to do is to clone the repository:

```sh
$ git clone https://github.com/TechnoServe/Caju-Dashboard-v2.git
$ cd Caju-Dashboard-v2
```

Create a virtual environment to install dependencies in and activate it:

```sh
$ python3 -m venv env
$ source env/bin/activate
```

Then install the dependencies:

```sh
(env)$ pip install -r requirements.txt
```
Note the `(env)` in front of the prompt. This indicates that this terminal
session operates in a virtual environment set up previously.

Once `pip` has finished downloading the dependencies, run migrations with following command:

```sh
(env)$ python3 manage.py migrate --skip-checks
```



Then, create a `.env` file in the root of the project with following content:

```sh
TIMES=2

#Dashboard DB credentials
NAME='YOUR DATABASE NAME HERE'
USER='YOUR DATATBASE USERNAME HERE'
PASSWORD='YOUR DATABASE USER PASSWORD HERE'
HOST=YOUR DATABASE SERVER HOSTNAME HERE
PORT='YOUR DATABASE SERVER PORT HERE'

#CAJU-APP credentials
SQL_HOSTNAME=''
SQL_USERNAME=''
SQL_PASSWORD=''
SQL_DATABASE=''
SSH_HOSTNAME=''
SSH_USER=''

#SMTP
EMAIL_HOST='YOUR EMAIL SERVER HOSTNAME HERE'
EMAIL_HOST_USER='YOUR EMAIL ADDRESS HERE'
EMAIL_HOST_PASSWORD='YOUR EMAIL PASSWORD HERE'
EMAIL_PORT=YOUR EMAIL SERVER PORT HERE

#AWS
PKEY=''

#ALTEIA
ALTEIA_USER=""
ALTEIA_PASSWORD=""

#GOOGLE EARTH ENGINE
PRIVATE_KEY=""

#PROJECT SECRET KEY
SECRET_KEY="YOUR SECRET KEY HERE"

SERVER_URL="YOUR SERVER URL HERE. ex:http://127.0.0.1:8000/"
```

Note: A request will have to be made to [support](mailto:cajusupport@tnslabs.org) to obtain the missing data in the `.env` file.

```sh
(env)$ python manage.py runserver
```
And navigate to `http://127.0.0.1:8000/`.

## Screenshots

![Screenshots of projects](https://i.ibb.co/5s6PMDk/Capture-d-cran-2022-06-02-112228.png)

![Screenshots of projects](https://i.ibb.co/Snv1XJP/Capture-d-cran-2022-06-02-120718.png)
