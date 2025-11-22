FROM python:3.13-slim

WORKDIR /app

COPY Pipfile Pipfile.lock ./

RUN pip install pipenv && \
    pipenv install --system --deploy

COPY . .

ENV FLASK_RUN_PORT=5000
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
