import jwt
from datetime import datetime, timedelta


def generate_tmp_link(room_id: str, secret_key: str, expiration_minutes: str = '30'):
    payload = {
        "room_id": room_id,
        "exp": datetime.utcnow() + timedelta(minutes=int(expiration_minutes))
    }
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    url = f"/chat/{room_id}?token={token}"
    return url


def verify_tmp_link(token: str, secret_key: str):
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        room_id = payload["room_id"]
        expiration_time = payload["exp"]
        if datetime.utcnow() < datetime.fromtimestamp(expiration_time):
            return room_id
        else:
            return None
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
