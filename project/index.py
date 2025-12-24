from flask import render_template, request, redirect, url_for, flash, abort, jsonify, make_response
from flask_login import login_user, logout_user, login_required, current_user
from init import app, login, db
from project import dao
from datetime import datetime, date

from sqlalchemy import func
from models import (RoleEnum, PhieuTiepNhan, Loi, Xe, HangMuc, LoaiXe, ChiTietSuaChua,
                    PhieuSuaChua, TenQuyDinhEnum, QuyDinh, PhieuThanhToan, Ptn_loi)


@app.route('/login')
def index():
    return render_template('login.html')
@login.user_loader
def load_user(pk):
    return dao.get_user_by_id(pk)
def check_role(*allowed_roles):
    if current_user.role not in allowed_roles:
        abort(403)
    return None
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

    tong_so_ptn = dao.count_phieu_tiep_nhan_today()
    max_sl = dao.get_quy_dinh_sl_xe_nhan()

    return render_template(
        'NVTiepNhan/tiepnhan.html',
        danh_sach_ptn=danh_sach_ptn,
        tong_so_ptn=tong_so_ptn,
        max_sl=max_sl
    )
@app.route('/tiepnhan/taophieu', methods=['GET', 'POST'])
@login_required
def tiepnhan_taophieu():
    check = check_role(RoleEnum.TIEPNHAN)
    if check:
        return check

    if request.method == 'POST':

        max_sl = dao.get_quy_dinh_sl_xe_nhan()
        if max_sl is None:
            flash("Không tìm thấy quy định về số lượng xe nhận!", "danger")
            return redirect(url_for('tiepnhan_taophieu'))

        sl_hom_nay = dao.count_phieu_tiep_nhan_today()

        if sl_hom_nay >= max_sl:
            flash(f"Hôm nay đã nhận đủ {max_sl} xe theo quy định! Không thể nhận thêm.", "warning")
            return redirect(url_for('tiepnhan_dashboard'))

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

    ptn = dao.get_phieu_tiep_nhan_by_id(id)
    if not ptn:
        flash("Phiếu tiếp nhận không tồn tại!", "danger")
        return redirect(url_for('tiepnhan_dashboard'))

    if dao.is_phieu_sc_confirmed(id):
        flash("Việc sửa chữa đã hoàn tất, không thể chỉnh sửa phiếu tiếp nhận được nữa!", "warning")
        return redirect(url_for('tiepnhan_dashboard'))

    if request.method == 'POST':
        new_loi_ids = request.form.getlist('loi_ids')
        description = request.form.get('description')
        new_sdt = request.form.get('customer_sdt')
        try:
            dao.update_phieu_tiep_nhan(id, new_loi_ids, description, new_sdt)
            if dao.is_phieu_sc_in_progress(id):
                flash("Cập nhật thành công, quá trình sửa chữa đang được tiến hành. "
                      "Hãy thông báo cho nhân viên sửa chữa!", "warning")
            else:
                flash("Cập nhật phiếu thành công!", "success")
            return redirect(url_for('tiepnhan_dashboard'))
        except Exception as e:
            flash(f"Lỗi khi cập nhật: {str(e)}", "danger")

    lois = dao.get_all_loi()
    loai_xes = LoaiXe

    return render_template(
        'NVTiepNhan/taophieu.html',
        ptn=ptn,
        lois=lois,
        loai_xes=loai_xes,
    )
@app.route('/tiepnhan/delete/<int:id>', methods=['POST'])
@login_required
def tiepnhan_delete(id):
    check = check_role(RoleEnum.TIEPNHAN)
    if check:
        return check

    if dao.check_start_sc(id):
        flash("Không thể xoá! Việc sửa chữa đang được tiến hành.", "danger")
        return redirect(url_for('tiepnhan_dashboard'))

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

    kw_cho = request.args.get('kw_cho', '')
    ngay_cho = request.args.get('ngay_cho', '')


    kw = request.args.get('kw', '')
    ngay = request.args.get('ngay', '')

    page_phieuchosua = request.args.get('page_phieuchosua', 1, type=int)
    page_pscs = request.args.get('page', 1, type=int)

    phieu_cho_sua = dao.get_ptn_cho_psc(page=page_phieuchosua, per_page=5, kw=kw_cho, ngay=ngay_cho)
    pscs = dao.get_all_psc(page=page_pscs, per_page=5, kw=kw, ngay=ngay)

    return render_template(
        'NVSuaChua/suachua.html',
        phieu_cho_sua=phieu_cho_sua,
        pscs=pscs,
        kw_cho=kw_cho,
        ngay_cho=ngay_cho,
        kw=kw,
        ngay=ngay
    )
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

    kw = request.args.get('kw', '').strip()
    ngay = request.args.get('ngay', '').strip()
    page = request.args.get('page', 1, type=int)

    phieu_thanh_toan_pagination = dao.get_phieu_thanh_toan(page=page, per_page=4, kw=kw, ngay=ngay)

    for psc in phieu_thanh_toan_pagination.items:
        pt = PhieuThanhToan.query.filter_by(phieu_sua_chua_id=psc.id).first()
        if pt:
            psc.da_thanh_toan = pt.da_thanh_toan
            psc.tong_tien = pt.tong_tien
        else:
            psc.da_thanh_toan = False
            psc.tong_tien = dao.tinh_tong_tien_phieu_sua_chua(psc.id)

    return render_template(
        'NVThuNgan/thungan.html',
        phieu_thanh_toan=phieu_thanh_toan_pagination,
        kw=kw,
        ngay=ngay
    )
