import json
import os
import os.path as op
import pathlib
import time

import requests as requests
from flask import abort, redirect, url_for, request, flash, send_file, after_this_request
from flask_admin import expose, BaseView
from flask_admin.contrib import sqla
from flask_admin.contrib.sqla.fields import InlineModelFormList
from flask_admin.contrib.sqla.form import InlineModelConverter
from flask_admin.form import ImageUploadField, ImageUploadInput
from flask_admin.helpers import get_form_data, get_redirect_target
from flask_babelex import gettext
from flask_login import current_user
from markupsafe import Markup
from sqlalchemy import func
from werkzeug.utils import secure_filename
from wtforms import PasswordField, ValidationError

from admin.config import UPDATE_BUTTON_URL, UPDATE_MESSAGE_URL, SEND_MESSAGE_URL, XLSX_PATH
from admin.flask_app_init import db
from admin.models import TourOperator, Photo, Tour, Date, Order
# from loader import logger
from utils.exports import TourExport


def name_gen(obj, file_data):
    parts = op.splitext(file_data.filename)
    return secure_filename(f'file-{time.time()}%s%s' % parts)


class ImportView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/import.html')


class CustomImageFieldWidget(ImageUploadInput):
    data_template = ('<div class="image-thumbnail">'
                     ' <img %(image)s>'
                     '</div>'
                     '<br>'
                     '<input %(file)s>')

#class="btn btn-success"
class CustomImageField(ImageUploadField):
    widget = CustomImageFieldWidget()


class MyModelView(sqla.ModelView):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))

    # can_edit = True
    edit_modal = True
    create_modal = True
    can_view_details = True
    details_modal = True


class UserView(MyModelView):
    column_editable_list = ['email', 'first_name']
    column_searchable_list = column_editable_list
    column_exclude_list = ['password']
    # form_excluded_columns = column_exclude_list
    column_details_exclude_list = column_exclude_list
    column_filters = column_editable_list
    form_overrides = {
        'password': PasswordField
    }


class TelegramUserView(MyModelView):
    can_export = True

    column_editable_list = ['full_name', 'city', 'phone', 'birthday', 'lang']
    column_searchable_list = column_editable_list
    column_exclude_list = ['chats']
    # form_excluded_columns = column_exclude_list
    column_details_exclude_list = column_exclude_list
    column_filters = column_editable_list


