from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask_admin import Admin
from flask import redirect, url_for
from flask_login import logout_user, current_user
from init import app, db
from models import LinhKien, HangMuc, QuyDinh, RoleEnum

admin = Admin(app, name='Quản lý', url='/admin')


class AdminModelView(ModelView):
    # list_template = 'quanly/base_quanly.html'
    # create_template = 'quanly/base_quanly.html'
    # edit_template = 'quanly/base_quanly.html'
    # details_template = 'quanly/base_quanly.html'
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == RoleEnum.QUANLY


admin.add_view(AdminModelView(LinhKien, db.session, category="Quản lý", endpoint="linhkien_admin"))
admin.add_view(AdminModelView(HangMuc, db.session, category="Quản lý", endpoint="hangmuc_admin"))
admin.add_view(AdminModelView(QuyDinh, db.session, category="Quản lý", endpoint="quydinh_admin"))
