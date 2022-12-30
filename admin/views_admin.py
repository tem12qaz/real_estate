import json
import os
import os.path as op
import pathlib
import time

import requests as requests
from flask import abort, redirect, url_for, request, flash, send_file, after_this_request
from flask_admin import expose, BaseView
from flask_admin.actions import action
from flask_admin.contrib import sqla
from flask_admin.contrib.sqla.fields import InlineModelFormList
from flask_admin.contrib.sqla.form import InlineModelConverter
from flask_admin.form import ImageUploadField, ImageUploadInput, FileUploadInput, FileUploadField
from flask_admin.helpers import get_form_data, get_redirect_target
from flask_babelex import gettext
from flask_login import current_user
from markupsafe import Markup
from sqlalchemy import func
from werkzeug.utils import secure_filename
from wtforms import PasswordField, ValidationError, HiddenField, Form, TextAreaField
from wtforms.validators import InputRequired

from admin.config import UPDATE_BUTTON_URL, UPDATE_MESSAGE_URL, SEND_MESSAGE_URL, XLSX_PATH
from admin.flask_app_init import db
from admin.models import Photo, File, Action


# from loader import logger


class ChangeForm(Form):
    ids = HiddenField()
    text = TextAreaField(validators=[InputRequired()])


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


class CustomImageField(ImageUploadField):
    widget = CustomImageFieldWidget()


class CustomFileField(FileUploadField):
    widget = FileUploadInput()


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

    column_editable_list = ['username', 'lang']
    column_searchable_list = column_editable_list
    column_exclude_list = ['chats']
    # form_excluded_columns = column_exclude_list
    column_details_exclude_list = column_exclude_list
    column_filters = column_editable_list


class DeveloperAdminView(MyModelView):
    can_export = True

    # column_editable_list = ['name', 'manager', 'chat_id', 'photo', 'message', 'rating', 'successful_orders']
    # column_searchable_list = column_editable_list
    # column_filters = column_editable_list

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
        'photo': _list_thumbnail,
    }


class MessageView(MyModelView):
    column_editable_list = ['name', 'ru', 'en']
    column_searchable_list = column_editable_list
    column_filters = column_editable_list

    def after_model_change(self, form, instance, is_created):
        requests.get(UPDATE_MESSAGE_URL)


class ButtonView(MyModelView):
    column_editable_list = ['name', 'ru', 'en']
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


class DistrictView(MyModelView):
    column_editable_list = ['name']
    column_searchable_list = column_editable_list
    # column_exclude_list = ['password']
    # form_excluded_columns = column_exclude_list
    # column_details_exclude_list = column_exclude_list
    column_filters = column_editable_list


class ObjectAdmin(MyModelView):
    can_export = True

    # export_types = ['xlsx']

    # column_editable_list = ['name', 'description', 'included', 'terms']
    # column_searchable_list = column_editable_list
    # column_exclude_list = ['password']
    # form_excluded_columns = column_exclude_list
    # column_details_exclude_list = column_exclude_list
    # column_filters = column_editable_list

    # @expose('/export/<export_type>/')
    # def export(self, export_type):
    #     return_url = get_redirect_target() or self.get_url('.index_view')
    #
    #     if not self.can_export or (export_type not in self.export_types):
    #         flash(gettext('Permission denied.'), 'error')
    #         return redirect(return_url)
    #
    #     filename = self.export_tours()
    #
    #     @after_this_request
    #     def remove_file(response):
    #         try:
    #             os.remove(XLSX_PATH + filename)
    #         except Exception as error:
    #             pass
    #             # logger.error("Error removing or closing downloaded file handle", error)
    #         return response
    #
    #     if export_type == 'csv':
    #         return self._export_csv(return_url)
    #     elif export_type == 'xlsx':
    #         return send_file(XLSX_PATH + filename, download_name=filename)
    #     else:
    #         return self._export_tablib(export_type, return_url)
    #
    # def export_tours(self):
    #     export = TourExport(admin=True)
    #     tours = Tour.query.all()
    #     print(len(tours))
    #     return export.write_tours(tours)

    def _list_thumbnail(view, context, model, name):
        if not model.path:
            return ''

        url = url_for('static', filename=os.path.join(model.path))
        return Markup('<img src="%s" width="100">' % url)

    # def on_model_change(self, form, model, is_created):
    #     if len(model.photos) > 10:
    #         raise ValidationError('До 10 фотографий у тура')
    #     elif len(model.dates) > 10:
    #         raise ValidationError('До 10 дат у тура')

    form_extra_fields = {
        'presentation_path': CustomFileField(
            'presentation_path',
            base_path=pathlib.Path(__file__).parent.resolve().joinpath('static'), namegen=name_gen
        )
    }

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
        (File, dict(
            # _list_thumbnail=_list_thumbnail,

            form_extra_fields={
                'path': CustomFileField(
                    'path',
                    base_path=pathlib.Path(__file__).parent.resolve().joinpath('static'), namegen=name_gen
                )
            },
            # column_formatters={
            #     'path': _list_thumbnail
            # }
        )),
        (File, dict(
            # _list_thumbnail=_list_thumbnail,

            form_extra_fields={
                'path': CustomFileField(
                    'path',
                    base_path=pathlib.Path(__file__).parent.resolve().joinpath('static'), namegen=name_gen
                )
            },
            # column_formatters={
            #     'path': _list_thumbnail
            # }
        )),
        # CustomInlineFormAdmin(Date)
    ]


