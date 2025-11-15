from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from init import app, login
from project import dao
from models import RoleEnum, LinhKien, HangMuc
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

    if not username or not password:
        flash("Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu", "warning")
        return render_template('login.html')

    u = dao.auth_user(username=username, password=password)

    if not u:
        flash("Tên đăng nhập hoặc mật khẩu không đúng", "danger")
        return render_template('login.html')

    login_user(u)

    redirect_map = {
        RoleEnum.TIEPNHAN: 'tiepnhan_dashboard',
        RoleEnum.SUACHUA: 'suachua_dashboard',
        RoleEnum.THUNGAN: 'thungan_dashboard',
        RoleEnum.QUANLY: 'quanly_dashboard'
    }

    return redirect(url_for(redirect_map.get(u.role, 'login')))



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
        ten = request.form['ten'].strip()
        try:
            gia = float(request.form['gia'])
            tien_cong = float(request.form['tien_cong'])
            hangmuc_id = int(request.form['hangmuc'])
        except ValueError:
            flash("Dữ liệu không hợp lệ!", "danger")
            return render_template('quanly/tao_or_xoa_lk.html', hangmucs=hangmucs, linhkien=None)

        if gia <= 0:
            flash("Giá linh kiện phải lớn hơn 0!", "danger")
        elif tien_cong < 0:
            flash("Tiền công không được âm!", "danger")
        elif not dao.is_name_unique(LinhKien, ten, field_name='ten_linh_kien'):
            flash("Tên linh kiện đã tồn tại!", "danger")
        else:
            dao.create_linhkien(
                ten=ten,
                gia=gia,
                tien_cong=tien_cong,
                hangmuc_id=hangmuc_id,
                quanly_id=current_user.id
            )
            flash("Tạo linh kiện thành công!", "success")
            return redirect(url_for('quanly_linhkien'))

        return render_template('quanly/tao_or_xoa_lk.html', hangmucs=hangmucs, linhkien=None)

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
        ten = request.form['ten'].strip()
        try:
            gia = float(request.form['gia'])
            tien_cong = float(request.form['tien_cong'])
            hangmuc_id = int(request.form['hangmuc'])
        except ValueError:
            flash("Dữ liệu không hợp lệ!", "danger")
            return render_template('quanly/tao_or_xoa_lk.html', hangmucs=hangmucs, linhkien=lk)

        if gia <= 0:
            flash("Giá linh kiện phải lớn hơn 0!", "danger")
        elif tien_cong < 0:
            flash("Tiền công không được âm!", "danger")
        elif not dao.is_name_unique(LinhKien, ten, exclude_id=id, field_name='ten_linh_kien'):
            flash("Tên linh kiện đã tồn tại!", "danger")
        else:
            dao.update_linhkien(
                id=id,
                ten=ten,
                gia=gia,
                tien_cong=tien_cong,
                hangmuc_id=hangmuc_id
            )
            flash("Cập nhật linh kiện thành công!", "success")
            return redirect(url_for('quanly_linhkien'))

        return render_template('quanly/tao_or_xoa_lk.html', hangmucs=hangmucs, linhkien=lk)

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

    page = request.args.get('page', 1, type=int)
    hangmucs = dao.get_hangmuc_paginate(page=page, per_page=5)

    return render_template('quanly/hangmuc.html', hangmucs=hangmucs)



@app.route('/quanly/hangmuc/create', methods=['GET', 'POST'])
@login_required
def quanly_hangmuc_create():
    check = check_role(RoleEnum.QUANLY)
    if check:
        return check

    if request.method == 'POST':
        ten = request.form['ten'].strip()
        mo_ta = request.form.get('mo_ta', '').strip()

        if not dao.is_name_unique(HangMuc, ten, field_name='ten_hang_muc'):
            flash("Tên hạng mục đã tồn tại!", "danger")
            return render_template('quanly/tao_or_sua_hm.html', hangmuc=None)

        dao.create_hangmuc(ten=ten, mo_ta=mo_ta, quanly_id=current_user.id)
        flash("Tạo hạng mục thành công", "success")
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
        ten = request.form['ten'].strip()
        if not dao.is_name_unique(HangMuc, ten, exclude_id=id, field_name='ten_hang_muc'):
            flash("Tên hạng mục đã tồn tại!", "danger")
            return render_template('quanly/tao_or_sua_hm.html', hangmuc=hm)

        dao.update_hangmuc(id, ten=ten)
        flash("Cập nhật hạng mục thành công", "success")
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
    if current_user.role not in allowed_roles:
        abort(403)
    return None


if __name__ == '__main__':
    from project import admin
    from init import app

    app.run(debug=True)
