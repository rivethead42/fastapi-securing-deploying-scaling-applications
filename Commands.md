# FastAPI Widget API

A RESTful API for managing widgets with user authentication, built with FastAPI and MongoDB.

Create a SSL Certificate:
```
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout key.pem -out cert.pem
```

Run Uvicorn with SSL:
```
uvicorn main:app --ssl-keyfile=key.pem --ssl-certfile=cert.pem --reload 
```
