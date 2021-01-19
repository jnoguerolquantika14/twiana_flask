from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class SearchForm(FlaskForm):
    account = StringField('Account: ',
                           validators=[DataRequired()])

    submit = SubmitField('Search')


