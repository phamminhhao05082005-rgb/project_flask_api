from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from init import app, login
from project import dao
from models import RoleEnum
import math


@app.route('/login')
def index():
    return render_template('login.html')


@login.user_loader
def load_user(pk):
    return dao.get_user_by_id(pk)


@app.route('/login', methods=['POST'])
def login_process():
    username = request.form.get('username')
    password = request.form.get('password')

    u = dao.auth_user(username=username, password=password)
    if u:
        login_user(u)

        if u.role == RoleEnum.TIEPNHAN:
            return redirect(url_for('tiepnhan_dashboard'))
        elif u.role == RoleEnum.SUACHUA:
            return redirect(url_for('suachua_dashboard'))
        elif u.role == RoleEnum.THUNGAN:
            return redirect(url_for('thungan_dashboard'))
        elif u.role == RoleEnum.QUANLY:
            return redirect(url_for('quanly_dashboard'))
        else:
            return render_template('login.html')
    else:
        return render_template('login.html', error="Tên đăng nhập hoặc mật khẩu không đúng")


@app.route('/tiepnhan')
@login_required
def tiepnhan_dashboard():
    check = check_role(RoleEnum.TIEPNHAN)
    if check:
        return check
    return render_template('NVTiepNhan/tiepnhan.html')


@app.route('/suachua')
@login_required
def suachua_dashboard():
    check = check_role(RoleEnum.SUACHUA)
    if check:
        return check
    return render_template('NVSuaChua/suachua.html')


@app.route('/thungan')
@login_required
def thungan_dashboard():
    check = check_role(RoleEnum.THUNGAN)
    if check:
        return check
    return render_template('NVThuNgan/thungan.html')


