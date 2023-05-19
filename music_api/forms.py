from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, EqualTo
from wtforms import StringField, IntegerField, SelectField, TextAreaField, BooleanField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, NumberRange, URL, Optional, DataRequired

class RegisterForm(FlaskForm):
    """Form for registering a user."""

    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired(), EqualTo('confirm', message='Passwords must match') ])
    confirm  = PasswordField('Repeat Password')


class LoginForm(FlaskForm):
    """Form for registering a user."""

    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])



class PlaylistForm(FlaskForm):
    """Form for adding playlists."""
    # Add the necessary code to use this form
    name = StringField("Playlist Name", validators=[InputRequired()])


class SongForm(FlaskForm):
    """Form for adding songs."""
    # Add the necessary code to use this form
    title = StringField("Song Title", validators=[InputRequired()] )
    artist = StringField("Artist Name", validators=[InputRequired()] )



# DO NOT MODIFY THIS FORM - EVERYTHING YOU NEED IS HERE
class NewSongForPlaylistForm(FlaskForm):
    """Form for adding a song to playlist."""

class SearchSongsForm(FlaskForm):
    """Form for searching music"""
    track = StringField("Search for songs", validators=[InputRequired()] )

class DeleteForm(FlaskForm):
    """Delete form -- this form is intentionally blank."""

class FindSongForm(FlaskForm):
    song = StringField('Song', validators=[DataRequired()])
    submit = SubmitField('Find')

