from tornado.web import HTTPError
from ymci.ext.hooks import PrepareHook
<<<<<<< HEAD
from ymci.model import User
=======
from tornado.web import HTTPError
from tornado.escape import json_decode
>>>>>>> 7c1faf749075b21da42c0b8d8c6fc60ba90da0b8
from .db import Acl


class AclHook(PrepareHook):
    @property
    def active(self):
        return route.db.query(Acl).count()

    def prepare(self, route):
        user = route.db.query(User).get(route.get_current_user())
        query = (
            route.db
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
                    route.db.query(Acl)
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
