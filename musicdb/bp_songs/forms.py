from wtforms.validators import InputRequired
from flask_wtf.file import FileAllowed
from flask_wtf import FlaskForm
from wtforms import MultipleFileField, SubmitField

class UploadForm(FlaskForm):
    files = MultipleFileField("Files", validators=[InputRequired(), FileAllowed(['mp3'])])
    submit = SubmitField("Upload file")

