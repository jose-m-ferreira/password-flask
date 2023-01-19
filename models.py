from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "user"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    pwd = db.Column(db.String(300), nullable=False, unique=True)
    usergroupid = db.Column(db.String(80), primary_key=False)

    def __repr__(self):
        return '<User %r>' % self.username


class Groups(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    groupname = db.Column(db.String(80), unique=True, nullable=False)

    #def __init__(self, groupname):
    #    self.groupname = groupname

    def __repr__(self):
        return f"{self.groupname}"

class Asset(db.Model):
    __tablename__ = "assets"
    __searchable__=['assetname', 'assetdescription', 'assetipaddress', 'assetgroups', 'assetnotes']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    assetname = db.Column(db.String(120), unique=True, nullable=False)
    assetdescription = db.Column(db.String(120), unique=False, nullable=True)
    assetipaddress = db.Column(db.String(80), unique=False, nullable=False)
    assetuser = db.Column(db.String(80), unique=False, nullable=False)
    assetpwd = db.Column(db.Text, nullable=False, unique=False)
    permiteduserid = db.Column(db.String(300), nullable=True, unique=False)
    permitedgroupid = db.Column(db.String(300), nullable=False, unique=False, default='')
    assetgroups = db.Column(db.String(120), unique=False, nullable=True, default='')
    assetnotes = db.Column(db.String(512), unique=False, nullable=True)


class AssetGroups(db.Model):
    __tablename__ = "assetgroups"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    assetgroupname = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f"{self.assetgroupname}"
