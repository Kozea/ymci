from sqlalchemy.exc import IntegrityError
from tornado.web import HTTPError
from ymci.model import Project, User
from ymci.ext.routes import BlockWebSocket, Route, url
from .db import Acl, AclLevel, Group, Set, UserLevel
from .form import GroupForm, LevelForm, RightForm, SetForm, UserLevelForm
from logging import getLogger

log = getLogger('ymci')


@url(r'/rights/list')
class RightsList(Route):
    def get(self):
        return self.render('index.html')

    def post(self):
        pass


@url(r'/blocks/rights_per_user')
class RightsUsersBlock(BlockWebSocket):
    def render_block(self):
        users = self.db.query(User).all()
        return self.render_string('blocks/rights_per_user.html', users=users)


@url(r'/blocks/rights_per_group')
class RightsGroupsBlock(BlockWebSocket):
    def render_block(self):
        groups = self.db.query(Group).all()
        return self.render_string(
            'blocks/rights_per_group.html', groups=groups)


@url(r'/blocks/set_list')
class SetList(BlockWebSocket):
    def render_block(self):
        sets = self.db.query(Set).all()
        return self.render_string('blocks/set_list.html', sets=sets)


@url(r'/rights/add/acl')
class RightsAdd(Route):
    def get(self):
        form = RightForm()
        form.login.choices = [('', '')] + [
            (u.login, u.login) for u in self.db.query(User).all()]
        form.group_id.choices = [(0, '')] + [
            (g.group_id, g.name) for g in self.db.query(Group).all()]
        form.level_id.choices = [(0, '')] + [
            (l.level_id, l.name) for l in self.db.query(AclLevel).all()]
        form.project_id.choices = [(0, '')] + [
            (p.project_id, p.name) for p in self.db.query(Project).all()]
        form.route.choices = [('', '')] + [
            (r, r) for r in sorted(self.application.named_handlers.keys())]
        return self.render(
            'form.html', form=form,
            render_form_recursively=self.render_form_recursively)

    def post(self):
        form = RightForm(self.posted)
        form.login.choices = [('', '')] + [
            (u.login, u.login) for u in self.db.query(User).all()]
        form.group_id.choices = [(0, '')] + [
            (g.group_id, g.name) for g in self.db.query(Group).all()]
        form.level_id.choices = [(0, '')] + [
            (l.level_id, l.name) for l in self.db.query(AclLevel).all()]
        form.project_id.choices = [(0, '')] + [
            (p.project_id, p.name) for p in self.db.query(Project).all()]
        form.route.choices = [('', '')] + [
            (r, r) for r in sorted(self.application.named_handlers.keys())]
        if form.validate():
            acl = Acl()
            form.populate_obj(acl)
            for key, value in form.data.items():
                if not value:
                    setattr(acl, key, None)
            self.db.add(acl)
            try:
                self.db.commit()
                self.set_flash_message(
                    'success', 'The acl has been successfully added')
            except IntegrityError:
                self.set_flash_message('danger', 'This acl already exists')
                self.redirect(self.reverse_url('RightsAdd'))
                return
        self.redirect(self.reverse_url('RightsList'))
        return


@url(r'/rights/edit/acl/(.*)')
class RightsEdit(Route):
    def get(self, id):
        if not id:
            raise HTTPError(404)
        form = RightForm()
        form.login.choices = [('', '')] + [
            (u.login, u.login) for u in self.db.query(User).all()]
        form.group_id.choices = [(0, '')] + [
            (g.group_id, g.name) for g in self.db.query(Group).all()]
        form.level_id.choices = [(0, '')] + [
            (l.level_id, l.name) for l in self.db.query(AclLevel).all()]
        form.project_id.choices = [(0, '')] + [
            (p.project_id, p.name) for p in self.db.query(Project).all()]
        acl = self.db.query(Acl).get(id)
        form.login.data = acl.login
        form.group_id.data = acl.group_id
        form.level_id.data = acl.level_id
        form.project_id.data = acl.project_id
        form.route.data = acl.route
        return self.render(
            'form.html', form=form,
            render_form_recursively=self.render_form_recursively)

    def post(self, id):
        if not id:
            raise HTTPError(404)
        form = RightForm(self.posted)
        form.login.choices = [('', '')] + [
            (u.login, u.login) for u in self.db.query(User).all()]
        form.group_id.choices = [(0, '')] + [
            (g.group_id, g.name) for g in self.db.query(Group).all()]
        form.level_id.choices = [(0, '')] + [
            (l.level_id, l.name) for l in self.db.query(AclLevel).all()]
        form.project_id.choices = [(0, '')] + [
            (p.project_id, p.name) for p in self.db.query(Project).all()]
        if form.validate():
            acl = self.db.query(Acl).get(id)
            form.populate_obj(acl)
            for key, value in form.data.items():
                if not value:
                    setattr(acl, key, None)
            try:
                self.db.commit()
                self.set_flash_message(
                    'success', 'The rights have been successfully set')
            except IntegrityError:
                self.set_flash_message('danger', 'This acl already exists')
                self.redirect(self.reverse_url('RightsEdit', id))
                return
            self.set_flash_message(
                'success', 'This acl has been successfully edited')
        self.redirect(self.reverse_url('RightsList'))
        return