@app.route('/thungan/chi-tiet/<int:psc_id>')
@login_required
def thungan_chi_tiet(psc_id):
    check = check_role(RoleEnum.THUNGAN)
    if check:
        return check

    psc = dao.get_psc_by_id(psc_id)
    if not psc or not psc.da_xac_nhan:
        flash("Phiếu không tồn tại hoặc chưa được xác nhận sửa xong!", "danger")
        return redirect(url_for('thungan_dashboard'))

    quy_dinh_vat = QuyDinh.query.filter_by(ten_quy_dinh=TenQuyDinhEnum.THUE_VAT).first()
    if quy_dinh_vat:
        vat_rate = float(quy_dinh_vat.noi_dung)
    else:
        vat_rate = 10

    if psc.phieu_thanh_toan:
        tong_that = psc.phieu_thanh_toan.tong_tien
        da_thanh_toan = psc.phieu_thanh_toan.da_thanh_toan
    else:
        tong_that = dao.tinh_tong_tien_phieu_sua_chua(psc_id)
        da_thanh_toan = False

    return render_template(
        'NVThuNgan/chi_tiet_thanh_toan.html',
        psc=psc,
        tong_that=tong_that,
        vat_rate=vat_rate,
        da_thanh_toan=da_thanh_toan
    )
@app.route('/thungan/xac-nhan-thanh-toan/<int:psc_id>', methods=['POST'])
@login_required
def thungan_xacnhan_thanh_toan(psc_id):
    check = check_role(RoleEnum.THUNGAN)
    if check:
        return check

    psc = PhieuSuaChua.query.get(psc_id)
    if not psc:
        flash("Không tìm thấy phiếu sửa chữa!", "danger")
        return redirect(url_for('thungan_dashboard'))

    from models import PhieuThanhToan

    tong = dao.tinh_tong_tien_phieu_sua_chua(psc_id)

    pt = PhieuThanhToan.query.filter_by(phieu_sua_chua_id=psc.id).first()
    if not pt:
        pt = PhieuThanhToan(
            phieu_sua_chua_id=psc.id,
            tong_tien=tong,
            thu_ngan_id=current_user.id,
            da_thanh_toan=True
        )
        db.session.add(pt)
    else:
        pt.da_thanh_toan = True
        pt.thu_ngan_id = current_user.id
        pt.ngay_thanh_toan = date.today()

    db.session.commit()

    flash("Đã xác nhận thanh toán!", "success")
    return redirect(url_for('thungan_chi_tiet', psc_id=psc.id))


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
        so_luong_list = request.form.getlist('so_luong[]')
        hangmuc_list = request.form.getlist('hangmuc[]')

        created_count = 0

        for idx in range(len(ten_list)):
            ten = ten_list[idx].strip()
            if not ten:
                continue

            try:
                gia = float(gia_list[idx])
                tien_cong = float(tien_cong_list[idx])
                so_luong = int(so_luong_list[idx])
            except:
                continue

            hangmuc_id = common_hangmuc if same_category else int(hangmuc_list[idx])

            ok, message = dao.create_linhkien(
                ten=ten,
                gia=gia,
                tien_cong=tien_cong,
                so_luong=so_luong,
                hangmuc_id=hangmuc_id,
                quanly_id=current_user.id
            )

            if ok:
                created_count += 1
            else:
                flash(message, "warning")

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
            so_luong=int(request.form['so_luong']),
            hangmuc_id=int(request.form['hangmuc'])
        )
        flash(msg, "success" if success else "warning")
        if success:
            return redirect(url_for('quanly_linhkien'))

    return render_template('quanly/tao_or_sua_lk.html', hangmucs=hangmucs, linhkien=lk)
