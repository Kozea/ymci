from tornado.web import HTTPError
from tornado.escape import json_decode, to_unicode
from ymci.ext.hooks import PrepareHook
from ymci.model import User
from .db import Acl


class AclHook(PrepareHook):
    @property
    def active(self):
        return self.db.query(Acl).count()

    def prepare(self, route):
        current_user = self.get_current_user(route)
        if not current_user:
            raise HTTPError(403)

        user = self.db.query(User).get(current_user)
        query = (
            self.db
            .query(Acl)
            .filter_by(login=user.login or 'anonymous')
            .all())
        # You shall not … Oh wait you're THE admin
        if user.level and user.level.acl_level.name == 'ADMIN':
            return
        if not query:
            raise HTTPError(403)
        for acl in query:
            # User scope rights
            if acl.route != route.__class__.__name__:
                continue
            # Last chance to access the page if user is in acl group
            if acl.user.groups:
                gacl = (
                    self.db.query(Acl)
                    .filter(Acl.group_id.in_(
                        [x.group_id for x in acl.user.groups]))
                    .first())
            if not (gacl and gacl.route == route.__class__.__name__):
                continue
            # Project route
            project_id = route.path_kwargs.get('project_id', None)
            if project_id:
                if project_id != acl.project_id:
                    continue
            break
        else:
            raise HTTPError(403)

    def get_current_user(self, route):
        user = route.get_secure_cookie("user")
        if not user:
            return None
        return json_decode(to_unicode(user))
