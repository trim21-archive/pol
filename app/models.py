import base64
import json


class User(object):
    is_authenticated = True
    is_active = True
    is_anonymous = False
    auth = ''

    def get_id(self):
        return self.auth

    def __init__(self, auth):
        auth_string = auth

        if auth:
            auth = auth.replace('@', '=')
            auth = base64.b64decode(auth).decode()
            auth = json.loads(auth)
            auth['auth'] = auth_string
            self.username = auth['username']
            self.password = auth['password']
            self.auth = auth_string
        else:
            raise ValueError('you must input a auth')
            # except binascii.Error:
            #     return
            # except json.JSONDecodeError:
            #     return

    @classmethod
    def get(cls, auth):
        try:
            user = cls(auth)
            return user
        except:
            return
