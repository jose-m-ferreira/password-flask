import flask_login
from flask import (
    Flask,
    render_template,
    redirect,
    flash,
    url_for,
    session,
    request
)

from datetime import timedelta
from sqlalchemy.exc import (
    IntegrityError,
    DataError,
    DatabaseError,
    InterfaceError,
    InvalidRequestError,
)
from werkzeug.routing import BuildError
from werkzeug.datastructures import ImmutableMultiDict


from flask_bcrypt import Bcrypt,generate_password_hash, check_password_hash

from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)

from app import create_app, db, login_manager, bcrypt, rsa, asset_group_list, asset_permited_group_list, asset_permited_user_list, return_assets_in_assetgroup, return_group_name, return_groupnames, asset_permited_user_dict
from models import User, Groups, Asset, AssetGroups, Audit
from forms import login_form, register_form, self_update_form, search_form
from rsa_key_management import loadSecrets
from load_groups import insert_group_data
import pandas as pd

insert_group_data()
privateKey, publicKey = loadSecrets()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app = create_app()

@app.before_request
def session_handler():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)


@app.route("/", methods=("GET", "POST"), strict_slashes=False)
@login_required
def index():
    #print(type(current_user.usergroupid))
    assetgroups = AssetGroups.query.with_entities(AssetGroups.id, AssetGroups.assetgroupname).all()
    return render_template("index.html",title="Home", assetgroups=assetgroups)


@app.route("/login/", methods=("GET", "POST"), strict_slashes=False)
def login():
    form = login_form()

    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if check_password_hash(user.pwd, form.pwd.data):
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash("Invalid Username or password!", "danger")
        except Exception as e:
            flash(e, "danger")

    return render_template("auth.html",
        form=form,
        text="Login",
        title="Login",
        btn_action="Login"
        )


# Register route
@app.route("/register/", methods=("GET", "POST"), strict_slashes=False)
def register():
    form = register_form()
    if form.validate_on_submit():
        try:
            email = form.email.data
            pwd = form.pwd.data
            username = form.username.data
            
            newuser = User(
                username=username,
                email=email,
                pwd=bcrypt.generate_password_hash(pwd),
                usergroupid='2'
            )
    
            db.session.add(newuser)
            db.session.commit()
            flash(f"Account Succesfully created", "success")
            return redirect(url_for("login"))

        except InvalidRequestError:
            db.session.rollback()
            flash(f"Something went wrong!", "danger")
        except IntegrityError:
            db.session.rollback()
            flash(f"User already exists!.", "warning")
        except DataError:
            db.session.rollback()
            flash(f"Invalid Entry", "warning")
        except InterfaceError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except DatabaseError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except BuildError:
            db.session.rollback()
            flash(f"An error occured !", "danger")
    return render_template("auth.html",
        form=form,
        text="Create account",
        title="Register",
        btn_action="Register account"
        )


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/mypasswords")
@login_required
def mypasswords():
    if current_user.is_authenticated:
        user = current_user.username
        userid = current_user.id
        userGroupId = list(map(int,current_user.usergroupid.split(',')))

        all_assets = Asset.query.with_entities(Asset.id, Asset.assetname, Asset.assetipaddress, Asset.assetuser, Asset.assetpwd, Asset.permiteduserid, Asset.permitedgroupid, Asset.assetdescription, Asset.assetnotes).all()
        #print(userid, userGroupId)
        #print(all_assets)
        user_assets = []
        for i in range(0, len(all_assets)):
            #print(f"{all_assets[i][5]} - {all_assets[i]}")
            #print(f"all_assets: {all_assets[i][5]}")
            if all_assets[i][5]:
                asset_permited_users = list(map(int, all_assets[i][5].split(',')))
                #print(f"asset_permited_users: {asset_permited_users}")
                if userid in (list(map(int, all_assets[i][5].split(',')))):
                    #print(all_assets[i])
                    user_assets.append(all_assets[i])
        user_group_assets = []
        for i in range(0, len(all_assets)):
            #print(f"{all_assets[i][6]} - {all_assets[i]}")

            #print(f"list of user groupids user belongs to: {userGroupId}")
            #print(f"Asset permited user group ids: {(all_assets[i][6].split(',')[0]), type(all_assets[i][6].split(',')[0]), len(all_assets[i][6].split(',')[0])}")

            #if any(userGroupId) in any((list(map(int, all_assets[i][6].split(','))))):

            if (len(all_assets[i][6].split(',')[0]) > 0):

                for ugid in userGroupId:
                    if ugid in list(map(int, all_assets[i][6].split(','))):
                        #print(all_assets[i])
                        user_group_assets.append(all_assets[i])

        #remove duplicates from each list
        user_assets = list(dict.fromkeys(user_assets))
        user_group_assets = list(dict.fromkeys(user_group_assets))
        #print(f"search results: {user_assets, type(user_assets)}")
        #print(user_group_assets)

        #return f"UserID: {userid} <br> UserGroupId: {userGroupId} <br> User Assets: {user_assets} <br> Group Assets: {user_group_assets}"
        assetgroups = AssetGroups.query.with_entities(AssetGroups.id, AssetGroups.assetgroupname).all()
        return render_template('mypasswords.html', user_assets=user_assets, user_group_assets=user_group_assets, assetgroups=assetgroups)
    else:
        return f"Error"


