FROM python:3.11

ENV PYTHONUNBUFFERED=1
WORKDIR /foundly

COPY requirenments.txt /foundly/
RUN pip install --no-cache-dir -r requirenments.txt

COPY . /foundly/
EXPOSE 8000

# No need to run collectstatic since you don't want admin CSS/JS
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
