#!venv/bin/python
import os
import time
import traceback

import flask_admin
from flask import url_for, render_template, request, flash, redirect
from flask_admin import helpers as admin_helpers
from flask_login import login_required, current_user
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore

from admin.flask_app_init import db, app
from admin.models import User, Role, TelegramUser, Config, Button, Message, PromoCode, Order, Date, Photo, Tour, \
    Direction, TourOperator
from admin.views_admin import TelegramUserView, TourOperatorView, DirectionView, \
    TourView, OrderView, PromoCodeView, MessageView, ButtonView, ConfigView, TourOperatorAdminView, PhotoViewAdmin, \
    OrderViewAdmin, DateViewAdmin, TourViewAdmin, ImportView
from data.config import BASE_PATH
from utils.imports import ImportTours

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

MIGRATION_DIR = os.path.join('', 'migrations')

migrate = Migrate(app, db, directory=MIGRATION_DIR)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and '.xlsx' in file.filename:
            print('xlsx_file')
            path = BASE_PATH + f'{time.time()}_xlsx_input.xlsx'
            file.save(path)
            try:
                ImportTours(path, current_user).read_xlsx()
            except Exception as e:
                if os.path.exists(path):
                    os.remove(path)
                print(traceback.format_exc())
                flash('Ошибка чтения файла, проверьте формат документа')
                return redirect(url_for('import.index'))

        else:
            print('no_xlsx')
            flash('Недопустимое расширение файла')
            return redirect(url_for('import.index'))

        if current_user.has_role('superuser'):
            return redirect(url_for('tour.index_view'))
        else:
            return redirect(url_for('my_tours.index_view'))


# Create admin
admin = flask_admin.Admin(
    app,
    'TuruTur Admin',
    base_template='my_master.html',
    template_mode='bootstrap4',
)

# Add model views
# admin.add_view(MyModelView(Role, db.session, menu_icon_type='fa', menu_icon_value='fa-server', name="Roles"))
# admin.add_view(UserView(User, db.session, menu_icon_type='fa', menu_icon_value='fa-users', name="Users"))
admin.add_view(
    TelegramUserView(TelegramUser, db.session, menu_icon_type='fa', menu_icon_value='fa-users', name="Telegram User"))
admin.add_view(TourOperatorAdminView(TourOperator, db.session, menu_icon_type='fa', menu_icon_value='fa-address-card',
                                     name="Tour Operator"))
admin.add_view(TourOperatorView(endpoint='operator_card', name="Operator Card", model=TourOperator, session=db.session,
                                menu_icon_type='fa', menu_icon_value='fa-address-card'))
admin.add_view(DirectionView(Direction, db.session, menu_icon_type='fa', menu_icon_value='fa-arrows', name="Direction"))

admin.add_view(TourViewAdmin(Tour, db.session, menu_icon_type='fa', menu_icon_value='fa-plane', name="Tour"))
admin.add_view(
    TourView(Tour, db.session, menu_icon_type='fa', menu_icon_value='fa-plane', name="Tour", endpoint='my_tours'))

admin.add_view(ImportView(name="Import tours", endpoint='import', menu_icon_type='fa', menu_icon_value='fa-cloud-upload'))


# admin.add_view(PhotoView(Photo, db.session, menu_icon_type='fa', menu_icon_value='fa-picture-o', name="Photo",
#                          endpoint='tour_photo'))
admin.add_view(PhotoViewAdmin(Photo, db.session, menu_icon_type='fa', menu_icon_value='fa-picture-o', name="Photo"))

admin.add_view(DateViewAdmin(Date, db.session, menu_icon_type='fa', menu_icon_value='fa-calendar', name="Date"))
# admin.add_view(DateView(Date, db.session, menu_icon_type='fa', menu_icon_value='fa-calendar', name="Tour Dates",
#                         endpoint='tour_dates'))

admin.add_view(
    OrderViewAdmin(Order, db.session, menu_icon_type='fa', menu_icon_value='fa-shopping-cart', name="Orders"))
admin.add_view(OrderView(Order, db.session, menu_icon_type='fa', menu_icon_value='fa-shopping-cart', name="Orders",
                         endpoint='tour_orders'))

admin.add_view(PromoCodeView(PromoCode, db.session, menu_icon_type='fa', menu_icon_value='fa-ticket', name="PromoCode"))
admin.add_view(MessageView(Message, db.session, menu_icon_type='fa', menu_icon_value='fa-comment', name="Message"))
admin.add_view(ButtonView(Button, db.session, menu_icon_type='fa', menu_icon_value='fa-comments', name="Button"))
admin.add_view(ConfigView(Config, db.session, menu_icon_type='fa', menu_icon_value='fa-cog', name="Config"))


# define a context processor for merging flask-admin's template context into the
# flask-security views.


@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )


if __name__ == '__main__':
    app_dir = os.path.realpath(os.path.dirname(__file__))
    # database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    app.run(debug=False)