@app.route("/mypasswords/<int:id>")
@login_required
def mypasswords_assetgroups(id):
    if current_user.is_authenticated:
        user = current_user.username
        userid = current_user.id
        print(f"current_user.usergroupid {current_user.usergroupid}")
        userGroupId = list(map(int, current_user.usergroupid.split(',')))
        print(f"assetgroup id : {id}")
        every_asset = Asset.query.with_entities(Asset.id, Asset.assetname, Asset.assetipaddress, Asset.assetuser, Asset.assetpwd, Asset.permiteduserid, Asset.permitedgroupid, Asset.assetgroups).all()
        #all_assets = Asset.query.filter_by(assetgroups=id).with_entities(Asset.id, Asset.assetname, Asset.assetipaddress, Asset.assetuser, Asset.assetpwd, Asset.permiteduserid, Asset.permitedgroupid, Asset.assetgroups).all()
        all_assets = []
        for each in every_asset:
            print(f"id: {id} each asset.assetgroups: {each.assetgroups.split(',')}")
            if each.assetgroups.split(',')[0]:
                agroups = list(map(int, each.assetgroups.split(',')))
                print(f"agroups {agroups}")
                if id in agroups:
                    all_assets.append(each)

        print(f"all_assets {all_assets}")
        print(f"routes.py /search: userid:  {userid}, userGroupId: {userGroupId}")
        # for asset in all_assets:
        # print(f"routes.py /search: all_assets: {asset}")
        user_assets = []
        for i in range(0, len(all_assets)):
            if all_assets[i][5]:
                asset_permited_users = list(map(int, all_assets[i][5].split(',')))
                if userid in (list(map(int, all_assets[i][5].split(',')))):
                    user_assets.append(all_assets[i])
        # print(f"routes.py - user_assets 678 {user_assets}")
        user_group_assets = []
        for i in range(0, len(all_assets)):
            print(f"routes.py - /search i: {i}")
            for ugid in userGroupId:
                print(f"{ugid} - all_assets[i][6].split(',') {all_assets[i][6].split(',')}")
                # if ugid in list(map(int, all_assets[i][6].split(','))):
                if ugid in list(map(int, all_assets[i][6].split(','))):
                    print(f"all_assets[i] {all_assets[i]}")
                    user_group_assets.append(all_assets[i])
        print(f"routes.py - user_group_assets 687 {user_group_assets}")

        # remove duplicates from each list
        user_assets = list(dict.fromkeys(user_assets))
        user_group_assets = list(dict.fromkeys(user_group_assets))
        # print(f"search results: {user_assets, type(user_assets)}")
        # print(user_group_assets)
        user_and_group_assets = []
        for usr in user_assets:
            user_and_group_assets.append(usr)
        for grp in user_group_assets:
            user_and_group_assets.append(grp)

        user_and_group_assets = list(dict.fromkeys(user_and_group_assets))
        user_and_group_assets = return_assets_in_assetgroup(id, user_and_group_assets)

        # return f"UserID: {userid} <br> UserGroupId: {userGroupId} <br> User Assets: {user_assets} <br> Group Assets: {user_group_assets}"
        assetgroups = AssetGroups.query.with_entities(AssetGroups.id, AssetGroups.assetgroupname).all()
        return render_template('asset_group_passwords.html', user_and_group_assets=user_and_group_assets,
                               assetgroups=assetgroups)
    else:
        return f"Error"


