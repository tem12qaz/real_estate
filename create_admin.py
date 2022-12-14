import os

from admin.admin_app import db
from admin.admin_app import user_datastore
from admin.models import Role, User

# app_dir = os.path.realpath(os.path.dirname(__file__))


def create_admin_account():
    email = 'test@test.ru'#random
    password = 'test'#random
    user_datastore.create_user(email=email, password=password, first_name='test', active=True)
    user_datastore.create_role(name = 'superuser', description='superuser')
    db.session.commit()
    user = User.query.filter(User.email == email).first()
    role = Role.query.filter(Role.name == 'superuser').first()
    user_datastore.add_role_to_user(user, role)
    db.session.commit()

    return email, password


if __name__ == '__main__':
    create_admin_account()