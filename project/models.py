from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

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