class TourOperatorAdminView(MyModelView):
    can_export = True

    column_editable_list = ['prepayment', 'full_name', 'about', 'region', 'city', 'languages', 'verified',
                            'contact_fio', 'experience', 'site', 'verified']
    column_searchable_list = column_editable_list
    column_filters = column_editable_list

    def _approve_decline_buttons(view, context, model, name):
        if model.moderate:
            return 'Approved'

        # render a form with a submit button for student, include a hidden field for the student id
        # note how checkout_view method is exposed as a route below
        url = url_for('.approve_decline_view')

        _html = '''
               <form action="{url}" method="POST">
                   <input id="operator_id" name="operator_id"  type="hidden" value="{operator_id}">
                   <input id="action" name="action"  type="hidden" value="approve">
                   <button type='submit' class="btn btn-success" >Approve</button>
               </form
               <br>
               <form action="{url}" method="POST">
                   <input id="operator_id" name="operator_id"  type="hidden" value="{operator_id}">
                   <input id="action" name="action"  type="hidden" value="decline">
                   <button type='submit' class="btn btn-danger" >Decline</button>
               </form>

           '''.format(url=url, operator_id=model.id)

        return Markup(_html)

    @expose('moderate', methods=['POST'])
    def approve_decline_view(self):
        return_url = self.get_url('.index_view')
        form = get_form_data()

        if not form:
            flash(gettext('Could not get form from request.'), 'error')
            return redirect(return_url)

        # Form is an ImmutableMultiDict
        operator_id = form['operator_id']
        action = form['action']

        # Get the model from the database
        operator = self.get_one(operator_id)

        if operator is None:
            flash(gettext('Оператор не найден'), 'error')
            return redirect(return_url)

        if operator.moderate:
            flash(gettext('Оператор уже прошел модерацию'))
            return redirect(return_url)
        try:
            if action == 'approve':
                operator.moderate = True
                _id = operator.id
            else:
                _id = operator.user.telegram_id
                self.session.delete(operator)

            self.session.commit()
            flash(gettext('ОК'))
            requests.post(
                SEND_MESSAGE_URL,
                data=json.dumps({
                    'action': f'{action}_operator',
                    'id': _id
                }),
                headers={'Content-Type': 'application/json'}
            )
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise

            flash(gettext('Ошибка при модерации тура'), 'error')

        return redirect(return_url)

    def _list_thumbnail(view, context, model, name):
        if not model.photo:
            return ''

        url = url_for('static', filename=os.path.join(model.photo))

        return Markup('<img src="%s" width="100">' % url)

    base_path = pathlib.Path(__file__).parent.resolve().joinpath('static')

    def picture_validation(form, field):
        if field.data:
            filename = field.data.filename
            if filename[-4:] != '.jpg' and filename[-4:] != '.png':
                raise ValidationError('file must be .jpg or .png')
        data = field.data.stream.read()
        field.data = data
        return True

    def on_model_delete(self, model):
        postfix = model.photo.split(".")[-1]
        prefix = model.photo.replace("." + postfix, '')
        try:
            os.remove(f'static/{model.photo}')
        except FileNotFoundError:
            pass
        try:
            os.remove(f'static/{prefix + "_thumb." + postfix}')
        except FileNotFoundError:
            pass

    form_extra_fields = {
        'photo': CustomImageField(
            'path', base_path=base_path, thumbnail_size=(100, 100, True),
            namegen=name_gen, endpoint='static')
    }

    column_formatters = {
        'moderate': _approve_decline_buttons,
        'photo': _list_thumbnail,
    }


class TourOperatorView(TourOperatorAdminView):

    column_exclude_list = ['chats', 'user', 'admin_account', 'tours', 'orders', 'verified', 'moderate']
    form_excluded_columns = column_exclude_list
    column_details_exclude_list = column_exclude_list

    def get_query(self):
        return super(TourOperatorView, self).get_query().filter(TourOperator.admin_account == current_user)

    def get_count_query(self):
        return self.session.query(func.count('*')).select_from(self.model).filter(
            TourOperator.admin_account == current_user)

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('admin'):
            self.can_delete = False
            self.can_create = False
            return True


class MessageView(MyModelView):
    column_editable_list = ['name', 'ru']
    column_searchable_list = column_editable_list
    column_filters = column_editable_list

    def after_model_change(self, form, instance, is_created):
        requests.get(UPDATE_MESSAGE_URL)


class ButtonView(MyModelView):
    column_editable_list = ['name', 'ru']
    column_searchable_list = column_editable_list
    column_filters = column_editable_list

    def after_model_change(self, form, instance, is_created):
        requests.get(UPDATE_BUTTON_URL)


class PhotoViewAdmin(MyModelView):
    form_columns = ('tour', 'path')

    def _list_thumbnail(view, context, model, name):
        if not model.path:
            return ''

        url = url_for('static', filename=os.path.join(model.path))

        return Markup('<img src="%s" width="100">' % url)

    base_path = pathlib.Path(__file__).parent.resolve().joinpath('static')

    column_formatters = {
        'path': _list_thumbnail
    }

    def on_model_delete(self, model):
        postfix = model.path.split(".")[-1]
        prefix = model.path.replace("." + postfix, '')
        try:
            os.remove(f'static/{model.path}')
        except FileNotFoundError:
            pass
        try:
            if os.path.exists(f'static/{prefix + "_thumb." + postfix}'):
                os.remove(f'static/{prefix + "_thumb." + postfix}')
        except FileNotFoundError:
            pass

    form_extra_fields = {
        'path': CustomImageField(
            'path', base_path=base_path, thumbnail_size=(100, 100, True),
            namegen=name_gen, endpoint='static')
    }


