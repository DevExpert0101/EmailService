FROM python:3.8
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY . /code/
RUN pip install -r requirements.txt
RUN python manage.py collectstatic
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 emailchaser_backend.wsgi:application