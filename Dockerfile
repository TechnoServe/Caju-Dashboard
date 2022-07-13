# syntax=docker/dockerfile:1
FROM python:3.9
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /Caju-Dashboard-v2
COPY requirements.txt /Caju-Dashboard-v2/
RUN pip install -r requirements.txt
COPY . /Caju-Dashboard-v2/
RUN python3 manage.py migrate --skip-checks
RUN python3 ./staticfiles/well_i_dont_know_their_use/import_alteia_data.py
RUN python3 ./staticfiles/well_i_dont_know_their_use/import_nurseries.py
RUN python3 ./staticfiles/well_i_dont_know_their_use/import_plantations.py
RUN python3 ./staticfiles/well_i_dont_know_their_use/import_satellite_data.py
RUN python3 ./staticfiles/well_i_dont_know_their_use/Import_training_dummy_data.py
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]