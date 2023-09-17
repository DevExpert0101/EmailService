## Emailchaser Backend

The backend is built using django, djangorestframework

### Local setup for development

1. Install env, and required libraries
2. Migrate the database: `python manage.py migrate`
3. Start the local server: `python manage.py runserver`

### Server setup using this tutorial

[django with nginx and gunicorn](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-18-04)


### Code style
Install precommit and run it before commit anything
```
pre-commit install
```