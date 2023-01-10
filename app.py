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

def asset_permited_group_list(asset_permited_group_ids):
    if asset_permited_group_ids:
        from models import Groups
        Groups()

        asset_permited_group_ids = list(map(int, asset_permited_group_ids.split(',')))
        print(f"asset_permited_group_ids: {asset_permited_group_ids}")
        asset_permited_group_list = []
        for permited_group in asset_permited_group_ids:
            asset_permited_group_list.append(Groups.query.filter_by(id=permited_group).with_entities(Groups.groupname).all()[0][0])
        return asset_permited_group_list
    else:
        return asset_permited_group_ids

def asset_permited_user_list(asset_permited_user_ids):
    if asset_permited_user_ids:
        from models import User
        User()

        asset_permited_user_ids = list(map(int, asset_permited_user_ids.split(',')))

        asset_permited_user_list = []
        for permited_user in asset_permited_user_ids:
            asset_permited_user_list.append(
                User.query.filter_by(id=permited_user).with_entities(User.username).all()[0][0])
        return asset_permited_user_list
    else:
        return asset_permited_user_ids

def return_assets_in_assetgroup(assetgroupid, assetgrouplist):
    #print(f"assetgroupid, assetgrouplist: {assetgroupid, assetgrouplist}")
    return_assets_in_assetgroup = []
    if assetgrouplist and assetgroupid:
        for asset in assetgrouplist:
            if asset[7]:
                asset_list = list(map(int, asset[7].split(',')))

                print(f"asset_list: {asset_list}")
                if assetgroupid in asset_list:
                    return_assets_in_assetgroup.append(asset)
        return return_assets_in_assetgroup
    else:
        return [f"There are no Assets in this Asset Group"]


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