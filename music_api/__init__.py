from flask import Flask
from flask_migrate import Migrate
from .api.routes import api
from .authentication.routes import auth
from .site.routes import site
from .models import db as root_db, login_manager, ma 
from config import Config
from .helpers import to_est, JSONEncoder
from flask_cors import CORS


app = Flask(__name__)
app.secret_key = "12345"



@app.context_processor
def inject_to_est():
    return {'to_est': to_est}

app.register_blueprint(api)
app.register_blueprint(site)
app.register_blueprint(auth)

app.config.from_object(Config)
root_db.init_app(app)

with app.app_context():
    # root_db.drop_all()
    root_db.create_all()
    
migrate = Migrate(app, root_db)

ma.init_app(app)

login_manager.init_app(app)
login_manager.login_view = 'auth.login'

app.json_encoder = JSONEncoder


CORS(app)