class PhotoView(PhotoViewAdmin):
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('admin'):
            return True

    def get_query(self):
        return super(PhotoView, self).get_query().join(Tour).join(TourOperator).filter(
            TourOperator.admin_account == current_user)

    def get_count_query(self):
        return self.session.query(func.count('*')).select_from(self.model).join(Tour).join(TourOperator).filter(
            TourOperator.admin_account == current_user)

    form_args = {
        'tour': {
            "query_factory": lambda: db.session.query(Tour).join(TourOperator).filter(
                TourOperator.admin_account == current_user)
        }
    }


class DirectionView(MyModelView):
    column_editable_list = ['name']
    column_searchable_list = column_editable_list
    # column_exclude_list = ['password']
    # form_excluded_columns = column_exclude_list
    # column_details_exclude_list = column_exclude_list
    column_filters = column_editable_list


class TourViewAdmin(MyModelView):
    can_export = True
    export_types = ['xlsx']

    column_editable_list = ['name', 'description', 'included', 'terms']
    column_searchable_list = column_editable_list
    # column_exclude_list = ['password']
    # form_excluded_columns = column_exclude_list
    # column_details_exclude_list = column_exclude_list
    column_filters = column_editable_list

    @expose('/export/<export_type>/')
    def export(self, export_type):
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_export or (export_type not in self.export_types):
            flash(gettext('Permission denied.'), 'error')
            return redirect(return_url)

        filename = self.export_tours()

        @after_this_request
        def remove_file(response):
            try:
                os.remove(XLSX_PATH + filename)
            except Exception as error:
                pass
                # logger.error("Error removing or closing downloaded file handle", error)
            return response

        if export_type == 'csv':
            return self._export_csv(return_url)
        elif export_type == 'xlsx':
            return send_file(XLSX_PATH + filename, download_name=filename)
        else:
            return self._export_tablib(export_type, return_url)

    def export_tours(self):
        export = TourExport(admin=True)
        tours = Tour.query.all()
        print(len(tours))
        return export.write_tours(tours)

    def _approve_decline_buttons(view, context, model, name):
        if model.moderate:
            return 'Approved'

        # render a form with a submit button for student, include a hidden field for the student id
        # note how checkout_view method is exposed as a route below
        url = url_for('.approve_decline_view')


        _html = '''
               <form action="{moderate_tour_url}" method="POST">
                   <input id="tour_id" name="tour_id"  type="hidden" value="{tour_id}">
                   <input id="action" name="action"  type="hidden" value="approve">
                   <button type='submit' class="btn btn-success">Approve</button>
               </form
               <br>
               <form action="{moderate_tour_url}" method="POST">
                   <input id="tour_id" name="tour_id"  type="hidden" value="{tour_id}">
                   <input id="action" name="action"  type="hidden" value="decline">
                   <button type='submit' class="btn btn-danger">Decline</button>
               </form>
               
           '''.format(moderate_tour_url=url, tour_id=model.id)

        return Markup(_html)

    @expose('moderate', methods=['POST'])
    def approve_decline_view(self):

        return_url = self.get_url('.index_view')

        form = get_form_data()

        if not form:
            flash(gettext('Could not get form from request.'), 'error')
            return redirect(return_url)

        # Form is an ImmutableMultiDict
        tour_id = form['tour_id']
        action = form['action']

        # Get the model from the database
        tour = self.get_one(tour_id)

        if tour is None:
            flash(gettext('Тур не найден'), 'error')
            return redirect(return_url)

        if tour.moderate:
            flash(gettext('Тур уже прошел модерацию'))
            return redirect(return_url)

        try:
            if action == 'approve':
                _id = tour.id
                tour.moderate = True
            else:
                _id = tour.owner.user.telegram_id
                self.session.delete(tour)
            self.session.commit()
            flash(gettext('ОК'))
            requests.post(
                    SEND_MESSAGE_URL,
                    data=json.dumps({
                        'action': f'{action}_tour',
                        'id': _id
                    }),
                    headers={'Content-Type': 'application/json'}
                )
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise

            flash(gettext('Ошибка при модерации тура'), 'error')

        return redirect(return_url)

    column_formatters = {
        'moderate': _approve_decline_buttons
    }

    def _list_thumbnail(view, context, model, name):
        if not model.path:
            return ''

        url = url_for('static', filename=os.path.join(model.path))
        return Markup('<img src="%s" width="100">' % url)

    def on_model_change(self, form, model, is_created):
        if len(model.photos) > 10:
            raise ValidationError('До 10 фотографий у тура')
        elif len(model.dates) > 10:
            raise ValidationError('До 10 дат у тура')

    inline_models = [
        (Photo, dict(
            _list_thumbnail=_list_thumbnail,

            form_extra_fields={
                'path': CustomImageField(
                    'path',
                    base_path=pathlib.Path(__file__).parent.resolve().joinpath('static'),
                    thumbnail_size=(100, 100, True), namegen=name_gen
                )
            },
            column_formatters={
                'path': _list_thumbnail
            }
        )),
        # CustomInlineFormAdmin(Date)
        (Date, dict(
            form_columns=('id', 'places', 'price', 'start', 'end'),
        ))
    ]