@app.route('/quanly')
@login_required
def quanly_dashboard():
    check = check_role(RoleEnum.QUANLY)
    if check:
        return check
    return render_template('quanly/base_quanly.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('login.html')

@app.route('/quanly/linhkien')
@login_required
def quanly_linhkien():
    check = check_role(RoleEnum.QUANLY)
    if check:
        return check

    page = request.args.get('page', 1, type=int)
    hangmuc_id = request.args.get('hangmuc', type=int)
    keyword = request.args.get('q', '')

    linhkiens = dao.get_linhkien_paginate(page=page, per_page=5, hangmuc_id=hangmuc_id, keyword=keyword)
    hangmucs = dao.get_all_hangmuc()

    return render_template(
        'quanly/linhkien.html',
        linhkiens=linhkiens,
        hangmucs=hangmucs,
        selected_hangmuc=hangmuc_id
    )


@app.route('/quanly/linhkien/create', methods=['GET', 'POST'])
@login_required
def quanly_linhkien_create():
    check = check_role(RoleEnum.QUANLY)
    if check:
        return check

    hangmucs = dao.get_all_hangmuc()
    if request.method == 'POST':
        dao.create_linhkien(
            ten=request.form['ten'],
            gia=float(request.form['gia']),
            tien_cong=float(request.form['tien_cong']),  # thêm
            hangmuc_id=int(request.form['hangmuc']),
            quanly_id=current_user.id
        )
        flash("Tạo linh kiện thành công", "success")
        return redirect(url_for('quanly_linhkien'))

    return render_template('quanly/tao_or_xoa_lk.html', hangmucs=hangmucs, linhkien=None)



@app.route('/quanly/linhkien/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def quanly_linhkien_edit(id):
    check = check_role(RoleEnum.QUANLY)
    if check:
        return check

    lk = dao.get_linhkien_by_id(id)
    hangmucs = dao.get_all_hangmuc()
    if request.method == 'POST':
        dao.update_linhkien(
            id=id,
            ten=request.form['ten'],
            gia=float(request.form['gia']),
            tien_cong=float(request.form['tien_cong']),
            hangmuc_id=int(request.form['hangmuc'])
        )
        flash("Cập nhật linh kiện thành công", "success")
        return redirect(url_for('quanly_linhkien'))

    return render_template('quanly/tao_or_xoa_lk.html', hangmucs=hangmucs, linhkien=lk)



@app.route('/quanly/linhkien/delete/<int:id>', methods=['POST'])
@login_required
def quanly_linhkien_delete(id):
    check = check_role(RoleEnum.QUANLY)
    if check:
        return check

    dao.delete_linhkien(id)
    flash("Xóa linh kiện thành công", "success")
    return redirect(url_for('quanly_linhkien'))


@app.route('/quanly/quydinh')
@login_required
def quanly_quydinh():
    check = check_role(RoleEnum.QUANLY)
    if check:
        return check

    page = request.args.get('page', 1, type=int)
    quydinhs = dao.get_quydinh_paginate(page=page, per_page=5)
    return render_template('quanly/quydinh.html', quydinhs=quydinhs)


@app.route('/quanly/quydinh/create', methods=['GET', 'POST'])
@login_required
def quanly_quydinh_create():
    check = check_role(RoleEnum.QUANLY)
    if check:
        return check

    if request.method == 'POST':
        dao.create_quydinh(
            ten_quy_dinh=request.form['ten_quy_dinh'],
            noi_dung=request.form['noi_dung'],
            quanly_id=current_user.id
        )
        flash("Tạo quy định thành công", "success")
        return redirect(url_for('quanly_quydinh'))

    return render_template('quanly/tao_or_xoa_qd.html', quydinh=None)


@app.route('/quanly/quydinh/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def quanly_quydinh_edit(id):
    check = check_role(RoleEnum.QUANLY)
    if check:
        return check

    qd = dao.get_quydinh_by_id(id)
    if request.method == 'POST':
        dao.update_quydinh(
            id=id,
            ten_quy_dinh=request.form['ten_quy_dinh'],
            noi_dung=request.form['noi_dung']
        )
        flash("Cập nhật quy định thành công", "success")
        return redirect(url_for('quanly_quydinh'))

    return render_template('quanly/tao_or_xoa_qd.html', quydinh=qd)


@app.route('/quanly/quydinh/delete/<int:id>', methods=['POST'])
@login_required
def quanly_quydinh_delete(id):
    check = check_role(RoleEnum.QUANLY)
    if check:
        return check

    dao.delete_quydinh(id)
    flash("Xóa quy định thành công", "success")
    return redirect(url_for('quanly_quydinh'))


@app.route('/quanly/baocao')
@login_required
def quanly_baocao():
    check = check_role(RoleEnum.QUANLY)
    if check:
        return check
    return render_template('quanly/baocao.html')

@app.route('/quanly/hangmuc')
@login_required
def quanly_hangmuc():
    check = check_role(RoleEnum.QUANLY)
    if check:
        return check

    hangmucs = dao.get_all_hangmuc()
    return render_template('quanly/hangmuc.html', hangmucs=hangmucs)


@app.route('/quanly/hangmuc/create', methods=['GET', 'POST'])
@login_required
def quanly_hangmuc_create():
    check = check_role(RoleEnum.QUANLY)
    if check:
        return check

    if request.method == 'POST':
        dao.create_hangmuc(request.form['ten'])
        flash("Tạo danh mục thành công", "success")
        return redirect(url_for('quanly_hangmuc'))

    return render_template('quanly/tao_or_sua_hm.html', hangmuc=None)


@app.route('/quanly/hangmuc/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def quanly_hangmuc_edit(id):
    check = check_role(RoleEnum.QUANLY)
    if check:
        return check

    hm = dao.get_hangmuc_by_id(id)
    if request.method == 'POST':
        dao.update_hangmuc(id, request.form['ten'])
        flash("Cập nhật danh mục thành công", "success")
        return redirect(url_for('quanly_hangmuc'))

    return render_template('quanly/tao_or_sua_hm.html', hangmuc=hm)


@app.route('/quanly/hangmuc/delete/<int:id>', methods=['POST'])
@login_required
def quanly_hangmuc_delete(id):
    check = check_role(RoleEnum.QUANLY)
    if check:
        return check

    success, message = dao.delete_hangmuc(id)
    flash(message, "success" if success else "danger")
    return redirect(url_for('quanly_hangmuc'))



def check_role(*allowed_roles):
    """Kiểm tra quyền dựa theo Enum RoleEnum"""
    if current_user.role not in allowed_roles:
        abort(403)
    return None


if __name__ == '__main__':
    app.run(debug=True)
