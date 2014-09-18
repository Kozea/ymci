from ymci.ext.hooks import PrepareHook
from tornado.web import HTTPError
from tornado.escape import json_decode
from .db import Acl


class AclHook(PrepareHook):
    @property
    def active(self):
        return True

    def prepare(self, route):
        user = route.get_current_user()
        if user:
            user = json_decode(user)
        if not route.db.query(Acl).count():
            return
        query = (
            route.db
            .query(Acl)
            .filter_by(login=user or 'anonymous',
                       route=route.__class__.__name__)
            .first())
        if not query:
            raise HTTPError(403)