# lets manage groups
# create a new group
@app.route('/groups/create', methods=['GET', 'POST'])
@login_required
def create():
    if current_user.is_authenticated and 1 in list(map(int, current_user.usergroupid.split(','))):
        if request.method == 'GET':
            assetgroups = AssetGroups.query.with_entities(AssetGroups.id, AssetGroups.assetgroupname).all()
            return render_template('creategroup.html', assetgroups=assetgroups)

        if request.method == 'POST':
            #id = request.form['id']
            groupname = request.form['groupname']

            #group = Groups(id=id, groupname=groupname)
            group = Groups(groupname=groupname)
            db.session.add(group)
            db.session.commit()
            return redirect('/groups')
    else:
        return f"User not an admin"

#list the groups
@app.route('/groups')
@login_required
def RetrieveGroupList():
    groups = Groups.query.with_entities(Groups.id, Groups.groupname)
    assetgroups = AssetGroups.query.with_entities(AssetGroups.id, AssetGroups.assetgroupname).all()
    return render_template('groups_list.html', groups=groups, assetgroups=assetgroups)


#list individual groups
@app.route('/groups/<int:id>')
@login_required
def RetrieveSingleGroup(id):
    group = Groups.query.filter_by(id=id).first()
    if group:
        assetgroups = AssetGroups.query.with_entities(AssetGroups.id, AssetGroups.assetgroupname).all()
        return render_template('group.html', group=group, assetgroups=assetgroups)
    return f"Employee with id ={id} Doenst exist"


#update the groups
@app.route('/groups/<int:id>/groupupdate', methods=['GET', 'POST'])
@login_required
def update(id):
    if current_user.is_authenticated and 1 in list(map(int, current_user.usergroupid.split(','))):

        group = Groups.query.filter_by(id=id).first()
        if request.method == 'POST':
            if group:
                db.session.delete(group)
                db.session.commit()

                groupname = request.form['groupname']
                group = Groups(id=id, groupname=groupname)
                db.session.add(group)
                db.session.commit()
                return redirect(f'/groups/{id}')
            else:
                return f"Group with id = {id} Does not exist"


        assetgroups = AssetGroups.query.with_entities(AssetGroups.id, AssetGroups.assetgroupname).all()
        return render_template('groupupdate.html', group=group, assetgroups=assetgroups)
    else:
        return f"User not an admin"

#Let's manage users
#lets list users
@app.route('/users')
@login_required
def retrieve_user_list():
    users = User.query.with_entities(User.id, User.username, User.email, User.usergroupid)
    user_result = []
    for usr in users:
        user_group_names = []
        #usr_group_names = Groups.query.filter_by(id=usr.usergroupid).with_entities(Groups.groupname).first()

        for usr_group in usr.usergroupid.split(','):
            user_group_names.append(Groups.query.filter_by(id=usr_group).with_entities(Groups.groupname).first())


        #print(f"usr {usr, type(usr)}")
        #print(f"user_group_names {user_group_names, type(user_group_names)}")

        user_result_temp = [usr, user_group_names]
        #print(user_result_temp)
        user_result.append(user_result_temp)

    user_and_group_names = user_result
    print(user_and_group_names)
    assetgroups = AssetGroups.query.with_entities(AssetGroups.id, AssetGroups.assetgroupname).all()
    return render_template('user_list.html',users=users, user_and_group_names=user_and_group_names, assetgroups=assetgroups)


#list individual users
@app.route('/users/<int:id>')
@login_required
def retrieve_single_user(id):
    user = User.query.filter_by(id=id).first()
    #print(user.id, user.username, user.email, user.usergroupid)
    if user:
        assetgroups = AssetGroups.query.with_entities(AssetGroups.id, AssetGroups.assetgroupname).all()
        return render_template('user.html', user=user, assetgroups=assetgroups)
    return f"User with id ={id} Does not exist"


