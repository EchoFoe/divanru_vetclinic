FROM python:3.11
# RUN apt-get update && apt-get install -y ncat
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /code/
# RUN python manage.py migrate
CMD ["sh", "-c", "while ! pg_isready -h $DB_HOST -p $DB_PORT; do sleep 1; done; python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]