@url(r'/rights/delete/acl/(\d+)')
class RightsDelete(Route):
    def get(self, id):
        if not id:
            raise HTTPError(404)
        return self.render(
            'ask.html',
            confirm='Are you sure you want to delete acl %s ?' % id)

    def post(self, id):
        if not id:
            raise HTTPError(404)
        acl = self.db.query(Acl).get(id)
        if acl:
            self.db.delete(acl)
            self.db.commit()
            self.set_flash_message(
                'success', 'The acl has been successfully deleted')
        self.redirect(self.reverse_url('RightsList'))
        return


@url(r'/rights/add/group')
class RightsAddGroup(Route):
    def get(self):
        form = GroupForm()
        return self.render(
            'form.html', form=form,
            render_form_recursively=self.render_form_recursively)

    def post(self):
        form = GroupForm(self.posted)
        if form.validate():
            group = Group()
            form.populate_obj(group)
            self.db.add(group)
            try:
                self.db.commit()
                self.set_flash_message(
                    'success', 'The group has been successfully added')
            except IntegrityError:
                self.set_flash_message('danger', 'This group already exists')
                self.redirect(self.reverse_url('RightsAddGroup'))
                return
        self.redirect(self.reverse_url('RightsList'))
        return


@url(r'/rights/edit/group/(\d+)')
class RightsEditGroup(Route):
    def get(self, id):
        if not id:
            raise HTTPError(404)
        form = GroupForm()
        group = self.db.query(Group).get(id)
        if group:
            form.name.data = group.name
        return self.render(
            'form.html', form=form,
            render_form_recursively=self.render_form_recursively)

    def post(self, id):
        if not id:
            raise HTTPError(404)
        form = GroupForm(self.posted)
        if form.validate():
            group = self.db.query(Group).get(id)
            form.populate_obj(group)
            try:
                self.db.commit()
                self.set_flash_message(
                    'success', 'The group has been successfully edited')
            except IntegrityError:
                self.set_flash_message('danger', 'This group already exists')
                self.redirect(self.reverse_url('RightsEditGroup', id))
                return
        self.redirect(self.reverse_url('RightsList'))
        return


@url(r'/rights/delete/group/(\d+)')
class RightsDeleteGroup(Route):
    def get(self, id):
        if not id:
            raise HTTPError(404)
        return self.render(
            'ask.html',
            confirm='Are you sure you want to delete the group: %s ?' % id)

    def post(self, id):
        if not id:
            raise HTTPError(404)
        group = self.db.query(Group).get(id)
        if group:
            self.db.delete(group)
            self.db.commit()
            self.set_flash_message('success', 'Group successfully deleted')
        self.redirect(self.reverse_url('RightsList'))
        return


@url(r'/rights/add/set')
class RightsAddSet(Route):
    def get(self):
        form = SetForm()
        form.group_id.choices = [
            (g.group_id, g.name) for g in self.db.query(Group).all()]
        form.login.choices = [
            (u.login, u.login) for u in self.db.query(User).all()]
        return self.render(
            'form.html', form=form,
            render_form_recursively=self.render_form_recursively)

    def post(self):
        form = SetForm(self.posted)
        form.group_id.choices = [
            (g.group_id, g.name) for g in self.db.query(Group).all()]
        form.login.choices = [
            (u.login, u.login) for u in self.db.query(User).all()]
        if form.validate():
            union = Set()
            form.populate_obj(union)
            self.db.add(union)
            try:
                self.db.commit()
                self.set_flash_message(
                    'success', 'The set has been successfully added')
            except IntegrityError:
                self.set_flash_message('danger', 'This set already exists')
                self.redirect(self.reverse_url('RightsAddSet'))
                return
        self.redirect(self.reverse_url('RightsList'))
        return


