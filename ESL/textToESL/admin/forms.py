from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from flask_wtf.file import FileField, FileAllowed
from textToESL.models import Dictionary

class NewWord(FlaskForm):
    word = StringField('Word', validators=[DataRequired()])
    sign_video = FileField('Sign Language Video', validators=[FileAllowed(['mp4', 'mov'])])
    submit = SubmitField('Add Word')

    def validate_word(self, word):
        word_exists = Dictionary.query.filter_by(word=word.data).first()
        if word_exists:
            raise ValidationError('This word already exists in the dictionary.')
        
class DeleteCustomerForm(FlaskForm):
    pass

class DeleteMessageForm(FlaskForm):
    pass
