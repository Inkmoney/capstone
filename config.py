import os

from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))

#Give access to the project in ANY os where find ourselves in
#allow outside files/folder to be added to the project
#from the base directory

load_dotenv(os.path.join(basedir, '.env'))


class Config():
    """
    Set configuration variable for the flask app.
    Using environment variable where available
    otherwise create the config variable if not done
    already
    """

    FLASK_APP = os.environ.get('FLASK_APP')
    FLASK_APP = os.environ.get('FLASK_ENV')
    CLIENT_ID = os.environ.get('CLIENT_ID')
    CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
    YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
    SECRET_KEY = os.environ.get("SECRET_KEY") or "nana nana boo youll never guess"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///" + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODEFICATIONS = False #turns of messages from sqlalchemy regarding updates to our db