#update the user
@app.route('/users/<int:id>/userupdate', methods=['GET', 'POST'])
@login_required
def updateuser(id):
    if current_user.is_authenticated and 1 in list(map(int, current_user.usergroupid.split(','))):
        user = User.query.filter_by(id=id).first()
        all_user_groups = return_groupnames()

        this_user_groups = user.usergroupid

        #for ugid in user.usergroupid.split(','):

         #   this_user_groups = this_user_groups + str(ugid)
        #print(user, type(user), all_user_groups, type(all_user_groups), this_user_groups, type(this_user_groups))
        if request.method == 'POST':
            #print(f"request method: {request.form.keys()}")
            #print(f"request form: {request.form}")

            if "username" in request.form.keys():
                if user:
                    ##we don't want to change password so let's get it:
                    user_password = User.query.filter_by(id=id).with_entities(User.pwd).first()
                    user_password = user_password[0]
    #
                    db.session.delete(user)
                    db.session.commit()
    #
                    username = request.form['username']
                    email = request.form['email']

                    #request.form is an immutablemultidict!!!
                    #print(f"skills: {request.form.getlist('skills')}")
                    #print(f"skills str: {','.join(request.form.getlist('skills'))}")

                    usergroupid = ','.join(request.form.getlist('skills'))
                    #print(f"usergroupid: {usergroupid, type(usergroupid)}")
                    user = User(id=id, username=username, email=email, usergroupid=usergroupid, pwd=user_password)
    #
                    db.session.add(user)
                    db.session.commit()
                    return redirect(f'/users/{id}')
                else:
                    return f"User with id = {id} Does not exist"
            else:
                #print(f"hidden_skills in a ajax submit {request.form['hidden_skills']}")

                #print(f"request: {request.form}")
                return f"User with id = {id} Does not exist"
        assetgroups = AssetGroups.query.with_entities(AssetGroups.id, AssetGroups.assetgroupname).all()
        return render_template('userupdate.html', user=user, assetgroups=assetgroups, all_user_groups=all_user_groups, this_user_groups=this_user_groups)
    else:
        return f"User with id ={id} Does not exist"


