from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.testing.provision import drop_db

from init import db, app
from flask_login import UserMixin
from enum import Enum as UserEnum
from datetime import date
import hashlib


class RoleEnum(UserEnum):
    QUANLY = "quanly"
    TIEPNHAN = "tiepnhan"
    SUACHUA = "suachua"
    THUNGAN = "thungan"

class NhanVienBase(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    ngay_sinh = Column(Date)
    sdt = Column(String(15))
    email = Column(String(100))
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    quy_dinhs = relationship("QuyDinh", backref="quanly", lazy=True)
    linh_kiens = relationship("LinhKien", backref="quanly", lazy=True)

    def __str__(self):
        return f"{self.name} ({self.role.value})"

class QuyDinh(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_quy_dinh = Column(String(50), nullable=False)
    noi_dung = Column(String(100), nullable=False)
    quanly_id = Column(Integer, ForeignKey(NhanVienBase.id), nullable=False)


class HangMuc(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_hang_muc = Column(String(100), nullable=False)
    mo_ta = Column(String(255), nullable=True)
    quanly_id = Column(Integer, ForeignKey(NhanVienBase.id), nullable=False)
    linh_kiens = relationship("LinhKien",backref="hangmuc",lazy=True,cascade="all, delete-orphan")

class LinhKien(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_linh_kien = Column(String(100), nullable=False)
    gia = Column(Float, nullable=False)
    tien_cong = Column(Float, nullable=True, default=0)
    quanly_id = Column(Integer, ForeignKey(NhanVienBase.id), nullable=False)
    hangmuc_id = Column(Integer, ForeignKey(HangMuc.id))

class KhachHang(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    sdt = Column(String(15), nullable=False, unique=True)

class LoaiXe(UserEnum):
    XE_MAY = "Xe may"
    O_TO = "O to"
    XE_TAI = "Xe tai"
    SUV = "SUV"
    Sedan = "Sedan"

class Xe(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    bien_so = Column(String(20), nullable=False, unique=True)
    loai_xe = Column(Enum(LoaiXe), nullable=False)
    khachhang_id = Column(Integer, ForeignKey(KhachHang.id), nullable=False)
    khachhang = relationship('KhachHang', backref='xes', lazy=True)
    phieu_tiep_nhans = relationship('PhieuTiepNhan', backref='xe', lazy=True)

class Loi(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ten_loi = Column(String(100), nullable=False)

class Ptn_loi(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    ptn_id = Column(Integer, ForeignKey('phieu_tiep_nhan.id'), nullable=False)
    loi_id = Column(Integer, ForeignKey(Loi.id), nullable=False)

class PhieuTiepNhan(db.Model):
    __tablename__ = 'phieu_tiep_nhan'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nvtn_id = Column(Integer, ForeignKey(NhanVienBase.id), nullable=False)
    xe_id = Column(Integer, ForeignKey(Xe.id), nullable=False)
    ngay_tiep_nhan = Column(Date, nullable=False, default=date.today)
    description = db.Column(db.String(255))
    phieu_sua_chuas = relationship('PhieuSuaChua', backref='phieu_tiep_nhan', lazy=True, cascade='all, delete-orphan')
    lois = relationship('Loi', secondary=Ptn_loi.__table__,
                        backref='phieu_tiep_nhans', lazy=True)
    nhan_vien_tiep_nhan = relationship('NhanVienBase',
                                       backref='phieu_tiep_nhans',
                                       lazy=True)

class PhieuSuaChua(db.Model):
    __tablename__ = 'phieu_sua_chua'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ptn_id = Column(Integer, ForeignKey(PhieuTiepNhan.id), nullable=False)
    nvsc_id = Column(Integer, ForeignKey(NhanVienBase.id), nullable=False)
    ngay_sua_chua = Column(Date, nullable=False, default=date.today)
    tong_tien = Column(Float, nullable=False, default=0)
    da_xac_nhan = Column(Boolean, default=False)
    chi_tiet_sua_chuas = relationship('ChiTietSuaChua', backref='phieu_sua_chua', lazy=True, cascade='all, delete-orphan')
    nhan_vien_sua_chua = relationship('NhanVienBase',backref='phieu_sua_chua', lazy=True)

class ChiTietSuaChua(db.Model): # inject phieu_tiep_nhan
    __tablename__ = 'chi_tiet_sua_chua'
    id = Column(Integer, primary_key=True, autoincrement=True)
    psc_id = Column(Integer, ForeignKey(PhieuSuaChua.id), nullable=False)
    linh_kien_id = Column(Integer, ForeignKey(LinhKien.id), nullable=False)
    so_luong = Column(Integer, nullable=False, default=1)
    don_gia = Column(Float, nullable=False)
    linh_kien = relationship('LinhKien', backref='chi_tiet_sua_chuas', lazy=True)

if __name__ == "__main__":
    with app.app_context():
        # db.drop_all()
        db.create_all()
        l1 = Loi(ten_loi="Loi dong co")
        l2 = Loi(ten_loi="Loi phanh")
        l3 = Loi(ten_loi="Loi den xe")
        l4 = Loi(ten_loi="Loi hop so")
        l5 = Loi(ten_loi="Loi dieu hoa")
        l6 = Loi(ten_loi="Loi lop xe")
        l7 = Loi(ten_loi="Loi binh xang")
        l8 = Loi(ten_loi="Loi guong chieu hau")
        l9 = Loi(ten_loi="Loi canh bao")
        l10 = Loi(ten_loi="Loi he thong giai tri")
        db.session.add_all([l1, l2, l3, l4, l5, l6, l7, l8, l9, l10])
        db.session.commit()


        ql = NhanVienBase(
            name="Pham Minh Hao",
            role=RoleEnum.QUANLY,
            ngay_sinh=date(2005, 8, 5),
            sdt="0909123456",
            email="minhhao@gmail.com",
            username="minhhao",
            password=hashlib.md5("123456".encode("utf-8")).hexdigest(),
        )

        tn = NhanVienBase(
            name="Tran Duc Phu",
            role=RoleEnum.TIEPNHAN,
            ngay_sinh=date(2005, 8, 5),
            sdt="0909123456",
            email="ducphu@gmail.com",
            username="ducphu",
            password=hashlib.md5("123456".encode("utf-8")).hexdigest(),
        )

        sc = NhanVienBase(
            name="Tan Phuc",
            role=RoleEnum.SUACHUA,
            ngay_sinh=date(2005, 8, 5),
            sdt="0909123456",
            email="tanphuc@gmail.com",
            username="tanphuc",
            password=hashlib.md5("123456".encode("utf-8")).hexdigest(),
        )

        tg = NhanVienBase(
            name="Tran Quoc Huy",
            role=RoleEnum.THUNGAN,
            ngay_sinh=date(2005, 8, 5),
            sdt="0909123456",
            email="quochuy@gmail.com",
            username="quochuy",
            password=hashlib.md5("123456".encode("utf-8")).hexdigest(),
        )

        db.session.add_all([ql, tn, sc, tg])
        db.session.commit()

        qd1 = QuyDinh(ten_quy_dinh="Số xe nhận", noi_dung="300", quanly_id=ql.id)
        qd2 = QuyDinh(ten_quy_dinh="Thuế VAT", noi_dung="0.1", quanly_id=ql.id)
        db.session.add_all([qd1, qd2])

        hm_list = [
            ("Bugi", "Bugi xe máy, ô tô",ql.id),
            ("Nhớt", "Dầu nhớt động cơ",ql.id),
            ("Lọc gió", "Lọc gió xe",ql.id),
            ("Ắc quy", "Ắc quy xe máy, ô tô",ql.id),
            ("Phanh", "Má phanh, đĩa phanh",ql.id),
            ("Dầu thắng", "Dầu phanh",ql.id),
            ("Dầu hộp số", "Dầu hộp số tự động / số sàn",ql.id),
            ("Lốp xe", "Lốp xe máy, ô tô",ql.id),
            ("Dây curoa / xích", "Dây curoa, xích truyền động",ql.id),
            ("Bugi đánh lửa", "Bugi Iridium, Platinum",ql.id),
            ("Giảm xóc", "Phuộc trước/sau",ql.id),
            ("Đèn", "Đèn pha, đèn xi-nhan, đèn hậu",ql.id),
            ("Bugi ô tô", "Bugi động cơ ô tô",ql.id),
            ("Lọc nhớt", "Lọc dầu nhớt",ql.id),
            ("Phụ tùng khác", "Các linh kiện nhỏ khác",ql.id),
        ]

        hangmuc_objects = []
        for ten, mota, ql_id in hm_list:
            hm = HangMuc(ten_hang_muc=ten, mo_ta=mota,quanly_id=ql.id)
            hangmuc_objects.append(hm)
            db.session.add(hm)

        db.session.commit()

        linh_kien_list = [
            ("Bugi Denso", 200000, 50000, "Bugi"),
            ("Bugi Iridium", 250000, 45000, "Bugi"),
            ("Bugi NGK", 180000, 40000, "Bugi"),
            ("Bugi Bosch", 220000, 50000, "Bugi"),
            ("Bugi Platinum", 260000, 55000, "Bugi"),

            ("Nhớt Castrol", 120000, 20000, "Nhớt"),
            ("Nhớt Motul 7100", 180000, 25000, "Nhớt"),
            ("Nhớt Total", 150000, 22000, "Nhớt"),
            ("Nhớt Shell", 160000, 23000, "Nhớt"),
            ("Nhớt Liqui Moly", 200000, 30000, "Nhớt"),

            ("Lọc gió K&N", 150000, 30000, "Lọc gió"),
            ("Lọc gió Yamaha", 120000, 20000, "Lọc gió"),
            ("Lọc gió Honda", 130000, 22000, "Lọc gió"),
            ("Lọc gió Air Blade", 110000, 18000, "Lọc gió"),
            ("Lọc gió ô tô", 250000, 40000, "Lọc gió"),

            ("Ắc quy GS 12V", 850000, 70000, "Ắc quy"),
            ("Ắc quy Đồng Nai 12V", 780000, 65000, "Ắc quy"),
            ("Ắc quy Vision", 720000, 60000, "Ắc quy"),
            ("Ắc quy ô tô Exide", 1500000, 120000, "Ắc quy"),
            ("Ắc quy ô tô Amaron", 1700000, 130000, "Ắc quy"),

            ("Má phanh trước Yamaha", 320000, 40000, "Phanh"),
            ("Má phanh sau Honda", 280000, 35000, "Phanh"),
            ("Đĩa phanh ô tô", 1200000, 150000, "Phanh"),
            ("Bộ phanh ABS", 2500000, 200000, "Phanh"),
            ("Má phanh Suzuki", 300000, 38000, "Phanh"),

            ("Dầu thắng Castrol", 90000, 15000, "Dầu thắng"),
            ("Dầu thắng Motul", 100000, 18000, "Dầu thắng"),
            ("Dầu thắng Total", 95000, 16000, "Dầu thắng"),
            ("Dầu thắng DOT4", 85000, 15000, "Dầu thắng"),
            ("Dầu thắng DOT3", 80000, 12000, "Dầu thắng"),

            ("Dầu hộp số Castrol", 200000, 30000, "Dầu hộp số"),
            ("Dầu hộp số Motul", 220000, 35000, "Dầu hộp số"),
            ("Dầu hộp số Shell", 210000, 32000, "Dầu hộp số"),
            ("Dầu hộp số ô tô", 250000, 40000, "Dầu hộp số"),
            ("Dầu hộp số Liqui Moly", 270000, 45000, "Dầu hộp số"),

            ("Lốp Michelin", 1200000, 100000, "Lốp xe"),
            ("Lốp Bridgestone", 1100000, 95000, "Lốp xe"),
            ("Lốp Dunlop", 1000000, 90000, "Lốp xe"),
            ("Lốp xe máy Michelin", 400000, 35000, "Lốp xe"),
            ("Lốp xe máy Pirelli", 380000, 30000, "Lốp xe"),

            ("Dây curoa Vision", 50000, 10000, "Dây curoa / xích"),
            ("Dây curoa Air Blade", 55000, 12000, "Dây curoa / xích"),
            ("Xích xe máy", 80000, 15000, "Dây curoa / xích"),
            ("Dây curoa ô tô", 150000, 25000, "Dây curoa / xích"),
            ("Xích ô tô", 200000, 30000, "Dây curoa / xích"),

            ("Phuộc trước Yamaha", 600000, 50000, "Giảm xóc"),
            ("Phuộc sau Honda", 550000, 45000, "Giảm xóc"),
            ("Phuộc trước ô tô", 1500000, 120000, "Giảm xóc"),
            ("Phuộc sau ô tô", 1400000, 110000, "Giảm xóc"),
            ("Giảm xóc Universal", 700000, 60000, "Giảm xóc"),

            ("Đèn pha xe máy", 250000, 30000, "Đèn"),
            ("Đèn hậu xe máy", 150000, 20000, "Đèn"),
            ("Đèn xi-nhan", 100000, 15000, "Đèn"),
            ("Đèn pha ô tô", 1200000, 100000, "Đèn"),
            ("Đèn hậu ô tô", 800000, 70000, "Đèn"),

            ("Lọc nhớt Yamaha", 120000, 15000, "Lọc nhớt"),
            ("Lọc nhớt Honda", 110000, 12000, "Lọc nhớt"),
            ("Lọc nhớt ô tô", 250000, 30000, "Lọc nhớt"),
            ("Lọc nhớt Castrol", 130000, 18000, "Lọc nhớt"),
            ("Lọc nhớt Motul", 150000, 20000, "Lọc nhớt"),

            ("Gương chiếu hậu", 180000, 20000, "Phụ tùng khác"),
            ("Còi xe", 90000, 15000, "Phụ tùng khác"),
            ("Tay lái", 250000, 30000, "Phụ tùng khác"),
            ("Chân chống", 80000, 12000, "Phụ tùng khác"),
            ("Bảo vệ sên", 50000, 10000, "Phụ tùng khác"),
            ("Nắp bình xăng", 60000, 12000, "Phụ tùng khác"),
            ("Bộ dây điện", 100000, 20000, "Phụ tùng khác"),
            ("Khóa cổ xe máy", 40000, 8000, "Phụ tùng khác"),
        ]

        hm_dict = {hm.ten_hang_muc: hm.id for hm in hangmuc_objects}

        for ten, gia, tc, hm_name in linh_kien_list:
            lk = LinhKien(
                ten_linh_kien=ten,
                gia=gia,
                tien_cong=tc,
                quanly_id=ql.id,
                hangmuc_id=hm_dict[hm_name]
            )
            db.session.add(lk)

        db.session.commit()

        khach_hang_list = [
            ("Nguyen Van A", "0909000001"),
            ("Tran Thi B", "0909000002"),
            ("Le Van C", "0909000003"),
            ("Pham Thi D", "0909000004"),
            ("Hoang Van E", "0909000005"),
            ("Nguyen Van F", "0909000006"),
            ("Tran Thi G", "0909000007"),
            ("Le Van H", "0909000008"),
            ("Pham Thi I", "0909000009"),
            ("Hoang Van K", "0909000010"),
        ]

        kh_objects = []
        for name, sdt in khach_hang_list:
            kh = KhachHang(name=name, sdt=sdt)
            db.session.add(kh)
            kh_objects.append(kh)
        db.session.commit()

        xe_objects = []
        loai_xe_list = [LoaiXe.XE_MAY, LoaiXe.O_TO, LoaiXe.SUV, LoaiXe.Sedan, LoaiXe.XE_TAI]
        for i, kh in enumerate(kh_objects):
            xe = Xe(
                bien_so=f"30{i}A-1234{i}",
                loai_xe=loai_xe_list[i % len(loai_xe_list)],
                khachhang_id=kh.id
            )
            db.session.add(xe)
            xe_objects.append(xe)
        db.session.commit()

        ptn_list = []
        descriptions = [
            "Kiểm tra tổng thể", "Bảo dưỡng định kỳ", "Sửa phanh", "Thay dầu nhớt",
            "Kiểm tra điện", "Sửa máy lạnh", "Sửa đèn pha", "Sửa còi",
            "Thay xi nhan", "Kiểm tra gương chiếu hậu"
        ]
        for i in range(10):
            ptn = PhieuTiepNhan(
                nvtn_id=tn.id,
                xe_id=xe_objects[i].id,
                ngay_tiep_nhan=date(2025, 11, 20 + i),
                description=descriptions[i]
            )
            db.session.add(ptn)
            ptn_list.append(ptn)
        db.session.commit()

        loi_list = db.session.query(Loi).all()
        for i, ptn in enumerate(ptn_list):
            ptn.lois.append(loi_list[i % len(loi_list)])
            if i % 2 == 0:
                ptn.lois.append(loi_list[(i + 1) % len(loi_list)])
        db.session.commit()

        psc_list = []
        for i, ptn in enumerate(ptn_list):
            psc = PhieuSuaChua(
                ptn_id=ptn.id,
                nvsc_id=sc.id,
                ngay_sua_chua=date(2025, 11, 21 + i),
                tong_tien=100000 * (i + 1),
                da_xac_nhan = True if i % 3 == 0 else False
            )
            db.session.add(psc)
            psc_list.append(psc)
        db.session.commit()

        linh_kien_all = db.session.query(LinhKien).all()
        for i, psc in enumerate(psc_list):

            for j in range(2):
                ct = ChiTietSuaChua(
                    psc_id=psc.id,
                    linh_kien_id=linh_kien_all[(i + j) % len(linh_kien_all)].id,
                    so_luong=1 + j,
                    don_gia=linh_kien_all[(i + j) % len(linh_kien_all)].gia
                )
                db.session.add(ct)
        db.session.commit()