class CustomInlineModelFormList(InlineModelFormList):
    def display_row_controls(self, field):
        if field.form._obj:
            _type = type(field.form._obj)
            if _type == Date:
                if field.form._obj.tour.dates == [field.form._obj]:
                    return False
                orders = db.session.query(Order).filter(Order.date == field.form._obj).all()
                if orders:
                    return False

            elif _type == Photo:
                if field.form._obj.tour.photos == [field.form._obj]:
                    return False

        return True


class MyInlineModelConverter(InlineModelConverter):
    inline_field_list_type = CustomInlineModelFormList


class TourView(TourViewAdmin):
    column_exclude_list = ['orders', 'moderate']
    form_excluded_columns = column_exclude_list
    column_details_exclude_list = column_exclude_list

    def export_tours(self):
        export = TourExport()
        return export.write_tours(self.get_query())

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('admin'):
            return True

    def get_query(self):
        return super(TourView, self).get_query().join(TourOperator).filter(TourOperator.admin_account == current_user)

    def get_count_query(self):
        return self.session.query(func.count('*')).select_from(self.model).join(TourOperator).filter(
            TourOperator.admin_account == current_user)

    def on_model_delete(self, model):
        orders = db.session.query(Order).filter(Order.tour == model).all()
        if orders:
            raise ValidationError('Вы не можете удалить тур при активных заказах')


    def get_one(self, id):
        query = self.get_query()
        results = query.filter(self.model.id == id).one()
        return results

    def _list_thumbnail(view, context, model, name):
        if not model.path:
            return ''

        url = url_for('static', filename=os.path.join(model.path))
        return Markup('<img src="%s" width="100">' % url)

    # inline_model_form_converter = MyInlineModelConverter

    def on_form_prefill(self, form, id):
        orders = db.session.query(Order).filter(Order.tour == form._obj).all()

        if orders:
            form.included.render_kw = {'readonly': True}
            form.terms.render_kw = {'readonly': True}

        else:
            form.included.render_kw = {'readonly': False}
            form.terms.render_kw = {'readonly': False}

    def on_model_change(self, form, model, is_created):
        if len(model.photos) > 10:
            raise ValidationError('До 10 фотографий у тура')
        elif len(model.dates) > 10:
            raise ValidationError('До 10 дат у тура')

    def after_model_change(self, form, instance, is_created):
        if is_created:
            requests.post(
                SEND_MESSAGE_URL,
                data=json.dumps({
                    'action': 'create_tour',
                    'id': instance.id
                }),
                headers={'Content-Type': 'application/json'}
            )

    def _is_order_exists(form, field):
        if field.object_data != field.data:
            orders = db.session.query(Order).filter(Order.tour == form._obj).all()
            if orders:
                raise ValidationError('Вы не можете изменить это поле при активных заказах')

        return True

    def _is_order_exists_by_date(form, field):
        if (field.object_data != field.data) and field.object_data:
            orders = db.session.query(Order).filter(Order.date == form._obj).all()
            if orders:
                raise ValidationError('Вы не можете изменить это поле при активных заказах')

        return True

    form_args = {
        'owner': {
            "query_factory": lambda: db.session.query(TourOperator).filter(
                TourOperator.admin_account == current_user)

        },
        'terms': {
            'validators': [_is_order_exists]
        },
        'included': {
            'validators': [_is_order_exists]
        }
    }

    inline_model_form_converter = MyInlineModelConverter
    inline_models = [
        (Photo, dict(
            _list_thumbnail=_list_thumbnail,

            form_extra_fields={
                'path': CustomImageField(
                    'path',
                    base_path=pathlib.Path(__file__).parent.resolve().joinpath('static'),
                    thumbnail_size=(100, 100, True), namegen=name_gen
                )
            },
            column_formatters={
                'path': _list_thumbnail
            }
        )),
        # CustomInlineFormAdmin(Date)
        (Date, dict(
            form_columns=('id', 'places', 'price', 'start', 'end'),
            form_args={
                'start': {
                    'validators': [_is_order_exists_by_date]
                },
                'end': {
                    'validators': [_is_order_exists_by_date]
                }
            },
        ))
    ]


