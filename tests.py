from starlette.testclient import TestClient

from app.fast import app

client = TestClient(app)
client.get('/', params={})
