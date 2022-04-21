from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, TextAreaField
from wtforms import SelectMultipleField, SubmitField
from wtforms.validators import DataRequired


class ArticlesForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    img = FileField('Изображение (необезательно)', validators=[FileRequired()])
    type = SelectMultipleField('Тип статьи ',
                                   choices=[
                                       ('personage', 'Персонажи'),
                                       ('planets', 'Планеты'),
                                       ('chapter', 'Сюжет'),
                                       ('story', 'Истории')
                                   ])
    submit = SubmitField('Применить')
