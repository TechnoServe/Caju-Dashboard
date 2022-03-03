# syntax=docker/dockerfile:1

FROM python:3.9
RUN mkdir /Caju-Dashboard
WORKDIR /Caju-Dashboard
COPY ./ /Caju-Dashboard
RUN pip install -r /Caju-Dashboard/requirements.txt
EXPOSE 8000
ENTRYPOINT ["python","manage.py","runserver","0.0.0.0:8000"]