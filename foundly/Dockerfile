FROM python:3.11

ENV PYTHONUNBUFFERED=1
WORKDIR /foundly

COPY requirenments.txt /foundly/
RUN pip install --no-cache-dir -r requirenments.txt

COPY . /foundly/
EXPOSE 8000

#CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "foundly.asgi:application"]