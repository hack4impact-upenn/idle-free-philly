from flask import render_template
from .. import db


class EditableHTML(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    editor_name = db.Column(db.String(100), unique=True)
    value = db.Column(db.Text)

    @staticmethod
    def get_editable_html(editor_name):
        editable_html_obj = EditableHTML.query.filter_by(
            editor_name=editor_name).first()

        if editable_html_obj is None:
            editable_html_obj = EditableHTML(editor_name=editor_name, value='')
        return editable_html_obj

    @staticmethod
    def add_default_faq():
        faq_editable_html = EditableHTML(
            editor_name='faq',
            value=render_template('main/faq_default.html')
        )
        db.session.add(faq_editable_html)
        db.session.commit()
