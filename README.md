# chama

A small tracker for a rotating savings group. Everyone puts in the same amount each month and one member takes the whole pot, in turn, until everybody has had a turn.

You tick who has paid, close the month, and it works out who receives. Someone who pays late can be marked later and their money goes to that month's member. New members join at the end of the round.

## Run

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app
```

Open http://localhost:8000. Everything is saved in chama.json in the folder you start it from. Set CHAMA_FILE to use a different file.

## How the rotation works

Members who still have to receive this round sit in a queue. Closing a month takes the first one off the front. When the queue is empty the round starts again in the same order. The logic is all in chama.py.

## Tests

```
pip install pytest
pytest
```

## License

MIT, see LICENSE.
