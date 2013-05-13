import base64
import uuid


def gen_cookie():
    return (base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes))


if __name__ == "__main__":
    print gen_cookie()
