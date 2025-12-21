from flask import flash
from init import db
from init import app
import hashlib
from models import (
    NhanVienBase, LinhKien, HangMuc, Loi, KhachHang, Xe,
    PhieuTiepNhan, Ptn_loi, LoaiXe, TenQuyDinhEnum, PhieuSuaChua, ChiTietSuaChua, PhieuThanhToan
)
from sqlalchemy.orm import joinedload
from datetime import date, datetime
from sqlalchemy import func, extract



def auth_user(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return NhanVienBase.query.filter(NhanVienBase.username == username.strip(),
                                     NhanVienBase.password == password).first()


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


def create_linhkien(ten, gia, tien_cong,so_luong, hangmuc_id, quanly_id):
    if not is_name_unique(LinhKien, ten, field_name='ten_linh_kien'):
        query = LinhKien.query.filter_by(ten_linh_kien=ten.strip(), hangmuc_id=hangmuc_id)
        if query.first():
            hangMuc = get_hangmuc_by_id(hangmuc_id)
            return False, f"Linh kiện '{ten}' đã tồn tại trong hạng mục '{hangMuc.ten_hang_muc}'!"

    lk = LinhKien(
        ten_linh_kien=ten.strip(),
        gia=gia,
        tien_cong=tien_cong,
        so_luong=so_luong,
        hangmuc_id=hangmuc_id,
        quanly_id=quanly_id
    )
    db.session.add(lk)
    db.session.commit()
    return True, "Tạo linh kiện thành công!"


def update_linhkien(id, ten, gia, tien_cong,so_luong, hangmuc_id):
    lk = get_linhkien_by_id(id)
    if not lk:
        return False, "Linh kiện không tồn tại"

    if not is_name_unique(LinhKien, ten, exclude_id=id, extra_filter={'hangmuc_id': hangmuc_id}):
        hangMuc = get_hangmuc_by_id(hangmuc_id)
        return False, f"Linh kiện '{ten}' đã tồn tại trong hạng mục '{hangMuc.ten_hang_muc}'!"

    lk.ten_linh_kien = ten.strip()
    lk.gia = gia
    lk.tien_cong = tien_cong
    lk.so_luong = so_luong
    lk.hangmuc_id = hangmuc_id
    db.session.commit()
    return True, "Cập nhật linh kiện thành công"


def delete_linhkien(id):
    lk = get_linhkien_by_id(id)
    if not lk:
        return False
    db.session.delete(lk)
    db.session.commit()
    return True


def get_all_linh_kien():
    return LinhKien.query.all()


def get_all_hangmuc():
    return HangMuc.query.all()


# cac ham thao tac voi quy dinh
from models import QuyDinh


def get_quydinh_paginate(page=1, per_page=5):
    return QuyDinh.query.paginate(page=page, per_page=per_page)


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


def get_all_linh_kien():
    return LinhKien.query.all()


# cac ham thao tac voi hang muc

def get_quydinh_paginate(page=1, per_page=5, keyword=None):
    query = QuyDinh.query
    if keyword:
        query = query.filter(QuyDinh.ten_quy_dinh.contains(keyword))
    return query.order_by(QuyDinh.id.asc()).paginate(page=page, per_page=per_page)


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


def get_hangmuc_by_id(hangmuc_id):
    return HangMuc.query.get(hangmuc_id)


def is_name_unique(model_class, name, exclude_id=None, field_name=None, extra_filter=None):
    if field_name is None:
        if model_class.__name__ == "LinhKien":
            field_name = 'ten_linh_kien'
        elif model_class.__name__ == "HangMuc":
            field_name = 'ten_hang_muc'
        else:
            field_name = 'ten'

    query = model_class.query.filter(getattr(model_class, field_name) == name.strip())

    if exclude_id:
        query = query.filter(model_class.id != exclude_id)


    if extra_filter:
        for k, v in extra_filter.items():
            query = query.filter(getattr(model_class, k) == v)

    return query.first() is None


# cac ham thao tac voi loi
def get_all_loi():
    return Loi.query.all()


def get_loi_by_id(id):
    return Loi.query.get(id)


def get_loi_by_name(name):
    return Loi.query.filter_by(ten_loi=name).first()


def get_loi_paginate(page=1, per_page=5):
    return Loi.query.order_by(Loi.id.asc()).paginate(page=page, per_page=per_page)


# cac thao tac voi xe
def get_xe_by_bien_so(bien_so):
    return Xe.query.options(joinedload(Xe.khachhang)).filter_by(bien_so=bien_so).first()


# cac ham thao tac voi phieu tiep nhan
def create_phieu_tiep_nhan(data, nvtn_id):
    with db.session.begin_nested():
        kh = KhachHang.query.filter_by(sdt=data['customer_sdt']).first()
        if not kh:
            kh = KhachHang(name=data['customer_name'], sdt=data['customer_sdt'])
            db.session.add(kh)
            db.session.flush()  # lay san id cua kh. Chua permanent, chi la temporary


        xe = get_xe_by_bien_so(data['xe_bien_so'])
        if not xe:
            xe = Xe(
                bien_so=data['xe_bien_so'],
                loai_xe=LoaiXe[data['xe_loai_xe']],
                khachhang_id=kh.id
            )
            db.session.add(xe)
            db.session.flush()  # lay san id cua xe


        ptn = PhieuTiepNhan(
            nvtn_id=nvtn_id,
            xe_id=xe.id,
            description=data.get('description')
        )
        db.session.add(ptn)
        db.session.flush()

        # chi tiet loi
        for loi_id in data['loi_ids']:
            ptn_loi = Ptn_loi(
                ptn_id=ptn.id,
                loi_id=int(loi_id)
            )
            db.session.add(ptn_loi)

    db.session.commit()


def get_all_phieu_tiep_nhan(page=1, per_page=5, kw=None, ngay=None):
    query = PhieuTiepNhan.query

    if kw:
        query = query.join(Xe).filter(Xe.bien_so.contains(kw))
    if ngay:
        query = query.filter(PhieuTiepNhan.ngay_tiep_nhan == ngay)

    return query.options(
        joinedload(PhieuTiepNhan.xe).joinedload(Xe.khachhang),
        joinedload(PhieuTiepNhan.nhan_vien_tiep_nhan),
        joinedload(PhieuTiepNhan.lois)
    ).order_by(PhieuTiepNhan.ngay_tiep_nhan.desc()).paginate(page=page, per_page=per_page)


def get_phieu_tiep_nhan_by_id(id):
    return PhieuTiepNhan.query.options(
        joinedload(PhieuTiepNhan.xe).joinedload(Xe.khachhang),
        joinedload(PhieuTiepNhan.lois)
    ).get(id)


def update_phieu_tiep_nhan(id, new_loi_ids, description=None):
    ptn = get_phieu_tiep_nhan_by_id(id)
    if not ptn:
        return None

    if description is not None:
        ptn.description = description

    ptn.lois.clear()
    for loi_id in new_loi_ids:
        loi = get_loi_by_id(loi_id)
        if loi:
            ptn.lois.append(loi)
    db.session.commit()
    return ptn


def delete_phieu_tiep_nhan(id):
    ptn = PhieuTiepNhan.query.get(id)
    if ptn:
        db.session.delete(ptn)
        db.session.commit()
        return True
    return False

def check_start_sc(ptn_id):
    psc = PhieuSuaChua.query.filter_by(ptn_id=ptn_id).first()
    return psc is not None

def is_phieu_sc_confirmed(ptn_id):
    psc = PhieuSuaChua.query.filter_by(ptn_id=ptn_id).first()
    if not psc:
        return False
    return psc.da_xac_nhan is True

def is_phieu_sc_in_progress(ptn_id):
    psc = PhieuSuaChua.query.filter_by(ptn_id=ptn_id).first()
    if not psc:
        return False

    return psc.da_xac_nhan != True

def get_quy_dinh_sl_xe_nhan():
    qd = QuyDinh.query.filter_by(ten_quy_dinh=TenQuyDinhEnum.SL_XE_NHAN).first()
    return int(qd.noi_dung) if qd else None


def count_phieu_tiep_nhan_today():
    return PhieuTiepNhan.query.filter_by(ngay_tiep_nhan=date.today()).count()


# def get_phieu_tiep_nhan_1():
#     ptns = PhieuTiepNhan.query.all()
#     res = []
#     for ptn in ptns:
#         bien_so = ptn.xe.bien_so
#         cus_name = ptn.xe.khachhang_id.name
#         res.append(f"{ptn.id} - {bien_so} - {cus_name}")
#     return res


# cac ham thao tac voi phieu sua chua

def get_ptn_cho_psc(page=1, per_page=5, kw=None, ngay=None):
    query = PhieuTiepNhan.query.filter(
        ~PhieuTiepNhan.phieu_sua_chuas.any()
    )

    if kw:
        query = query.join(PhieuTiepNhan.xe).filter(Xe.bien_so.contains(kw))

    if ngay:
        query = query.filter(PhieuTiepNhan.ngay_tiep_nhan == ngay)

    return query.options(
        joinedload(PhieuTiepNhan.xe).joinedload(Xe.khachhang),
        joinedload(PhieuTiepNhan.lois)
    ).order_by(PhieuTiepNhan.ngay_tiep_nhan.desc()).paginate(page=page, per_page=per_page)


def create_psc(ptn_id, nvsc_id):
    ton_tai_psc = PhieuSuaChua.query.filter_by(ptn_id=ptn_id).first()
    if ton_tai_psc:
        return ton_tai_psc

    psc = PhieuSuaChua(ptn_id=ptn_id, nvsc_id=nvsc_id, tong_tien=0)
    db.session.add(psc)
    db.session.commit()
    return psc


def get_psc_by_id(psc_id):
    return PhieuSuaChua.query.options(
        joinedload(PhieuSuaChua.chi_tiet_sua_chuas).joinedload(ChiTietSuaChua.linh_kien),
        joinedload(PhieuSuaChua.phieu_tiep_nhan).joinedload(PhieuTiepNhan.xe).joinedload(Xe.khachhang),
        joinedload(PhieuSuaChua.phieu_tiep_nhan).joinedload(PhieuTiepNhan.lois),
    ).get(psc_id)


def add_lk_to_psc(psc_id, linh_kien_id, so_luong):
    psc = get_psc_by_id(psc_id)
    if not psc:
        return False, "Phiếu sửa chữa không tồn tại"

    linh_kien = get_linhkien_by_id(linh_kien_id)
    if not linh_kien:
        return False, "Linh kiện không tồn tại"

    if linh_kien.so_luong < so_luong:
        return False, f"Số lượng linh kiện '{linh_kien.ten_linh_kien}' trong kho không đủ ({linh_kien.so_luong})"

    ctsc = ChiTietSuaChua.query.filter_by(psc_id=psc_id, linh_kien_id=linh_kien_id).first()
    if ctsc:

        ctsc.so_luong += so_luong
        thanh_tien = linh_kien.gia * so_luong
    else:
        ctsc = ChiTietSuaChua(
            psc_id=psc_id,
            linh_kien_id=linh_kien_id,
            so_luong=so_luong,
            don_gia=linh_kien.gia
        )
        db.session.add(ctsc)
        thanh_tien = linh_kien.gia * so_luong

    linh_kien.so_luong -= so_luong

    psc.tong_tien = (psc.tong_tien or 0) + thanh_tien

    db.session.commit()
    return True, "Thêm linh kiện thành công"


def get_all_psc(page=1, per_page=5, kw=None, ngay=None):
    query = PhieuSuaChua.query

    if kw:
        query = query.join(PhieuSuaChua.phieu_tiep_nhan).join(PhieuTiepNhan.xe).filter(Xe.bien_so.contains(kw))
    if ngay:
        query = query.filter(PhieuSuaChua.ngay_sua_chua == ngay)

    return query.options(
        joinedload(PhieuSuaChua.phieu_tiep_nhan).joinedload(PhieuTiepNhan.xe).joinedload(Xe.khachhang),
        joinedload(PhieuSuaChua.nhan_vien_sua_chua)
    ).order_by(PhieuSuaChua.id.desc()).paginate(page=page, per_page=per_page)



def delete_psc(psc_id):
    psc = PhieuSuaChua.query.get(psc_id)
    if not psc:
        return False, "Phiếu sửa chữa không tồn tại"

    for ctsc in psc.chi_tiet_sua_chuas:
        linh_kien = LinhKien.query.get(ctsc.linh_kien_id)
        if linh_kien:
            linh_kien.so_luong += ctsc.so_luong
            db.session.add(linh_kien)

    db.session.delete(psc)
    db.session.commit()
    return True, "Xóa phiếu thành công"

def delete_chitiet_psc(ctsc_id):
    ctsc = ChiTietSuaChua.query.get(ctsc_id)
    if not ctsc:
        return False, "Chi tiết sửa chữa không tồn tại"

    linh_kien = LinhKien.query.get(ctsc.linh_kien_id)
    if linh_kien:
        linh_kien.so_luong += ctsc.so_luong
        db.session.add(linh_kien)

    psc = PhieuSuaChua.query.get(ctsc.psc_id)
    so_tien_can_tru = ctsc.don_gia * ctsc.so_luong
    psc.tong_tien = max(0, (psc.tong_tien or 0) - so_tien_can_tru)
    db.session.add(psc)

    db.session.delete(ctsc)
    db.session.commit()

    return True, "Đã xóa chi tiết phiếu thành công"



def xac_nhan(psc_id):
    psc = PhieuSuaChua.query.get(psc_id)
    if not psc:
        return None
    psc.da_xac_nhan = True
    db.session.commit()
    return psc


# cac ham thao tac voi khach hang
def get_kh_by_sdt(sdt):
    return KhachHang.query.filter_by(sdt=sdt).first()


#====================================================
#Ham dung de tinh tong chi phi sua xe
def tinh_tong_tien_phieu_sua_chua(psc_id):
    psc = PhieuSuaChua.query.get(psc_id)
    if not psc:
        return 0.0

    vat_rule = QuyDinh.query.filter_by(ten_quy_dinh=TenQuyDinhEnum.THUE_VAT).first()
    vat_percent = float(vat_rule.noi_dung) if vat_rule else 0.0

    vat = vat_percent / 100.0

    tien_linh_kien = 0.0
    tien_cong = 0.0

    for ct in psc.chi_tiet_sua_chuas:
        tien_linh_kien += ct.so_luong * ct.don_gia
        tien_cong += ct.so_luong * (ct.linh_kien.tien_cong or 0)

    tong_truoc_thue = tien_linh_kien + tien_cong
    tong_sau_thue = tong_truoc_thue * (1 + vat)

    return round(tong_sau_thue)

def get_phieu_thanh_toan(page=1, per_page=10, kw=None, ngay=None):
    query = PhieuSuaChua.query.filter_by(da_xac_nhan=True) \
        .order_by(PhieuSuaChua.ngay_sua_chua.desc())

    if kw:
        query = query.join(PhieuTiepNhan, PhieuSuaChua.ptn_id == PhieuTiepNhan.id) \
            .join(Xe, PhieuTiepNhan.xe_id == Xe.id) \
            .filter(Xe.bien_so.ilike(f"%{kw}%"))

    if ngay:
        query = query.filter(PhieuSuaChua.ngay_sua_chua == ngay)

    return query.paginate(page=page, per_page=per_page, error_out=False)


def lay_gia_tri_quy_dinh(ten_quy_dinh):
    qd = QuyDinh.query.filter_by(ten_quy_dinh=ten_quy_dinh).first()
    if qd and qd.noi_dung:
        try:
            return float(qd.noi_dung)
        except:
            return 0.1
    return 0.1


def tao_phieu_thanh_toan(phieu_sua_chua_id, tong_tien, thu_ngan_id):
    pt = PhieuThanhToan(
        phieu_sua_chua_id=phieu_sua_chua_id,
        tong_tien=tong_tien,
        thu_ngan_id=thu_ngan_id
    )
    db.session.add(pt)
    db.session.commit()
    return pt


def revenue_by_specific_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
    except ValueError:
        return 0

    result = (
        db.session.query(
            func.sum(PhieuThanhToan.tong_tien).label('total')
        )
        .filter(func.date(PhieuThanhToan.ngay_thanh_toan) == date_obj.date())
        .scalar()
    )

    return result or 0


def revenue_by_day_in_month(year=None, month=None):
    from calendar import monthrange

    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month

    actual_data = (
        db.session.query(
            func.extract('day', PhieuThanhToan.ngay_thanh_toan).label('day'),
            func.sum(PhieuThanhToan.tong_tien).label('total')
        )
        .filter(
            func.extract('year', PhieuThanhToan.ngay_thanh_toan) == year,
            func.extract('month', PhieuThanhToan.ngay_thanh_toan) == month
        )
        .group_by(func.extract('day', PhieuThanhToan.ngay_thanh_toan))
        .all()
    )

    data_dict = {int(row[0]): row[1] for row in actual_data}

    num_days = monthrange(year, month)[1]
    result = []
    for day in range(1, num_days + 1):
        total = data_dict.get(day, 0)
        result.append((day, total))

    return result


def revenue_by_month(year=None):
    if year is None:
        year = datetime.now().year

    actual_data = (
        db.session.query(
            func.extract('month', PhieuThanhToan.ngay_thanh_toan).label('month'),
            func.sum(PhieuThanhToan.tong_tien).label('total')
        )
        .filter(func.extract('year', PhieuThanhToan.ngay_thanh_toan) == year)
        .group_by(func.extract('month', PhieuThanhToan.ngay_thanh_toan))
        .all()
    )

    data_dict = {int(row[0]): row[1] for row in actual_data}

    result = []
    for month in range(1, 13):
        total = data_dict.get(month, 0)
        result.append((month, total))

    return result


def revenue_by_quarter(year=None):
    if year is None:
        year = datetime.now().year

    actual_data = (
        db.session.query(
            func.extract('quarter', PhieuThanhToan.ngay_thanh_toan).label('quarter'),
            func.sum(PhieuThanhToan.tong_tien).label('total')
        )
        .filter(func.extract('year', PhieuThanhToan.ngay_thanh_toan) == year)
        .group_by(func.extract('quarter', PhieuThanhToan.ngay_thanh_toan))
        .all()
    )

    data_dict = {int(row[0]): row[1] for row in actual_data}

    result = []
    for quarter in range(1, 5):
        total = data_dict.get(quarter, 0)
        result.append((quarter, total))

    return result


def ty_le_loai_xe_by_year(year=None):
    if year is None:
        year = datetime.now().year

    return (
        db.session.query(
            Xe.loai_xe,
            func.count(PhieuTiepNhan.id).label('so_luong')
        )
        .join(PhieuTiepNhan, PhieuTiepNhan.xe_id == Xe.id)
        .filter(extract('year', PhieuTiepNhan.ngay_tiep_nhan) == year)
                .group_by(Xe.loai_xe)
                .order_by(func.count(PhieuTiepNhan.id).desc())
                .all()
            )


def top_loi_thuong_gap_by_year(year=None, limit=10):
    if year is None:
        year = datetime.now().year

    return (
        db.session.query(
            Loi.ten_loi,
            func.count(Ptn_loi.loi_id).label('so_lan')
        )
        .join(Ptn_loi, Loi.id == Ptn_loi.loi_id)

        .join(PhieuTiepNhan, Ptn_loi.ptn_id == PhieuTiepNhan.id)
        .filter(extract('year', PhieuTiepNhan.ngay_tiep_nhan) == year)
        .group_by(Loi.id, Loi.ten_loi)
        .order_by(func.count(Ptn_loi.loi_id).desc())
        .limit(limit)
        .all()
    )


def revenue_by_day_in_month_paginated(year=None, month=None, page=1, per_page=7):

    from calendar import monthrange

    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month

    actual_data = (
        db.session.query(
            func.extract('day', PhieuThanhToan.ngay_thanh_toan).label('day'),
            func.sum(PhieuThanhToan.tong_tien).label('total')
        )
        .filter(
            func.extract('year', PhieuThanhToan.ngay_thanh_toan) == year,
            func.extract('month', PhieuThanhToan.ngay_thanh_toan) == month
        )
        .group_by(func.extract('day', PhieuThanhToan.ngay_thanh_toan))
        .all()
    )

    data_dict = {int(row[0]): row[1] for row in actual_data}

    num_days = monthrange(year, month)[1]
    all_data = []
    for day in range(1, num_days + 1):
        total = data_dict.get(day, 0)
        all_data.append((day, total))

    # Tạo pagination object
    class SimplePagination:
        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page if total > 0 else 1

        @property
        def has_prev(self):
            return self.page > 1

        @property
        def has_next(self):
            return self.page < self.pages

        @property
        def prev_num(self):
            return self.page - 1 if self.has_prev else None

        @property
        def next_num(self):
            return self.page + 1 if self.has_next else None

        def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
            last = 0
            for num in range(1, self.pages + 1):
                if num <= left_edge or \
                        (num > self.page - left_current - 1 and num < self.page + right_current) or \
                        num > self.pages - right_edge:
                    if last + 1 != num:
                        yield None
                    yield num
                    last = num

    total = len(all_data)
    start = (page - 1) * per_page
    end = start + per_page
    items = all_data[start:end]
    return SimplePagination(items, page, per_page, total)
