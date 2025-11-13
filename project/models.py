from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from init import db, app
from flask_login import UserMixin
from enum import Enum as UserEnum
from datetime import date
import hashlib
class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


class RoleEnum(UserEnum):
    QUANLY = "quanly"
    TIEPNHAN = "tiepnhan"
    SUACHUA = "suachua"
    THUNGAN = "thungan"

class NhanVienBase(BaseModel, UserMixin):
    __tablename__ = 'nhan_vien_base'

    name = Column(String(50), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    ngay_sinh = Column(Date)
    sdt = Column(String(15))
    email = Column(String(100))
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(100), nullable=False)

    def __str__(self):
        return f"{self.name} ({self.role.value})"


class NhanVienTiepNhan(NhanVienBase):
    __tablename__ = 'nhan_vien_tiep_nhan'
    id = Column(Integer, ForeignKey('nhan_vien_base.id'), primary_key=True)
    ca_lam = Column(String(50))

class NhanVienSuaChua(NhanVienBase):
    __tablename__ = 'nhan_vien_sua_chua'
    id = Column(Integer, ForeignKey('nhan_vien_base.id'), primary_key=True)
    ca_lam = Column(String(50))

class ThuNgan(NhanVienBase):
    __tablename__ = 'thu_ngan'
    id = Column(Integer, ForeignKey('nhan_vien_base.id'), primary_key=True)
    ca_lam = Column(String(50))

class QuanLy(NhanVienBase):
    __tablename__ = 'quan_ly'
    id = Column(Integer, ForeignKey('nhan_vien_base.id'), primary_key=True)
    quy_dinhs = relationship('QuyDinh', backref='quanly', lazy=True)
    linh_kiens = relationship('LinhKien', backref='quanly', lazy=True)

class QuyDinh(BaseModel):
    ten_quy_dinh = Column(String(50), nullable=False)
    noi_dung = Column(String(100), nullable=False)
    quanly_id = Column(Integer, ForeignKey(QuanLy.id), nullable=False)


class HangMuc(BaseModel):
    ten_hang_muc = Column(String(100), nullable=False)
    mo_ta = Column(String(255), nullable=True)
    linh_kiens = relationship('LinhKien', backref='hangmuc',
                              lazy=True, cascade='all, delete-orphan')