# user settings update
@app.route('/users/selfupdate', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def selfupdateuser():
    form = self_update_form()
    id = current_user.id
    user = User.query.filter_by(id=id).first()
    username = user.username
    email = user.email
    pwd = user.pwd
    usergroupid = user.usergroupid
    if form.validate_on_submit():
        try:
            db.session.delete(user)
            db.session.commit()

            pwd = bcrypt.generate_password_hash(form.pwd.data)

            user = User(id=id, username=username, email=email, pwd=pwd, usergroupid=usergroupid)
            db.session.add(user)
            db.session.commit()
            flash(f"Account Succesfully updated, please login again", "success")
            return redirect("/logout")
        except InvalidRequestError:
            db.session.rollback()
            flash(f"Something went wrong!", "danger")
        except IntegrityError:
            db.session.rollback()
            flash(f"User already exists!.", "warning")
        except DataError:
            db.session.rollback()
            flash(f"Invalid Entry", "warning")
        except InterfaceError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except DatabaseError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except BuildError:
            db.session.rollback()
            flash(f"An error occured !", "danger")

    assetgroups = AssetGroups.query.with_entities(AssetGroups.id, AssetGroups.assetgroupname).all()
    return render_template("selfupdate.html",
                               form=form,
                               text="Save account",
                               title="Save",
                               btn_action="Submit",
                               assetgroups=assetgroups,
                               user=user
                               )


# lets manage assets
#list the assets
@app.route('/assets')
@login_required
def RetrieveAssetList():
    if current_user.is_authenticated and 1 in list(map(int, current_user.usergroupid.split(','))):
        assets = Asset.query.with_entities(Asset.id, Asset.assetname, Asset.assetdescription, Asset.assetipaddress,  Asset.permiteduserid, Asset.permitedgroupid, Asset.assetgroups, Asset.assetnotes)
        assetgroups = AssetGroups.query.with_entities(AssetGroups.id, AssetGroups.assetgroupname).all()
        return render_template('assets_list.html', assets=assets, assetgroups=assetgroups)
    return f"not an admin"


# create a new asset
@app.route('/assets/create', methods=['GET', 'POST'])
@login_required
def create_asset():
    if request.method == 'GET':
        all_user_groups = return_groupnames()
        this_asset_groups = Asset.permitedgroupid
        all_users = User.query.with_entities(User.id, User.username).all()
        this_asset_permited_users = Asset.permiteduserid
        assetgroups = AssetGroups.query.with_entities(AssetGroups.id, AssetGroups.assetgroupname).all()
        this_assets_assetgroups = Asset.assetgroups
        print(f"all_users: {all_users}")
        return render_template('createasset.html', assetgroups=assetgroups, all_user_groups=all_user_groups, this_asset_groups=this_asset_groups, all_users=all_users)

    if request.method == 'POST':
        print(f"asset create post skills: {request.form.getlist('skills')} form_asset_groups: {request.form.getlist('form_asset_groups')} permited_user_ids: {request.form.getlist('permited_user_ids')}")
        #id = request.form['id']
        assetname = request.form['assetname']
        assetdescription = request.form['assetdescription']
        assetnotes = request.form['assetnotes']
        assetipaddress = request.form['assetipaddress']
        assetuser = request.form['assetuser']
        assetpwd = rsa.encrypt(request.form['assetpwd'].encode('utf-8'), publicKey).hex()
        print(f"assetpwd: {assetpwd, type(assetpwd)}")
        permiteduserid = ','.join(request.form.getlist('permited_user_ids'))
        if not permiteduserid:
            permiteduserid = str(current_user.id)
        permitedgroupid = ','.join(request.form.getlist('skills'))
        #assetgroups = request.form['assetgroups']
        assetgroups = ','.join(request.form.getlist('form_asset_groups'))

        asset = Asset(assetname=assetname, assetdescription=assetdescription, assetipaddress=assetipaddress,
                      assetuser=assetuser,assetpwd=assetpwd, permiteduserid=permiteduserid,
                      permitedgroupid=permitedgroupid, assetgroups=assetgroups, assetnotes=assetnotes)
        try:
            db.session.add(asset)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash(f"Asset already exists!.", "warning")

        return redirect('/mypasswords')


#list individual assets
@app.route('/assets/<int:id>', methods=['GET', 'POST'])
@login_required
def RetrieveSingleAsset(id):
    userid = current_user.id
    userGroupId = list(map(int, current_user.usergroupid.split(',')))
    if Asset.query.filter_by(id=id).with_entities(Asset.permiteduserid)[0][0]:
        print(f"518: {Asset.query.filter_by(id=id).with_entities(Asset.permiteduserid)[0][0]}")
        asset_permited_users = list(map(int, Asset.query.filter_by(id=id).with_entities(Asset.permiteduserid)[0][0].split(',')))
    else:
        asset_permited_users = []
    print(f" asset_permited_groups_result query: {Asset.query.filter_by(id=id).with_entities(Asset.permitedgroupid)[0][0]}")
    if Asset.query.filter_by(id=id).with_entities(Asset.permitedgroupid)[0][0]:
        asset_permited_groups_result =list(map(int, Asset.query.filter_by(id=id).with_entities(Asset.permitedgroupid)[0][0].split(',')))
    else:
        asset_permited_groups_result = []
    print(f"routes: len asset_permited_groups_result: {len(asset_permited_groups_result), asset_permited_groups_result}")

    if len(asset_permited_groups_result) > 0:
        print(f"routes: asset_permited_groups_result query before map: {Asset.query.filter_by(id=id).with_entities(Asset.permitedgroupid)[0][0].split(',')}")
        asset_permited_groups = list(map(int, Asset.query.filter_by(id=id).with_entities(Asset.permitedgroupid)[0][0].split(',')))
    else:
        print(f"(asset_permited_groups_result): {(asset_permited_groups_result)}")
        print(f"len(asset_permited_groups_result) {len(asset_permited_groups_result)}")

    if userid in asset_permited_users or (set(userGroupId).intersection(asset_permited_groups)):
        #print(f"either userid {userid} or group {userGroupId} matched {asset_permited_users} or {asset_permited_groups}")

        asset = Asset.query.filter_by(id=id).first()
        if asset:
            print(f"asset.assetpwd {asset.assetpwd, type(asset.assetpwd)}")
            asset.assetpwd = rsa.decrypt(bytes.fromhex(asset.assetpwd), privateKey).decode()
            print(f"assetgroups: {asset.assetgroups, type(asset.assetgroups)}")
            if not asset.assetgroups:
                asset_group_names = ['No Asset Groups configured for this Asset']
            else:
                asset_group_names = asset_group_list(asset.assetgroups)

            if not asset.permitedgroupid:
                asset_permited_groups = ['No User Groups configured for this Asset']
            else:
                asset_permited_groups = asset_permited_group_list(asset.permitedgroupid)
            print(f"asset.permiteduserid: {asset.permiteduserid, type(asset.permiteduserid)}")
            if not asset.permiteduserid:
                asset_permited_users = ['No Users configured for this Asset']
            else:
                print(f"asset.permiteduserid {asset.permiteduserid}")
                asset_permited_users = asset_permited_user_list(asset.permiteduserid)

            db.session.close()
            #audit user -- this route method is view
            userid = current_user.id
            assetid = id
            method = 'view'
            audit = Audit(userid=userid, assetid=assetid, method=method)
            db.session.add(audit)
            db.session.commit()

            audit = Audit.query.filter_by(assetid=id).with_entities(Audit.id, Audit.userid, Audit.assetid, Audit.method,
                                              Audit.created_date).order_by(Audit.created_date.desc()).limit(100)
            assetgroups = AssetGroups.query.with_entities(AssetGroups.id, AssetGroups.assetgroupname).all()
            #rint(f"assetgroups {assetgroups}")
            return render_template('asset.html', asset=asset, assetgroups=assetgroups, asset_group_names=asset_group_names, asset_permited_groups=asset_permited_groups, asset_permited_users=asset_permited_users, audit=audit)
        return f"Asset with id ={id} Doesnt exist"
    else:
        return f"No permissions to view asset with id = {id}"


#update the assets
@app.route('/assets/<int:id>/assetupdate', methods=['GET', 'POST'])
@login_required
def updateasset(id):
    db.session.close()
    # audit user -- this route method is view
    userid = current_user.id
    assetid = id
    method = 'update'
    audit = Audit(userid=userid, assetid=assetid, method=method)
    db.session.add(audit)
    db.session.commit()
    db.session.close()

    all_user_groups = return_groupnames()
    this_asset_groups = Asset.query.filter_by(id=id).with_entities(Asset.permitedgroupid)[0][0]
    all_users = User.query.with_entities(User.id, User.username).all()
    this_asset_permited_users = Asset.query.filter_by(id=id).with_entities(Asset.permiteduserid)[0][0]
    assetgroups = AssetGroups.query.with_entities(AssetGroups.id, AssetGroups.assetgroupname).all()
    this_assets_assetgroups = Asset.query.filter_by(id=id).with_entities(Asset.assetgroups)[0][0]
    print(f"this_assets_assetgroups:  {this_assets_assetgroups}")
    userid = current_user.id
    userGroupId = list(map(int, current_user.usergroupid.split(',')))
    print(f"575 {Asset.query.filter_by(id=id).with_entities(Asset.permiteduserid)[0][0]}")
    if Asset.query.filter_by(id=id).with_entities(Asset.permiteduserid)[0][0]:
        asset_permited_users = list(map(int, Asset.query.filter_by(id=id).with_entities(Asset.permiteduserid)[0][0].split(',')))
        print(f"routes: asset_permited_groups before map: {Asset.query.filter_by(id=id).with_entities(Asset.permitedgroupid)[0][0]}")
    else:
        asset_permited_users = []
    if Asset.query.filter_by(id=id).with_entities(Asset.permitedgroupid)[0][0]:
        asset_permited_groups = list(map(int, Asset.query.filter_by(id=id).with_entities(Asset.permitedgroupid)[0][0].split(',')))
    else:
        asset_permited_groups = []

    if userid in asset_permited_users or (set(userGroupId).intersection(asset_permited_groups)):
        asset = Asset.query.filter_by(id=id).first()
        asset.assetpwd = rsa.decrypt(bytes.fromhex(asset.assetpwd), privateKey).decode()

        if request.method == 'POST':
            print(
                f"asset update skills: {request.form.getlist('skills')} form_asset_groups: {request.form.getlist('form_asset_groups')} permited_user_ids: {request.form.getlist('permited_user_ids')}")

            if asset:
                db.session.delete(asset)
                db.session.commit()
                print(f"asset delete?: {asset}")
                assetname = request.form['assetname']
                assetdescription = request.form['assetdescription']
                assetnotes = request.form['assetnotes']
                assetipaddress = request.form['assetipaddress']
                assetuser = request.form['assetuser']
                assetpwd = rsa.encrypt(request.form['assetpwd'].encode('utf-8'), publicKey).hex()

                permiteduserid = ','.join(request.form.getlist('permited_user_ids'))
                permitedgroupid = ','.join(request.form.getlist('skills'))
                assetgroups = ','.join(request.form.getlist('form_asset_groups'))


                #print(f"id={id}, assetname={assetname}, assetdescription={assetdescription}, assetipaddress={assetipaddress},\
                #      assetuser={assetuser},assetpwd={assetpwd}, permiteduserid={permiteduserid},\
                #      permitedgroupid={permitedgroupid}, assetgroups={assetgroups}, assetnotes={assetnotes}")
                asset = Asset(id=id, assetname=assetname, assetdescription=assetdescription, assetipaddress=assetipaddress,
                      assetuser=assetuser,assetpwd=assetpwd, permiteduserid=permiteduserid,
                      permitedgroupid=permitedgroupid, assetgroups=assetgroups, assetnotes=assetnotes)
                print(f"asset create? {asset.assetgroups}")

                db.session.add(asset)
                db.session.commit()
                return redirect(f'/assets/{id}')
            else:
                return f"Asset with id = {id} Does not exist"
        assetgroups = AssetGroups.query.with_entities(AssetGroups.id, AssetGroups.assetgroupname).all()
        return render_template('assetupdate.html', asset=asset, assetgroups=assetgroups,
                               this_assets_assetgroups=this_assets_assetgroups,all_user_groups=all_user_groups,
                               this_asset_groups=this_asset_groups, all_users=all_users,
                               this_asset_permited_users=this_asset_permited_users )
    else:
        return f"No permissions to edit asset with id = {id}"


#delete the asset
#@app.route('/assets/<int:id>/delete', methods=['GET'])
#@login_required
#def deleteasset(id):
#    userid = current_user.id
#    userGroupId = list(map(int, current_user.usergroupid.split(',')))
#
#    asset_permited_users = list(
#        map(int, Asset.query.filter_by(id=id).with_entities(Asset.permiteduserid)[0][0].split(',')))
#    asset_permited_groups = list(
#        map(int, Asset.query.filter_by(id=id).with_entities(Asset.permitedgroupid)[0][0].split(',')))
#
#    if userid in asset_permited_users or (set(userGroupId).intersection(asset_permited_groups)):
#        asset = Asset.query.filter_by(id=id).first()
#        if request.method == 'GET':
#            if asset:
#                db.session.delete(asset)
#                db.session.commit()
#            else:
#                return f"Asset with id = {id} Does not exist"
#
#        return redirect('/assets')
#    else:
#        return f"No permissions to delete asset with id: {id}"

#list the searched assets
@app.route("/search_results/<query>", methods=['GET', 'POST'])
@login_required
def show_search_results(query):

    

    assetgroups = AssetGroups.query.with_entities(AssetGroups.id, AssetGroups.assetgroupname).all()
    return render_template('search_result.html', assets=query, assetgroups=assetgroups)


#search for assets
@app.route('/search', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def search():
    if current_user.is_authenticated:
        user = current_user.username
        userid = current_user.id
        #print(f"current_user.usergroupid {current_user.usergroupid}")
        userGroupId = list(map(int, current_user.usergroupid.split(',')))
        all_assets = Asset.query.with_entities(Asset.id, Asset.assetname, Asset.assetipaddress, Asset.assetuser, Asset.assetpwd, Asset.permiteduserid, Asset.permitedgroupid, Asset.assetnotes, Asset.assetdescription).all()

        #print(f"routes.py /search: userid:  {userid}, userGroupId: {userGroupId}")
        #for asset in all_assets:
            #print(f"routes.py /search: all_assets: {asset}")
        user_assets = []
        for i in range(0, len(all_assets)):
            if all_assets[i][5]:
                asset_permited_users = list(map(int, all_assets[i][5].split(',')))
                if userid in (list(map(int, all_assets[i][5].split(',')))):
                    user_assets.append(all_assets[i])
        #print(f"routes.py - user_assets 698 {user_assets}")
        user_group_assets = []
        for i in range(0, len(all_assets)):
            #print(f"routes.py - /search i: {i}")
            for ugid in userGroupId:
                print(f"ugid: {ugid} - all_assets[i][6].split(',') {all_assets[i][6]}")

                if ugid in list(map(int, all_assets[i][6].split(','))):
                    #print(f"all_assets[i] {all_assets[i]}")
                    user_group_assets.append(all_assets[i])
        #print(f"routes.py - user_group_assets 687 {user_group_assets}")


        user_assets = list(dict.fromkeys(user_assets))
        user_group_assets = list(dict.fromkeys(user_group_assets))

        all_assets = user_assets + user_group_assets
        form = search_form()
        #print(f"all_assets: {all_assets} - {type(all_assets)}")
        if form.validate_on_submit():
            try:
                search_item = form.search_item.data.lower()
                if not all_assets:
                    flash(f"No Assets found for {search_item}", "search_empty_result")
                    assetgroups = AssetGroups.query.with_entities(AssetGroups.id, AssetGroups.assetgroupname).all()
                    return render_template("search.html", form=form, text="Search Assets", title="Search Assets",
                                           btn_action="Search Assets")

                else:
                    search_results = []
                    for item in list(all_assets):
                        #print(f"item: {item, type(item)}")
                        for sub_item in list(item):
                            #print(f"{search_item} - {sub_item, type(sub_item)}")
                            if search_item in str(sub_item).lower():
                                search_results.append(item)
                    #print(f"search_results: {search_results}")
                    if search_results:
                        search_results = list(dict.fromkeys(search_results))
                        #print(f"search results: {search_results, type(search_results)}")
                        #print(f"search_results[0]: {search_results[0], type(search_results[0])}")
                        #return redirect((url_for('search_results', query=search_results)))
                        # list the searched assets
                        return show_search_results(search_results)
                    else:
                        flash(f"No Assets found for {search_item}", "search_empty_result")
                        assetgroups = AssetGroups.query.with_entities(AssetGroups.id, AssetGroups.assetgroupname).all()
                        return render_template("search.html", form=form, text="Search Assets", title="Search Assets",
                                               btn_action="Search Assets", assetgroups=assetgroups)

            except:
                assetgroups = AssetGroups.query.with_entities(AssetGroups.id, AssetGroups.assetgroupname).all()
                return render_template("search.html", form=form, text="Search Assets", title="Search Assets",
                                       btn_action="Search Assets", assetgroups=assetgroups)
        #print('form did not validate on submit')
    assetgroups = AssetGroups.query.with_entities(AssetGroups.id, AssetGroups.assetgroupname).all()
    return render_template("search.html", form=form, text="Search Assets", title="Search Assets",
                           btn_action="Search Assets", assetgroups=assetgroups)


@app.route("/audit", methods=['GET'])
@login_required
def show_audit_log():
    audit = Audit.query.with_entities(Audit.id, Audit.userid, Audit.assetid, Audit.method, Audit.created_date).order_by(Audit.created_date.desc()).limit(100)
    assetgroups = AssetGroups.query.with_entities(AssetGroups.id, AssetGroups.assetgroupname).all()
    return render_template('show_audit_log.html', audit=audit, assetgroups=assetgroups)

if __name__ == "__main__":
    app.run(debug=True)