# class CustomInlineModelFormList(InlineModelFormList):
#     def display_row_controls(self, field):
#         if field.form._obj:
#             _type = type(field.form._obj)
#             if _type == Date:
#                 if field.form._obj.tour.dates == [field.form._obj]:
#                     return False
#                 orders = db.session.query(Order).filter(Order.date == field.form._obj).all()
#                 if orders:
#                     return False
#
#             elif _type == Photo:
#                 if field.form._obj.tour.photos == [field.form._obj]:
#                     return False
#
#         return True


# class MyInlineModelConverter(InlineModelConverter):
#     inline_field_list_type = CustomInlineModelFormList


class OrderViewAdmin(MyModelView):
    column_editable_list = ['paid', 'tax', 'remainder', 'places', 'state', 'datetime']
    column_searchable_list = column_editable_list
    # column_exclude_list = ['password']
    # form_excluded_columns = column_exclude_list
    # column_details_exclude_list = column_exclude_list
    column_filters = column_editable_list


class ActionsAdmin(MyModelView):
    column_editable_list = ['type', ]
    list_template = 'admin/mail.html'

    column_filters = ['user.username', 'user.lang', 'type']
    column_labels = {
        'user.username': 'Username',
        'user.lang': 'Language',
        'type': 'Type'
    }

    column_searchable_list = column_editable_list
    # column_exclude_list = ['password']
    # form_excluded_columns = column_exclude_list
    # column_details_exclude_list = column_exclude_list
    # column_filters = column_editable_list

    form_ajax_refs = {
        'user': {
            'fields': ['telegram_id', 'username'],
            'page_size': 10
        },
        'developer': {
            'fields': ['name'],
            'page_size': 10
        },
        'object': {
            'fields': ['name'],
            'page_size': 10
        }
    }

    @action('send_mail', 'Mail')
    def action_change_cost(self, ids):
        url = get_redirect_target() or self.get_url('.index_view')
        return redirect(url, code=307)

    @expose('/', methods=['POST'])
    def index(self):
        if request.method == 'POST':
            url = get_redirect_target() or self.get_url('.index_view')
            ids = request.form.getlist('rowid')
            if ids:
                actions: list[Action] = db.session.query(Action).filter(Action.id.in_(ids)).distinct(Action.user_id)
            else:
                view_args = self._get_list_extra_args()
                sort_column = self._get_column_by_idx(view_args.sort)
                if sort_column is not None:
                    sort_column = sort_column[0]
                _, actions = self.get_list(
                    0, sort_column, view_args.sort_desc,
                    view_args.search, view_args.filters,
                    page_size=self.export_max_rows
                )
            users = []
            for action_ in actions:
                users.append(str(action_.user.telegram_id))

            ids = list(set(users))

            joined_ids = ','.join(ids)
            change_form = ChangeForm()
            change_form.ids.data = joined_ids
            self._template_args['url'] = url
            self._template_args['change_form'] = change_form
            self._template_args['change_modal'] = True
            return self.index_view()

    @expose('/mail_send/', methods=['POST'])
    def update_view(self):
        if request.method == 'POST':
            url = get_redirect_target() or self.get_url('.index_view')
            change_form = ChangeForm(request.form)
            if change_form.validate():
                users = change_form.ids.data.split(',')
                if len(users) == 0:
                    flash(f"Need at least one user to send", category='warning')
                    return self.index_view()
                data = {
                    'users': users,
                    'text': change_form.text.data
                }
                requests.post(SEND_MESSAGE_URL, data=data)
                flash(f"Message sent to {len(users)} users", category='info')
                return redirect(url)
            else:
                flash(f"Form invalid", category='error')
                return self.index_view()


class ConfigView(MyModelView):
    column_editable_list = ['support', ]
    column_searchable_list = column_editable_list
    # column_exclude_list = ['password']
    # form_excluded_columns = column_exclude_list
    # column_details_exclude_list = column_exclude_list
    column_filters = column_editable_list
    can_create = False
    can_delete = False