class LinhKien(BaseModel):
    ten_linh_kien = Column(String(100), nullable=False)
    gia = Column(Float, nullable=False)
    tien_cong = Column(Float, nullable=True, default=0)
    quanly_id = Column(Integer, ForeignKey(QuanLy.id), nullable=False)
    hangmuc_id = Column(Integer, ForeignKey(HangMuc.id))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        ql = QuanLy(
            name='Pham Minh Hao',
            role='quanly',
            ngay_sinh=date(2005, 8, 5),
            sdt='0909123456',
            email='minhhao@gmail.com',
            username='minhhao',
            password=hashlib.md5("123456".encode('utf-8')).hexdigest()
        )

        tn = NhanVienTiepNhan(
            name='Tran Duc Phu',
            role='tiepnhan',
            ngay_sinh=date(2005, 8, 5),
            sdt='0909123456',
            ca_lam='Ca sáng',
            username='ducphu',
            password=hashlib.md5("123456".encode('utf-8')).hexdigest(),
            email='ducphu@gmail.com'
        )

        sc = NhanVienSuaChua(
            name='Tan Phuc',
            role='suachua',
            ngay_sinh=date(2005, 8, 5),
            sdt='0909123456',
            ca_lam='Ca chiều',
            username='tanphuc',
            password=hashlib.md5("123456".encode('utf-8')).hexdigest(),
            email='tanphuc@gmail.com'
        )

        tg = ThuNgan(
            name='Tran Quoc Huy',
            role='thungan',
            ngay_sinh=date(2005, 8, 5),
            sdt='0909123456',
            ca_lam='Ca sáng',
            username='quochuy',
            password=hashlib.md5("123456".encode('utf-8')).hexdigest(),
            email='quochuy@gmail.com'
        )

        db.session.add_all([ql, tn, sc, tg])
        db.session.commit()

        qd1 = QuyDinh(ten_quy_dinh="Số xe nhận", noi_dung="300", quanly_id=ql.id)
        qd2 = QuyDinh(ten_quy_dinh="Thuế VAT", noi_dung="0.1", quanly_id=ql.id)
        db.session.add_all([qd1, qd2])
        db.session.commit()


        hm1 = HangMuc(ten_hang_muc="Bugi", mo_ta="Bugi xe máy, ô tô")
        hm2 = HangMuc(ten_hang_muc="Nhớt", mo_ta="Dầu nhớt động cơ")
        hm3 = HangMuc(ten_hang_muc="Lọc gió", mo_ta="Lọc gió xe")
        hm4 = HangMuc(ten_hang_muc="Ắc quy", mo_ta="Ắc quy xe máy, ô tô")
        hm5 = HangMuc(ten_hang_muc="Phanh", mo_ta="Má phanh, đĩa phanh")
        hm6 = HangMuc(ten_hang_muc="Dầu thắng", mo_ta="Dầu phanh")
        hm7 = HangMuc(ten_hang_muc="Dầu hộp số", mo_ta="Dầu hộp số tự động / số sàn")
        hm8 = HangMuc(ten_hang_muc="Lốp xe", mo_ta="Lốp xe máy, ô tô")
        hm9 = HangMuc(ten_hang_muc="Dây curoa / xích", mo_ta="Dây curoa, xích truyền động")
        hm10 = HangMuc(ten_hang_muc="Bugi đánh lửa", mo_ta="Bugi Iridium, Platinum")
        hm11 = HangMuc(ten_hang_muc="Giảm xóc", mo_ta="Phuộc trước/sau")
        hm12 = HangMuc(ten_hang_muc="Đèn", mo_ta="Đèn pha, đèn xi-nhan, đèn hậu")
        hm13 = HangMuc(ten_hang_muc="Bugi ô tô", mo_ta="Bugi động cơ ô tô")
        hm14 = HangMuc(ten_hang_muc="Lọc nhớt", mo_ta="Lọc dầu nhớt")
        hm15 = HangMuc(ten_hang_muc="Phụ tùng khác", mo_ta="Các linh kiện nhỏ khác")

        db.session.add_all([hm1, hm2, hm3, hm4, hm5, hm6, hm7, hm8, hm9, hm10, hm11, hm12, hm13, hm14, hm15])
        db.session.commit()


        linh_kien_list = [

            ("Bugi Denso", 200000, 50000, hm1),
            ("Bugi Iridium", 250000, 45000, hm1),
            ("Bugi NGK", 180000, 40000, hm1),
            ("Bugi Bosch", 220000, 50000, hm1),
            ("Bugi Platinum", 260000, 55000, hm1),

            ("Nhớt Castrol", 120000, 20000, hm2),
            ("Nhớt Motul 7100", 180000, 25000, hm2),
            ("Nhớt Total", 150000, 22000, hm2),
            ("Nhớt Shell", 160000, 23000, hm2),
            ("Nhớt Liqui Moly", 200000, 30000, hm2),

            ("Lọc gió K&N", 150000, 30000, hm3),
            ("Lọc gió Yamaha", 120000, 20000, hm3),
            ("Lọc gió Honda", 130000, 22000, hm3),
            ("Lọc gió Air Blade", 110000, 18000, hm3),
            ("Lọc gió ô tô", 250000, 40000, hm3),

            ("Ắc quy GS 12V", 850000, 70000, hm4),
            ("Ắc quy Đồng Nai 12V", 780000, 65000, hm4),
            ("Ắc quy Vision", 720000, 60000, hm4),
            ("Ắc quy ô tô Exide", 1500000, 120000, hm4),
            ("Ắc quy ô tô Amaron", 1700000, 130000, hm4),

            ("Má phanh trước Yamaha", 320000, 40000, hm5),
            ("Má phanh sau Honda", 280000, 35000, hm5),
            ("Đĩa phanh ô tô", 1200000, 150000, hm5),
            ("Bộ phanh ABS", 2500000, 200000, hm5),
            ("Má phanh Suzuki", 300000, 38000, hm5),

            ("Dầu thắng Castrol", 90000, 15000, hm6),
            ("Dầu thắng Motul", 100000, 18000, hm6),
            ("Dầu thắng Total", 95000, 16000, hm6),
            ("Dầu thắng DOT4", 85000, 15000, hm6),
            ("Dầu thắng DOT3", 80000, 12000, hm6),

            ("Dầu hộp số Castrol", 200000, 30000, hm7),
            ("Dầu hộp số Motul", 220000, 35000, hm7),
            ("Dầu hộp số Shell", 210000, 32000, hm7),
            ("Dầu hộp số ô tô", 250000, 40000, hm7),
            ("Dầu hộp số Liqui Moly", 270000, 45000, hm7),

            ("Lốp Michelin", 1200000, 100000, hm8),
            ("Lốp Bridgestone", 1100000, 95000, hm8),
            ("Lốp Dunlop", 1000000, 90000, hm8),
            ("Lốp xe máy Michelin", 400000, 35000, hm8),
            ("Lốp xe máy Pirelli", 380000, 30000, hm8),

            ("Dây curoa Vision", 50000, 10000, hm9),
            ("Dây curoa Air Blade", 55000, 12000, hm9),
            ("Xích xe máy", 80000, 15000, hm9),
            ("Dây curoa ô tô", 150000, 25000, hm9),
            ("Xích ô tô", 200000, 30000, hm9),

            ("Phuộc trước Yamaha", 600000, 50000, hm11),
            ("Phuộc sau Honda", 550000, 45000, hm11),
            ("Phuộc trước ô tô", 1500000, 120000, hm11),
            ("Phuộc sau ô tô", 1400000, 110000, hm11),
            ("Giảm xóc Universal", 700000, 60000, hm11),

            ("Đèn pha xe máy", 250000, 30000, hm12),
            ("Đèn hậu xe máy", 150000, 20000, hm12),
            ("Đèn xi-nhan", 100000, 15000, hm12),
            ("Đèn pha ô tô", 1200000, 100000, hm12),
            ("Đèn hậu ô tô", 800000, 70000, hm12),

            ("Lọc nhớt Yamaha", 120000, 15000, hm14),
            ("Lọc nhớt Honda", 110000, 12000, hm14),
            ("Lọc nhớt ô tô", 250000, 30000, hm14),
            ("Lọc nhớt Castrol", 130000, 18000, hm14),
            ("Lọc nhớt Motul", 150000, 20000, hm14),

            ("Gương chiếu hậu", 180000, 20000, hm15),
            ("Còi xe", 90000, 15000, hm15),
            ("Tay lái", 250000, 30000, hm15),
            ("Chân chống", 80000, 12000, hm15),
            ("Bảo vệ sên", 50000, 10000, hm15),
            ("Nắp bình xăng", 60000, 12000, hm15),
            ("Bộ dây điện", 100000, 20000, hm15),
            ("Khóa cổ xe máy", 40000, 8000, hm15),
        ]

        for ten, gia, tien_cong, hm in linh_kien_list:
            lk = LinhKien(ten_linh_kien=ten, gia=gia, tien_cong=tien_cong, quanly_id=ql.id, hangmuc_id=hm.id)
            db.session.add(lk)

        db.session.commit()


