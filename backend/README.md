# installation

```bash
pip install -r requirements.txt
```

Create a .env file with the following content:

```bash
OPENAI_API_KEY
```

# run

## development

```bash
flask run --host=0.0.0.0 --port=5000
```

## production

```bash
gunicorn -w 4 wsgi:app
```

# Routes

## POST /feed-database

This route is used to feed the database with the message sent from the user.

Request:
```json
{
    "message": "Hey, the event was great!"
}
```

Response:
```json
{
    "message": "Message added successfully."
}
```

## GET /generate-feedbacks

This route is used to generate feedbacks based on the messages stored in the database.

Response:
```json
{
    "status": 200,
    "publish": True,
    "message": "Feedbacks",
}
```