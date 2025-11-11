from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask_admin import Admin
from flask import redirect, url_for
from flask_login import logout_user, current_user
from init import app, db
from project.models import LinhKien

admin = Admin(app=app, name='project')


class LinhKienView(ModelView):

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'quanly'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

from project.models import LinhKien

admin.add_view(LinhKienView(LinhKien, db.session, name="Quản lý Linh Kiện"))