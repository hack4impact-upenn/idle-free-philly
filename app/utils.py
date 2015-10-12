from flask import url_for


def register_template_utils(app):
    """Register Jinja 2 helpers (called from __init__.py)."""

    @app.template_test()
    def equalto(value, other):
        return value == other

    @app.template_global()
    def is_hidden_field(field):
        from wtforms.fields import HiddenField
        return isinstance(field, HiddenField)

    app.add_template_global(index_for_role)


def index_for_role(role):
    return url_for(role.name + '.index')


def parse_to_db(db, filename):
    import csv
    with open(filename, 'rb') as file:
        reader = csv.reader(file, delimiter=',')
        return reader.next()
