from wtforms.validators import InputRequired


class InputRequiredIf(InputRequired):
    def __init__(self, other_field_name, *args, **kwargs):
        self.other_field_name = other_field_name
        super().__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception(
                'No field named "%s" in form' % self.other_field_name)
        if bool(other_field.data):
            super().__call__(form, field)
