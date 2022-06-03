# Caju-Dashboard
> The Satellite Dashboard is a remote sensing dashboard created to map satellite growing areas in Benin, using satellite imagery and machine learning algorithms. The dashboard will help field teams improve operations and policy makers make better decisions

![GitHub](https://img.shields.io/github/license/Technoserve/Caju-Dashboard-v2)

![](https://i.ibb.co/zmSTb1N/Capture-d-cran-2022-06-02-120227.png)

## Requirements  (Prerequisites)
Tools and packages required to successfully install this project.
For example:
* Linux, Windows or MacOS
* Python 3.9

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

Once `pip` has finished downloading the dependencies:
```sh
(env)$ cd apps/dashboard
```
```sh
(env)$ python manage.py runserver
```
And navigate to `http://127.0.0.1:8000/`.

## Screenshots

![Screenshots of projects](https://i.ibb.co/5s6PMDk/Capture-d-cran-2022-06-02-112228.png)

![Screenshots of projects](https://i.ibb.co/Snv1XJP/Capture-d-cran-2022-06-02-120718.png)