class DateViewAdmin(MyModelView):
    column_editable_list = ['places', 'price', 'sale', 'start', 'end']
    column_searchable_list = column_editable_list
    column_filters = column_editable_list


class DateView(DateViewAdmin):
    column_exclude_list = ['orders', 'sale', 'start', 'end']
    form_excluded_columns = column_exclude_list
    column_details_exclude_list = column_exclude_list

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('admin'):
            return True

        return False

    def get_query(self):
        return super(DateView, self).get_query().join(Tour).join(TourOperator).filter(
            TourOperator.admin_account == current_user)

    def get_count_query(self):
        return self.session.query(func.count('*')).select_from(self.model).join(Tour).join(TourOperator).filter(
            TourOperator.admin_account == current_user)

    form_args = {
        'tour': {
            "query_factory": lambda: db.session.query(Tour).join(TourOperator).filter(
                TourOperator.admin_account == current_user)
        }
    }


class OrderViewAdmin(MyModelView):
    column_editable_list = ['paid', 'tax', 'remainder', 'places', 'state', 'datetime']
    column_searchable_list = column_editable_list
    # column_exclude_list = ['password']
    # form_excluded_columns = column_exclude_list
    # column_details_exclude_list = column_exclude_list
    column_filters = column_editable_list


class OrderView(OrderViewAdmin):
    column_exclude_list = ['customer', 'promo']
    form_excluded_columns = column_exclude_list
    column_details_exclude_list = column_exclude_list
    can_delete = False
    can_create = False
    can_edit = False

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('admin'):
            return True

        return False

    def get_query(self):
        return super(OrderView, self).get_query().join(TourOperator).filter(
            TourOperator.admin_account == current_user)

    def get_count_query(self):
        return self.session.query(func.count('*')).select_from(self.model).join(TourOperator).filter(
            TourOperator.admin_account == current_user)


class PromoCodeView(MyModelView):
    column_editable_list = ['text', 'percent', 'uses', 'uses_for_one', 'end']
    column_searchable_list = column_editable_list
    column_exclude_list = ['orders', 'used']
    # form_excluded_columns = column_exclude_list
    column_details_exclude_list = column_exclude_list
    column_filters = column_editable_list


class ConfigView(MyModelView):
    column_editable_list = ['support_url', 'group', 'tax']
    column_searchable_list = column_editable_list
    # column_exclude_list = ['password']
    # form_excluded_columns = column_exclude_list
    # column_details_exclude_list = column_exclude_list
    column_filters = column_editable_list
    can_create = False
    can_delete = False

