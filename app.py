import rsa
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)

#import models

login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message_category = "info"

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
rsa = rsa

def asset_group_list(asset_group_ids):
    if asset_group_ids:
        from models import AssetGroups
        AssetGroups()

        asset_group_ids = list(map(int, asset_group_ids.split(',')))
        #print(f"asset_group_ids__: {asset_group_ids, type(asset_group_ids), asset_group_ids[0], type(asset_group_ids[0])}")
        asset_group_list = []
        for assetgroup in asset_group_ids:
            #print(f"asset_group iteration: {AssetGroups.query.filter_by(id=assetgroup).with_entities(AssetGroups.assetgroupname).all()[0][0], type(AssetGroups.query.filter_by(id=assetgroup).with_entities(AssetGroups.assetgroupname).all()[0][0])}")
            asset_group_list.append(AssetGroups.query.filter_by(id=assetgroup).with_entities(AssetGroups.assetgroupname).all()[0][0])

        #print(asset_group_list)
        return asset_group_list
    else:
        return asset_groups_ids
def create_app():
    app = Flask(__name__)

    app.secret_key = 'secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    login_manager.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    return app

def __init__():
    import models