import rsa
import pandas as pd
from rsa_key_management import loadSecrets
from flask_sqlalchemy import SQLAlchemy
import loadAlchemy
from app import create_app
create_app()
db = SQLAlchemy()
from models import Asset




appdb_passwordflask = SQLAlchemy().create_engine(loadAlchemy.app_config_SQLALCHEMY_DATABASE_URI, {})
rsa = rsa
privateKey, publicKey = loadSecrets()

df = pd.read_excel('Z:\\0.6.Passwords\\jmf_clean_PasswordManager.xlsx')
df = df.where(pd.notnull(df), None)
for index, row in df.iterrows():
    print(row['Asset Name'], row['Asset Description'], row['Asset IPAddress'], row['Asset Username'], row['Asset Password'], row['Asset Permited User Id List'], row['Asset Groups Id List'], row['Notes'])
    assetpwd = rsa.encrypt(row['Asset Password'].encode('utf-8'), publicKey)
    print(assetpwd)

    if row['Notes'] != None:
        assetnotes = row['Notes']
    else:
        assetnotes=''
    assetname = row['Asset Name']
    assetdescription = row['Asset Description']
    if assetdescription == None:
        assetdescription = ''
    assetipaddress = row['Asset IPAddress']
    if  assetipaddress == None:
        assetipaddress = ''
    assetuser = row['Asset Username']
    permiteduserid = '0'
    permitedgroupid = '1'
    #print(f"row['Asset Groups Id List'] {row['Asset Groups Id List']}")
    if row['Asset Groups Id List'] != None:
        assetgroups = row['Asset Groups Id List'].split('.')[0]
    else:
        assetgroups = ''

    update_string = f"INSERT INTO assets (assetname, assetdescription, assetipaddress, assetuser, permiteduserid, permitedgroupid, assetgroups, assetnotes, assetpwd) VALUES('{assetname}', '{assetdescription}', '{assetipaddress}', '{assetuser}', '{permiteduserid}', '{permitedgroupid}', '{assetgroups}', '{assetnotes}', %s);"
    asset = Asset( assetname=assetname, assetdescription=assetdescription, assetipaddress=assetipaddress,
                  assetuser=assetuser, assetpwd=assetpwd, permiteduserid=permiteduserid,
                  permitedgroupid=permitedgroupid, assetgroups=assetgroups, assetnotes=assetnotes)

    #db.session.add(asset)
   # db.session.commit()
