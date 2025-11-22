from flask import render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from init import app, login
from project import dao
from models import RoleEnum, LoaiXe, ChiTietSuaChua, HangMuc, LoaiXe, ChiTietSuaChua, PhieuSuaChua


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


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('login.html')


@app.route('/tiepnhan')
@login_required
def tiepnhan_dashboard():
    check = check_role(RoleEnum.TIEPNHAN)
    if check:
        return check

    kw = request.args.get('kw')
    ngay = request.args.get('ngay')

    page = request.args.get('page', 1, type=int)
    danh_sach_ptn = dao.get_all_phieu_tiep_nhan(page=page, per_page=5, kw=kw, ngay=ngay)

    return render_template(
        'NVTiepNhan/tiepnhan.html',
        danh_sach_ptn=danh_sach_ptn
    )


@app.route('/tiepnhan/taophieu', methods=['GET', 'POST'])
@login_required
def tiepnhan_taophieu():
    check = check_role(RoleEnum.TIEPNHAN)
    if check:
        return check

    if request.method == 'POST':
        data = {
            "customer_name": request.form.get('customer_name'),
            "customer_sdt": request.form.get('customer_sdt'),
            "xe_bien_so": request.form.get('xe_bien_so'),
            "xe_loai_xe": request.form.get('xe_loai_xe'),
            "loi_ids": request.form.getlist('loi_ids'),
            "description": request.form.get('description')
        }
        try:
            dao.create_phieu_tiep_nhan(data=data, nvtn_id=current_user.id)
            flash("Tạo phiếu tiếp nhận thành công!", "success")
            return redirect(url_for('tiepnhan_dashboard'))
        except Exception as e:
            flash(f"Đã xảy ra lỗi: {str(e)}", "danger")
            return redirect(url_for('tiepnhan_taophieu'))

    lois = dao.get_all_loi()
    loai_xes = LoaiXe

    return render_template('NVTiepNhan/taophieu.html', lois=lois, loai_xes=loai_xes)


