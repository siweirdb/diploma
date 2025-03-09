FROM python:3.11

ENV PYTHONUNBUFFERED=1

WORKDIR /foundly

COPY requirenments.txt /foundly/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirenments.txt

COPY . /foundly/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