@url(r'/rights/edit/set/(\d+)/(.*)')
class RightsEditSet(Route):
    def get(self, group_id, login):
        if not group_id or not login:
            raise HTTPError(404)
        group_id = int(group_id)
        form = SetForm()
        form.group_id.choices = [
            (g.group_id, g.name) for g in self.db.query(Group).all()]
        form.login.choices = [
            (u.login, u.login) for u in self.db.query(User).all()]
        form.group_id.data = group_id
        form.login.data = login
        return self.render(
            'form.html', form=form,
            render_form_recursively=self.render_form_recursively)

    def post(self, group_id, login):
        if not group_id or not login:
            raise HTTPError(404)
        group_id = int(group_id)
        form = SetForm(self.posted)
        form.group_id.choices = [
            (g.group_id, g.name) for g in self.db.query(Group).all()]
        form.login.choices = [
            (u.login, u.login) for u in self.db.query(User).all()]
        if form.validate():
            union = self.db.query(Set).get([group_id, login])
            if not union:
                self.set_flash_message('danger', "This set doesn't exist")
            form.populate_obj(union)
            try:
                self.db.commit()
                self.set_flash_message(
                    'success', 'The set has been successfully edited')
            except IntegrityError:
                self.set_flash_message('danger', 'This set already exists')
                self.redirect(self.reverse_url('RightsEditSet',
                                               login=login, group_id=group_id))
                return
            self.set_flash_message('success',
                                   'The set has been successfully edited')
        self.redirect(self.reverse_url('RightsList'))
        return


@url(r'/rights/delete/set/(\d+)/(.*)')
class RightsDeleteSet(Route):
    def get(self, group_id, login):
        if not group_id or not login:
            raise HTTPError(404)
        group_id = int(group_id)
        message = ("Do you really want to delete the set: (%d %s) ?"
                   % (group_id, login))
        return self.render('ask.html', confirm=message)

    def post(self, group_id, login):
        if not group_id or not login:
            raise HTTPError(404)
        union = self.db.query(Set).get([group_id, login])
        if union:
            self.db.delete(union)
            self.db.commit()
            self.set_flash_message(
                'success', "The set has been successfully deleted")
        self.redirect(self.reverse_url('RightsList'))
        return


@url(r'/blocks/levels_list')
class RightsLevelList(BlockWebSocket):
    def render_block(self):
        levels = self.db.query(AclLevel).all()
        return self.render_string('blocks/levels_list.html', levels=levels)


@url(r'/rights/add/level')
class RightsAddLevel(Route):
    def get(self):
        form = LevelForm()
        self.render(
            'form.html', form=form,
            render_form_recursively=self.render_form_recursively)

    def post(self):
        form = LevelForm(self.posted)
        if form.validate():
            level = AclLevel()
            form.populate_obj(level)
            self.db.add(level)
            try:
                self.db.commit()
                self.set_flash_message(
                    'success', 'The level has been successfully added')
            except IntegrityError:
                self.set_flash_message('danger', 'This level already exists')
                self.redirect(self.reverse_url('RightsAddLevel'))
                return
        self.redirect(self.reverse_url('RightsList'))
        return


@url(r'/rights/edit/level/(\d+)')
class RightsEditLevel(Route):
    def get(self, id):
        if not id:
            raise HTTPError(404)
        level = self.db.query(AclLevel).get(id)
        if level:
            form = LevelForm()
            form.name.data = level.name
            self.render(
                'form.html', form=form,
                render_form_recursively=self.render_form_recursively)

    def post(self, id):
        if not id:
            raise HTTPError(404)
        form = LevelForm(self.posted)
        if form.validate():
            level = self.db.query(AclLevel).get(id)
            form.populate_obj(level)
            try:
                self.db.commit()
                self.set_flash_message(
                    'success', 'The level has been successfully edited')
            except IntegrityError:
                self.set_flash_message('danger', 'This level already exists')
                self.redirect(self.reverse_url('RightsEditLevel', id))
                return
        self.redirect(self.reverse_url('RightsList'))
        return


