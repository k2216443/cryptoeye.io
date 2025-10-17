curl -X POST http://127.0.0.1:8080/t \
  -H "Content-Type: application/json" \
  -H "X-Forwarded-For: 91.108.5.74" \
  -H "X-Forwarded-Proto: https" \
  -H "X-Forwarded-Port: 443" \
  -H "X-Amzn-Trace-Id: Root=1-68f219b3-70e718077716b8f53f8b62db" \
  -d '{
    "update_id": 770153179,
    "message": {
      "message_id": 12,
      "from": {
        "id": 194219638,
        "is_bot": false,
        "first_name": "Konstantin",
        "last_name": "Ivanov",
        "username": "debugger00",
        "language_code": "en"
      },
      "chat": {
        "id": 194219638,
        "first_name": "Konstantin",
        "last_name": "Ivanov",
        "username": "debugger00",
        "type": "private"
      },
      "date": 1760696755,
      "text": "testo"
    }
  }'

