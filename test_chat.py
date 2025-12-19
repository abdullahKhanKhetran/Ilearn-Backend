import requests

response = requests.post(
    "http://127.0.0.1:8000/chat",
    json={
        "student_id": "S001",
        "message": "How is this student?",
        "conversation_history": []
    },
    timeout=60
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")