@url(r'/rights/delete/level(\d+)')
class RightsDeleteLevel(Route):
    def get(self, id):
        if not id:
            raise HTTPError(404)
        return self.render(
            'ask.html',
            confirm='Are you sure you want to delete the level %s ?' % id)

    def post(self, id):
        if not id:
            raise HTTPError(404)
        level = self.db.query(AclLevel).get(id)
        if level:
            self.db.delete(level)
            self.db.commit()
            self.set_flash_message(
                'success', 'The level has been successfully deleted')
        self.redirect(self.reverse_url('RightsList'))
        return


@url(r'/blocks/user_levels_list')
class RightsUserLevelList(BlockWebSocket):
    def render_block(self):
        levels = self.db.query(UserLevel).all()
        return self.render_string('blocks/user_levels_list.html',
                                  levels=levels)


@url(r'/rights/add/user_level/')
class RightsAddUserLevel(Route):
    def get(self):
        form = UserLevelForm()
        form.login.choices = [(u.login, u.login) for
                              u in self.db.query(User).all()]
        form.level_id.choices = [(l.level_id, l.name) for
                                 l in self.db.query(AclLevel).all()]
        return self.render(
            'form.html', form=form,
            render_form_recursively=self.render_form_recursively)

    def post(self):
        form = UserLevelForm(self.posted)
        form.login.choices = [(u.login, u.login) for
                              u in self.db.query(User).all()]
        form.level_id.choices = [(l.level_id, l.name) for
                                 l in self.db.query(AclLevel).all()]
        if form.validate():
            userlevel = UserLevel()
            form.populate_obj(userlevel)
            self.db.add(userlevel)
            try:
                self.db.commit()
                self.set_flash_message(
                    'success',
                    'The level has been successfully assigned to the user.')
            except IntegrityError:
                self.set_flash_message(
                    'danger', 'This user already has this level')
                self.redirect(self.reverse_url('RightsAddUserLevel'))
                return
        self.redirect(self.reverse_url('RightsList'))
        return


@url(r'/rights/edit/user_level/(.*)/(\d+)')
class RightsEditUserLevel(Route):
    def get(self, login, id):
        if not id or not login:
            raise HTTPError(404)
        level = self.db.query(UserLevel).get((login, id))
        form = UserLevelForm()
        form.login.choices = [(u.login, u.login) for
                              u in self.db.query(User).all()]
        form.level_id.choices = [(l.level_id, l.name) for
                                 l in self.db.query(AclLevel).all()]
        form.login.data = level.login
        form.level_id.data = level.level_id
        if level:
            self.render(
                'form.html', form=form,
                render_form_recursively=self.render_form_recursively)

    def post(self, login, id):
        if not id and not login:
            raise HTTPError(404)
        level = self.db.query(UserLevel).get((login, id))
        form = UserLevelForm(self.posted)
        form.login.choices = [(u.login, u.login) for
                              u in self.db.query(User).all()]
        form.level_id.choices = [(l.level_id, l.name) for
                                 l in self.db.query(AclLevel).all()]
        if form.validate():
            form.populate_obj(level)
            try:
                self.db.commit()
                self.set_flash_message(
                    'success',
                    'The level of the user has been successfully edited')
            except IntegrityError:
                self.set_flash_message(
                    'danger', 'This user already has this level')
                self.redirect(
                    self.reverse_url('RightsEditUserLevel', login, id))
                return
        self.redirect(self.reverse_url('RightsList'))
        return


@url(r'/rights/delete/user_level/(.*)/(\d+)')
class RightsDeleteUserLevel(Route):
    def get(self, login, id):
        if not id or not login:
            raise HTTPError(404)
        return self.render(
            'ask.html',
            confirm='Are you sure you want to delete the assignation of level'
            ' %s to the user %s ?' % (id, login))

    def post(self, login, id):
        if not id or not login:
            raise HTTPError(404)
        user_level = self.db.query(UserLevel).get((login, id))
        if user_level:
            self.db.delete(user_level)
            self.db.commit()
            self.set_flash_message(
                'success',
                'The right of this user has been successfully removed')
        self.redirect(self.reverse_url('RightsList'))
        return
