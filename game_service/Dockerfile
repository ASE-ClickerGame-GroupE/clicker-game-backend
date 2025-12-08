FROM python:3.13-slim

WORKDIR /code

COPY . /code/game_service

RUN pip install --no-cache-dir --upgrade -r /code/game_service/requirements.txt

ENV PYTHONPATH=/code

CMD ["uvicorn", "game_service.app.main:app", "--host", "0.0.0.0", "--port", "80"]