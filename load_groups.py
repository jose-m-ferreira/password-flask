from app import create_app, db
from models import Groups


def insert_group_data():
    app = create_app()
    with app.app_context():
        if Groups.query.filter_by(id=1).first() != 'PWFlaskAdmin':
            db.session.delete(Groups.query.filter_by(id=1).first())
            db.session.delete(Groups.query.filter_by(id=2).first())
            db.session.commit()

            admingroup = Groups(id=1, groupname='PWFlaskAdmin')
            generalgroup = Groups(id=2, groupname='General')
            db.session.add(admingroup)
            db.session.add(generalgroup)
            db.session.commit()


if __name__ == "__main__":
    insert_group_data()