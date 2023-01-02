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


from flask_bcrypt import Bcrypt,generate_password_hash, check_password_hash

from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)

from app import create_app,db,login_manager,bcrypt
from models import User, Groups, Asset
from forms import login_form,register_form


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app = create_app()

@app.before_request
def session_handler():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=1)


@app.route("/", methods=("GET", "POST"), strict_slashes=False)
def index():
    return render_template("index.html",title="Home")


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
        userGroupId = current_user.usergroupid
        all_assets = Asset.query.with_entities(Asset.id, Asset.assetname, Asset.assetipaddress, Asset.assetuser, Asset.assetpwd, Asset.permiteduserid, Asset.permitedgroupid).all()
        #print(userid)
        #print(all_assets)
        user_assets = []
        for i in range(0, len(all_assets)):
            #print(f"{all_assets[i][5]} - {all_assets[i]}")
            if str(userid) in str(all_assets[i][5]) :
                #print(all_assets[i])
                user_assets.append(all_assets[i])
        user_group_assets = []
        for i in range(0, len(all_assets)):
            #print(f"{all_assets[i][5]} - {all_assets[i]}")
            if str(userGroupId) in str(all_assets[i][6]):
                #print(all_assets[i])
                user_group_assets.append(all_assets[i])

        return f"UserID: {userid} <br> UserGroupId: {userGroupId} <br> User Assets: {user_assets} <br> Group Assets: {user_group_assets}"


# lets manage groups
# create a new group
@app.route('/groups/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'GET':
        return render_template('creategroup.html')

    if request.method == 'POST':
        #id = request.form['id']
        groupname = request.form['groupname']

        #group = Groups(id=id, groupname=groupname)
        group = Groups(groupname=groupname)
        db.session.add(group)
        db.session.commit()
        return redirect('/groups')


#list the groups
@app.route('/groups')
@login_required
def RetrieveGroupList():
    groups = Groups.query.with_entities(Groups.id, Groups.groupname)
    return render_template('groups_list.html', groups=groups)


#list individual groups
@app.route('/groups/<int:id>')
@login_required
def RetrieveSingleGroup(id):
    group = Groups.query.filter_by(id=id).first()
    if group:
        return render_template('group.html', group=group)
    return f"Employee with id ={id} Doenst exist"


#update the groups
@app.route('/groups/<int:id>/groupupdate', methods=['GET', 'POST'])
@login_required
def update(id):
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

    return render_template('groupupdate.html', group=group)


#Let's manage users
#lets list useres
@app.route('/users')
@login_required
def retrieve_user_list():
    users = User.query.with_entities(User.id, User.username, User.email, User.usergroupid)
    return render_template('user_list.html', users=users)


#list individual users
@app.route('/users/<int:id>')
@login_required
def retrieve_single_user(id):
    user = User.query.filter_by(id=id).first()
    #print(user.id, user.username, user.email, user.usergroupid)
    if user:
        return render_template('user.html', user=user)
    return f"User with id ={id} Does not exist"


#update the user
@app.route('/users/<int:id>/userupdate', methods=['GET', 'POST'])
@login_required
def updateuser(id):
    user = User.query.filter_by(id=id).first()
    if request.method == 'POST':
        if user:
            #we don't want to change password so let's get it:
            user_password = User.query.filter_by(id=id).with_entities(User.pwd).first()
            user_password = user_password[0]

            db.session.delete(user)
            db.session.commit()

            username = request.form['username']
            email = request.form['email']
            usergroupid = request.form['usergroupid']
            user = User(id=id, username=username, email=email, usergroupid=usergroupid, pwd=user_password)

            db.session.add(user)
            db.session.commit()
            return redirect(f'/users/{id}')
        else:
            return f"User with id = {id} Does not exist"

    return render_template('userupdate.html', user=user)


# lets manage assets
#list the assets
@app.route('/assets')
@login_required
def RetrieveAssetList():
    assets = Asset.query.with_entities(Asset.id, Asset.assetname, Asset.assetdescription, Asset.assetipaddress, Asset.assetuser, Asset.assetpwd, Asset.permiteduserid, Asset.permitedgroupid)
    return render_template('assets_list.html', assets=assets)


# create a new asset
@app.route('/assets/create', methods=['GET', 'POST'])
@login_required
def create_asset():
    if request.method == 'GET':
        return render_template('createasset.html')

    if request.method == 'POST':
        #id = request.form['id']
        assetname = request.form['assetname']
        assetdescription = request.form['assetdescription']
        assetipaddress = request.form['assetipaddress']
        assetuser = request.form['assetuser']
        assetpwd = request.form['assetpwd']
        permiteduserid = request.form['permiteduserid']
        permitedgroupid = request.form['permitedgroupid']

        asset = Asset(assetname=assetname, assetdescription=assetdescription, assetipaddress=assetipaddress,
                      assetuser=assetuser,assetpwd=assetpwd, permiteduserid=permiteduserid,
                      permitedgroupid=permitedgroupid)
        db.session.add(asset)
        db.session.commit()
        return redirect('/assets')


#list individual assets
@app.route('/assets/<int:id>')
@login_required
def RetrieveSingleAsset(id):
    asset = Asset.query.filter_by(id=id).first()
    if asset:
        return render_template('asset.html', asset=asset)
    return f"Asset with id ={id} Doenst exist"


#update the assets
@app.route('/assets/<int:id>/assetupdate', methods=['GET', 'POST'])
@login_required
def updateasset(id):
    asset = Asset.query.filter_by(id=id).first()
    if request.method == 'POST':
        if asset:
            db.session.delete(asset)
            db.session.commit()

            assetname = request.form['assetname']
            assetdescription = request.form['assetdescription']
            assetipaddress = request.form['assetipaddress']
            assetuser = request.form['assetuser']
            assetpwd = request.form['assetpwd']
            permiteduserid = request.form['permiteduserid']
            permitedgroupid = request.form['permitedgroupid']

            asset = Asset(id=id, assetname=assetname, assetdescription=assetdescription, assetipaddress=assetipaddress,
                      assetuser=assetuser,assetpwd=assetpwd, permiteduserid=permiteduserid,
                      permitedgroupid = permitedgroupid)

            db.session.add(asset)
            db.session.commit()
            return redirect(f'/assets/{id}')
        else:
            return f"Asset with id = {id} Does not exist"

    return render_template('assetupdate.html', asset=asset)


#delete the asset
@app.route('/assets/<int:id>/delete', methods=['GET'])
@login_required
def deleteasset(id):
    asset = Asset.query.filter_by(id=id).first()
    if request.method == 'GET':
        if asset:
            db.session.delete(asset)
            db.session.commit()
        else:
            return f"Asset with id = {id} Does not exist"

    return redirect('/assets')


if __name__ == "__main__":
    app.run(debug=True)
