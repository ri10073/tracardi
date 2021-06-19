from ...service.storage import index
from app.service.storage.elastic import Elastic


class UserDb:
    def __init__(self):
        self.users_db = [
            {
                "username": "admin",
                "password": "admin",
                "full_name": "Admin",
                "email": "johndoe@example.com",
                "roles": ["admin"],
                "disabled": False
            }
        ]

    def get_user(self, username):
        for record in self.users_db:
            if record['username'] == username:
                return record
        return None

    def __contains__(self, item):
        return self.get_user(item)


class TokenDb:

    def __init__(self):
        self._elastic = Elastic.instance()
        self._index = index.resources['token'].name

    async def delete(self, key):
        await self._elastic.delete(self._index, key)

    async def has(self, item):
        return await self._elastic.exists(self._index, item)

    async def get(self, item):
        return await self._elastic.get(self._index, item)

    async def set(self, key, value):
        record = {
            "doc": {"user": value},
            'doc_as_upsert': True
        }
        await self._elastic.update(self._index, key, record)


token2user = TokenDb()