import hashlib
from models import NhanVienBase, LinhKien, HangMuc, QuyDinh
from init import db

def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return NhanVienBase.query.filter(NhanVienBase.username==username.strip(),
                             NhanVienBase.password==password).first()

def get_user_by_id(id):
    return NhanVienBase.query.get(id)

# cac ham thao tac voi linh kien

def get_linhkien_paginate(page=1, per_page=5, hangmuc_id=None, keyword=None):
    query = LinhKien.query

    if hangmuc_id:
        query = query.filter(LinhKien.hangmuc_id == hangmuc_id)

    if keyword:
        query = query.filter(LinhKien.ten_linh_kien.contains(keyword))

    return query.order_by(LinhKien.id.asc()).paginate(page=page, per_page=per_page)

def get_linhkien_by_id(id):
    return LinhKien.query.get(id)

def create_linhkien(ten, gia, tien_cong, hangmuc_id, quanly_id):
    lk = LinhKien(
        ten_linh_kien=ten,
        gia=gia,
        tien_cong=tien_cong,
        hangmuc_id=hangmuc_id,
        quanly_id=quanly_id
    )
    db.session.add(lk)
    db.session.commit()

def update_linhkien(id, ten, gia, tien_cong, hangmuc_id):
    lk = get_linhkien_by_id(id)
    if lk:
        lk.ten_linh_kien = ten
        lk.gia = gia
        lk.tien_cong = tien_cong
        lk.hangmuc_id = hangmuc_id
        db.session.commit()


def delete_linhkien(id):
    lk = get_linhkien_by_id(id)
    if not lk:
        return False
    db.session.delete(lk)
    db.session.commit()
    return True

# cac ham thao tac voi quy dinh

def get_quydinh_paginate(page=1, per_page=5, keyword=None):
    query = QuyDinh.query
    if keyword:
        query = query.filter(QuyDinh.ten_quy_dinh.contains(keyword))
    return query.order_by(QuyDinh.id.asc()).paginate(page=page, per_page=per_page)

def get_quydinh_by_id(id):
    return QuyDinh.query.get(id)

def create_quydinh(ten_quy_dinh, noi_dung, quanly_id):
    qd = QuyDinh(ten_quy_dinh=ten_quy_dinh, noi_dung=noi_dung, quanly_id=quanly_id)
    db.session.add(qd)
    db.session.commit()
    return qd

def update_quydinh(id, ten_quy_dinh, noi_dung):
    qd = get_quydinh_by_id(id)
    if not qd:
        return None
    qd.ten_quy_dinh = ten_quy_dinh
    qd.noi_dung = noi_dung
    db.session.commit()
    return qd

def delete_quydinh(id):
    qd = get_quydinh_by_id(id)
    if not qd:
        return False
    db.session.delete(qd)
    db.session.commit()
    return True

#  cac thao tac voi hang muc

def get_all_hangmuc():
    return HangMuc.query.all()

def get_hangmuc_by_id(id):
    return HangMuc.query.get(id)

def create_hangmuc(ten, quanly_id, mo_ta=None):
    hm = HangMuc(
        ten_hang_muc=ten,
        mo_ta=mo_ta,
        quanly_id=quanly_id
    )
    db.session.add(hm)
    db.session.commit()

def update_hangmuc(id, ten):
    hm = get_hangmuc_by_id(id)
    if hm:
        hm.ten_hang_muc = ten
        db.session.commit()

def delete_hangmuc(id):
    hm = get_hangmuc_by_id(id)
    if hm:
        if hm.linh_kiens:
            return False, "Hạng mục này vẫn còn linh kiện, không thể xóa!"
        db.session.delete(hm)
        db.session.commit()
        return True, "Xóa hạng mục thành công!"

def get_hangmuc_paginate(page=1, per_page=5, keyword=None):
    query = HangMuc.query
    if keyword:
        query = query.filter(HangMuc.ten_hang_muc.contains(keyword))
    return query.order_by(HangMuc.id.asc()).paginate(page=page, per_page=per_page)

def is_name_unique(model_class, name, exclude_id=None, field_name=None):

    if field_name is None:
        if model_class.__name__ == "LinhKien":
            field_name = 'ten_linh_kien'
        elif model_class.__name__ == "HangMuc":
            field_name = 'ten_hang_muc'
        elif model_class.__name__ == "QuyDinh":
            field_name = 'ten_quy_dinh'
        else:
            field_name = 'ten'

    query = model_class.query.filter(getattr(model_class, field_name) == name.strip())
    if exclude_id:
        query = query.filter(model_class.id != exclude_id)
    return query.first() is None