@app.route('/tiepnhan/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def tiepnhan_edit(id):
    check = check_role(RoleEnum.TIEPNHAN)
    if check:
        return check

    if request.method == 'POST':
        new_loi_ids = request.form.getlist('loi_ids')
        description = request.form.get('description')
        try:
            dao.update_phieu_tiep_nhan(id, new_loi_ids, description)
            flash("Cập nhật phiếu thành công!", "success")
            return redirect(url_for('tiepnhan_dashboard'))
        except Exception as e:
            flash(f"Lỗi khi cập nhật: {str(e)}", "danger")

    # xu ly khi GET
    ptn = dao.get_phieu_tiep_nhan_by_id(id)
    if not ptn:
        flash("Phiếu tiếp nhận không tồn tại!", "danger")
        return redirect(url_for('tiepnhan_dashboard'))

    lois = dao.get_all_loi()
    loai_xes = LoaiXe

    return render_template(
        'NVTiepNhan/taophieu.html',
        ptn=ptn,
        lois=lois,
        loai_xes=loai_xes
    )


@app.route('/tiepnhan/delete/<int:id>', methods=['POST'])
@login_required
def tiepnhan_delete(id):
    check = check_role(RoleEnum.TIEPNHAN)
    if check:
        return check

    if dao.delete_phieu_tiep_nhan(id):
        flash("Xóa phiếu tiếp nhận thành công!", "success")
    else:
        flash("Xóa thất bại, phiếu không tồn tại!", "danger")

    return redirect(url_for('tiepnhan_dashboard'))


@app.route('/request/kiem_tra_bien_so', methods=['POST'])
@login_required
def kiem_tra_bien_so():
    data = request.get_json()
    bien_so = data.get('bien_so')

    if not bien_so:
        return jsonify({'found': False})

    xe = dao.get_xe_by_bien_so(bien_so)
    if xe:
        return jsonify({'found': True,
                        'loai_xe': xe.loai_xe.name,
                        'kh_name': xe.khachhang.name,
                        'kh_sdt': xe.khachhang.sdt,
                        'message': 'Da tim thay thong tin xe co san trong db'
                        })
    return jsonify({'found': False})


@app.route('/suachua')
@login_required
def suachua_dashboard():
    check = check_role(RoleEnum.SUACHUA)
    if check:
        return check

    kw = request.args.get('kw')  # keyword lọc theo biển số xe
    ngay = request.args.get('ngay')  # ngày lọc
    page_phieuchosua = request.args.get('page_phieuchosua', 1, type=int)
    phieu_cho_sua = dao.get_ptn_cho_psc(page=page_phieuchosua, per_page=5, kw=kw, ngay=ngay)

    page = request.args.get('page', 1, type=int)
    pscs = dao.get_all_psc(page=page, per_page=5, kw=kw, ngay=ngay)

    return render_template('NVSuaChua/suachua.html', phieu_cho_sua=phieu_cho_sua, pscs=pscs, kw=kw, ngay=ngay)


@app.route('/suachua/nhan-phieu/<int:ptn_id>', methods=['POST'])
@login_required
def suachua_nhan_phieu(ptn_id):
    check = check_role(RoleEnum.SUACHUA)
    if check:
        return check

    psc = dao.create_psc(ptn_id, current_user.id)
    flash("Da nhan phieu, them linh kien")
    return redirect(url_for('suachua_chi_tiet', psc_id=psc.id))


@app.route('/suachua/chi-tiet/<int:psc_id>', methods=['GET', 'POST'])
@login_required
def suachua_chi_tiet(psc_id):
    check = check_role(RoleEnum.SUACHUA)
    if check:
        return check

    if request.method == 'POST':
        linh_kien_id = request.form.get('linh_kien_id')
        so_luong = request.form.get('so_luong', 1, type=int)

        ok, message = dao.add_lk_to_psc(psc_id, linh_kien_id, so_luong)
        flash(message, "success" if ok else "danger")
        return redirect(url_for('suachua_chi_tiet', psc_id=psc_id))

    # show trang
    psc = dao.get_psc_by_id(psc_id)
    if not psc:
        flash("Phiếu sửa chữa không tồn tại.", "danger")
        return redirect(url_for('suachua_dashboard'))

    if psc.nvsc_id != current_user.id:
        flash("Bạn không có quyền truy cập phiếu này.", "danger")
        return redirect(url_for('suachua_dashboard'))

    all_linh_kien = dao.get_all_linh_kien()

    return render_template(
        'NVSuaChua/chitiet_suachua.html',
        psc=psc,
        all_linh_kien=all_linh_kien
    )


@app.route('/suachua/delete/<int:psc_id>', methods=['POST'])
@login_required
def suachua_delete(psc_id):
    check = check_role(RoleEnum.SUACHUA)
    if check:
        return check

    ok, message = dao.delete_psc(psc_id)
    flash(message, "success" if ok else "danger")
    return redirect(url_for('suachua_dashboard'))


@app.route('/suachua/chi_tiet/<int:ctsc_id>', methods=['POST'])
@login_required
def suachua_delete_item(ctsc_id):
    check = check_role(RoleEnum.SUACHUA)
    if check:
        return check

    ctsc = ChiTietSuaChua.query.get(ctsc_id)
    if not ctsc_id:
        flash("Chi tiet ko ton tai")
        return redirect(url_for('suachua_dashboard'))

    psc_id = ctsc.psc_id

    ok, message = dao.delete_chitiet_psc(ctsc_id)
    flash(message, "success" if ok else "danger")
    return redirect(url_for('suachua_chi_tiet', psc_id=psc_id))

@app.route('/suachua/xacnhan/<int:psc_id>', methods=['POST'])
@login_required
def suachua_xac_nhan(psc_id):
    # kiểm tra quyền
    check = check_role(RoleEnum.SUACHUA)
    if check:
        flash("Bạn không có quyền thực hiện hành động này.", "danger")
        return redirect(url_for('suachua_dashboard'))

    psc = dao.xac_nhan(psc_id)
    if not psc:
        flash("Phiếu sửa chữa không tồn tại.", "danger")
        return redirect(url_for('suachua_dashboard'))

    flash(f"Phiếu #{psc.id} đã được xác nhận.", "success")
    return redirect(url_for('suachua_dashboard'))


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
        gia = float(request.form['gia'])
        tien_cong = float(request.form['tien_cong'])
        hangmuc_id = int(request.form['hangmuc'])

        ok, message = dao.create_linhkien(ten, gia, tien_cong, hangmuc_id, current_user.id)
        flash(message, "success" if ok else "danger")
        if ok:
            return redirect(url_for('quanly_linhkien'))
        else:
            return render_template('quanly/tao_or_xoa_lk.html', hangmucs=hangmucs, linhkien=None)

    return render_template('quanly/tao_or_xoa_lk.html', hangmucs=hangmucs, linhkien=None)


@app.route('/quanly/linhkien/create-multi', methods=['GET', 'POST'])
@login_required
def quanly_linhkien_create_multi():
    check = check_role(RoleEnum.QUANLY)
    if check:
        return check

    hangmucs = dao.get_all_hangmuc()

    if request.method == 'POST':
        same_category = request.form.get('same_category') == '1'
        common_hangmuc = int(request.form.get('common_hangmuc')) if same_category else None

        ten_list = request.form.getlist('ten[]')
        gia_list = request.form.getlist('gia[]')
        tien_cong_list = request.form.getlist('tien_cong[]')
        hangmuc_list = request.form.getlist('hangmuc[]')

        created_count = 0

        for idx in range(len(ten_list)):
            ten = ten_list[idx].strip()
            if not ten:
                continue

            try:
                gia = float(gia_list[idx])
                tien_cong = float(tien_cong_list[idx])
            except:
                continue

            hangmuc_id = common_hangmuc if same_category else int(hangmuc_list[idx])

            ok, message = dao.create_linhkien(
                ten=ten,
                gia=gia,
                tien_cong=tien_cong,
                hangmuc_id=hangmuc_id,
                quanly_id=current_user.id
            )

            if ok:
                created_count += 1
            else:
                flash(message, "warning")  # flash từng linh kiện trùng

        if created_count == 0:
            flash("Chưa có linh kiện nào hợp lệ để tạo!", "warning")
            return render_template('quanly/tao_nhieu_lk.html', hangmucs=hangmucs)

        flash(f"Tạo thành công {created_count} linh kiện!", "success")
        return redirect(url_for('quanly_linhkien'))

    return render_template('quanly/tao_nhieu_lk.html', hangmucs=hangmucs)


@app.route('/quanly/linhkien/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def quanly_linhkien_edit(id):
    check = check_role(RoleEnum.QUANLY)
    if check:
        return check

    lk = dao.get_linhkien_by_id(id)
    hangmucs = dao.get_all_hangmuc()
    if request.method == 'POST':
        success, msg = dao.update_linhkien(
            id=id,
            ten=request.form['ten'],
            gia=float(request.form['gia']),
            tien_cong=float(request.form['tien_cong']),
            hangmuc_id=int(request.form['hangmuc'])
        )
        flash(msg, "success" if success else "warning")
        if success:
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


@app.route('/quanly/linhkien/delete-multi', methods=['GET', 'POST'])
@login_required
def quanly_linhkien_delete_multi():
    check = check_role(RoleEnum.QUANLY)
    if check:
        return check

    if request.method == 'POST':
        ids = request.form.getlist('ids')
        if not ids:
            flash("Bạn chưa chọn linh kiện nào để xoá!", "warning")
            return redirect(url_for('quanly_linhkien_delete_multi',
                                    page=request.args.get('page', 1),
                                    hangmuc=request.args.get('hangmuc'),
                                    q=request.args.get('q')))
        deleted_count = 0
        for id in ids:
            if dao.delete_linhkien(id):
                deleted_count += 1
        flash(f"Đã xóa {deleted_count} linh kiện!", "success")
        return redirect(url_for('quanly_linhkien'))

    page = request.args.get('page', 1, type=int)
    hangmuc_id = request.args.get('hangmuc', type=int)
    keyword = request.args.get('q', '')
    linhkiens = dao.get_linhkien_paginate(page=page, per_page=5, hangmuc_id=hangmuc_id, keyword=keyword)
    hangmucs = dao.get_all_hangmuc()
    return render_template('quanly/xoa_nhieu_lk.html', linhkiens=linhkiens,
                           hangmucs=hangmucs,
                           selected_hangmuc=hangmuc_id)


@app.route('/quanly/quydinh')
@login_required
def quanly_quydinh():
    check = check_role(RoleEnum.QUANLY)
    if check:
        return check

    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('q', '')
    quydinhs = dao.get_quydinh_paginate(page=page, per_page=5, keyword=keyword)

    return render_template('quanly/quydinh.html', quydinhs=quydinhs, keyword=keyword)


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
    keyword = request.args.get('q', '')
    hangmucs = dao.get_hangmuc_paginate(page=page, per_page=5, keyword=keyword)

    return render_template('quanly/hangmuc.html', hangmucs=hangmucs, keyword=keyword)


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
        ten_moi = request.form['ten'].strip()

        if not dao.is_name_unique(HangMuc, ten_moi, exclude_id=id, field_name='ten_hang_muc'):
            flash("Tên hạng mục đã tồn tại!", "danger")
            return render_template('quanly/tao_or_sua_hm.html', hangmuc=hm)

        dao.update_hangmuc(id, ten_moi)
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
