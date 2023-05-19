from flask_login import LoginManager
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


bcrypt = Bcrypt()

db = SQLAlchemy()
ma = Marshmallow()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def get_session():
    return db.session

class User(db.Model):
    """Site user."""

    __tablename__ = "users"

    id = db.Column(db.Integer, 
                   primary_key=True, 
                   autoincrement=True)

    username = db.Column(db.Text, 
                         nullable=False, 
                         unique=True)

    password = db.Column(db.Text, 
                         nullable=False)

    # start_register
    @classmethod
    def register(cls, username, pwd):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return cls(username=username, password=hashed_utf8)
    # end_register

    # start_authenticate
    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False
    # end_authenticate    

class Playlist(db.Model):
    """Playlist."""
    __tablename__= "playlists"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(100), nullable=False)
    
    play_song_xref = db.relationship('PlaylistSong', backref='playlists', passive_deletes=True)
    
    song = db.relationship('Song', secondary='playlist_song', backref='playlists', passive_deletes=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user =   db.relationship("User",  backref="playlists")

class Song(db.Model):
    """Song."""
    __tablename__= "songs"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    artists = db.Column(db.String(255), nullable=False)
    spotify_id = db.Column(db.String(255), nullable=False)
    album_name = db.Column(db.String(255), nullable=False)
    album_image = db.Column(db.String(255), nullable=False)
    play_song_xref = db.relationship('PlaylistSong', backref='songs', passive_deletes=True)

    play_song = db.relationship(
        'Playlist',
        secondary="playlist_song",
        cascade="all,delete",
        backref="songs",
        overlaps="play_song_xref,playlists,song,songs",
    )

   


class PlaylistSong(db.Model):
    """Mapping of a playlist to a song."""
    __tablename__ = "playlist_song"
    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.id', ondelete="CASCADE"))
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id', ondelete="CASCADE"))




# from datetime import datetime
# from flask_login import UserMixin,LoginManager
# from flask_sqlalchemy import SQLAlchemy
# from flask_marshmallow import Marshmallow
# from werkzeug.security import generate_password_hash
# # import uuid


# db = SQLAlchemy()
# ma = Marshmallow()
# login_manager = LoginManager()

# db.create_all()

# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(user_id)

# class User(UserMixin, db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(100), unique=True)
#     password = db.Column(db.String(100))
#     name = db.Column(db.String(1000))
#     date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
#     def set_password(self, password):
#         self.password = generate_password_hash(password, method='sha256')