@app.route('/api/linhkien/delete/<int:id>', methods=['DELETE'])
@login_required
def api_delete_linhkien(id):
    check = check_role(RoleEnum.QUANLY)
    if check:
        return jsonify({"message": "Không có quyền thực hiện hành động này"}), 403

    try:
        dao.delete_linhkien(id)
        return jsonify({"message": "Xóa linh kiện thành công"}), 200
    except Exception as e:
        return jsonify({"message": "Lỗi khi xóa linh kiện"}), 500
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
        ten_quy_dinh = request.form['ten_quy_dinh']
        noi_dung = request.form['noi_dung']
        label = TenQuyDinhEnum[ten_quy_dinh].label

        if ten_quy_dinh in [TenQuyDinhEnum.SL_XE_NHAN.name, TenQuyDinhEnum.THUE_VAT.name]:
            exist = QuyDinh.query.filter_by(ten_quy_dinh=ten_quy_dinh).first()
            if exist:
                flash(f'Quy định "{label}" đã tồn tại, không thể tạo trùng.', "danger")
                return redirect(url_for('quanly_quydinh_create'))

        dao.create_quydinh(
            ten_quy_dinh=ten_quy_dinh,
            noi_dung=noi_dung,
            quanly_id=current_user.id
        )
        flash(f'Tạo quy định "{label}" thành công', "success")
        return redirect(url_for('quanly_quydinh'))

    return render_template(
        'quanly/tao_or_sua_qd.html',
        quydinh=None,
        QuyDinhEnum=TenQuyDinhEnum
    )
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

    return render_template('quanly/tao_or_sua_qd.html', quydinh=qd, QuyDinhEnum=TenQuyDinhEnum)
@app.route('/api/quydinh/delete/<int:id>', methods=['DELETE'])
@login_required
def api_quydinh_delete(id):
    check = check_role(RoleEnum.QUANLY)
    if check:
        return jsonify({"message": "Không có quyền"}), 403

    quydinh = QuyDinh.query.get_or_404(id)

    if quydinh.ten_quy_dinh in ["SL_XE_NHAN", "THUE_VAT"]:
        return jsonify({"message": f"Không thể xóa quy định {quydinh.ten_quy_dinh}!"}), 400

    dao.delete_quydinh(id)
    return jsonify({"message": "Xóa quy định thành công"}), 200


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
@app.route('/api/hangmuc/delete/<int:id>', methods=['DELETE'])
@login_required
def api_hangmuc_delete(id):
    check = check_role(RoleEnum.QUANLY)
    if check:
        return jsonify({"message": "Không có quyền"}), 403

    try:
        success, message = dao.delete_hangmuc(id)
        status = 200 if success else 400
        return jsonify({"message": message}), status
    except Exception as e:
        return jsonify({"message": "Lỗi khi xóa hạng mục"}), 500


@app.route('/quanly/baocao', methods=['GET', 'POST'])
@login_required
def quanly_baocao():
    check = check_role(RoleEnum.QUANLY)
    if check:
        return check

    loai_thong_ke = request.args.get('loai_thong_ke', 'doanh_thu')
    kieu_thong_ke = request.args.get('kieu_thong_ke', 'thang')
    nam_chon = request.args.get('nam', datetime.now().year, type=int)
    thang_chon = request.args.get('thang', datetime.now().month, type=int)
    ngay_chon = request.args.get('ngay', '').strip()
    page = request.args.get('page', 1, type=int)
    has_submitted = request.args.get('action') == 'view'

    context = {
        'loai_thong_ke': loai_thong_ke,
        'kieu_thong_ke': kieu_thong_ke,
        'nam_chon': nam_chon,
        'thang_chon': thang_chon,
        'ngay_chon': ngay_chon,
        'has_submitted': has_submitted,
        'doanh_thu_data': [],
        'ty_le_xe_data': [],
        'loi_thuong_gap_data': [],
        'tong_doanh_thu': 0,
        'tieu_de_thong_ke': "",
        'pagination': None
    }

    if not has_submitted:
        return render_template('quanly/baocao.html', **context)

    try:
        if loai_thong_ke == 'doanh_thu':
            dao.xu_ly_thong_ke_doanh_thu(context, kieu_thong_ke, nam_chon, thang_chon, ngay_chon, page)
        elif loai_thong_ke == 'loai_xe':
            dao.xu_ly_thong_ke_loai_xe(context, nam_chon)
        elif loai_thong_ke == 'loi_thuong_gap':
            dao.xu_ly_thong_ke_loi(context, nam_chon)
    except Exception as e:
        flash(f"Lỗi khi thống kê: {str(e)}", "danger")

    return render_template('quanly/baocao.html', **context)

if __name__ == '__main__':
    from project import admin
    from init import app

    app.run(debug=True)
