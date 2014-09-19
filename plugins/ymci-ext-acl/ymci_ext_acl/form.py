from ymci.ext.form import Form
from wtforms import StringField
from wtforms.validators import InputRequired, Optional
from .validators import InputRequiredIf
from wtforms_alchemy import SelectField


class RightForm(Form):
    login = SelectField(
        'User', validators=[InputRequiredIf('level_id')], default=None)
    group_id = SelectField('Group', coerce=int, default=None)
    level_id = SelectField(
        'Level', coerce=int, validators=[InputRequiredIf('login')],
        default=None)
    project_id = SelectField(
        'Project', coerce=int, validators=[Optional()], default=None)
    route = SelectField(
        'Controller', validators=[InputRequiredIf('group_id')], default=None)


class GroupForm(Form):
    name = StringField('Name', validators=[InputRequired()])


class SetForm(Form):
    group_id = SelectField('Group', coerce=int, validators=[InputRequired()])
    login = SelectField('User', validators=[InputRequired()])


class LevelForm(Form):
    name = StringField('Name', validators=[InputRequired()])


class UserLevelForm(Form):
    login = SelectField('User', validators=[InputRequired()])
    level_id = SelectField('Level', coerce=int, validators=[InputRequired()])
