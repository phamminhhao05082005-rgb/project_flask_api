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
    __mapper_args__ = {'polymorphic_identity': RoleEnum.TIEPNHAN.value}


class NhanVienSuaChua(NhanVienBase):
    __tablename__ = 'nhan_vien_sua_chua'
    id = Column(Integer, ForeignKey('nhan_vien_base.id'), primary_key=True)
    ca_lam = Column(String(50))
    __mapper_args__ = {'polymorphic_identity': RoleEnum.SUACHUA.value}


class ThuNgan(NhanVienBase):
    __tablename__ = 'thu_ngan'
    id = Column(Integer, ForeignKey('nhan_vien_base.id'), primary_key=True)
    ca_lam = Column(String(50))
    __mapper_args__ = {'polymorphic_identity': RoleEnum.THUNGAN.value}


class QuanLy(NhanVienBase):
    __tablename__ = 'quan_ly'
    id = Column(Integer, ForeignKey('nhan_vien_base.id'), primary_key=True)
    quy_dinhs = relationship('QuyDinh', backref='quanly', lazy=True)
    linh_kiens = relationship('LinhKien', backref='quanly', lazy=True)
    __mapper_args__ = {'polymorphic_identity': RoleEnum.QUANLY.value}


class QuyDinh(BaseModel):
    ten_quy_dinh = Column(String(50), nullable=False)
    noi_dung = Column(String(100), nullable=False)
    quanly_id = Column(Integer, ForeignKey(QuanLy.id), nullable=False)


class HangMuc(BaseModel):
    ten_hang_muc = Column(String(100), nullable=False)
    mo_ta = Column(String(255), nullable=True)
    linh_kiens = relationship('LinhKien', backref='hangmuc', lazy=True)


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

        hm1 = HangMuc(ten_hang_muc="Bugi", don_gia=200000)
        hm2 = HangMuc(ten_hang_muc="Nhớt", don_gia=150000)
        hm3 = HangMuc(ten_hang_muc="Lọc gió", don_gia=120000)
        hm4 = HangMuc(ten_hang_muc="Ắc quy", don_gia=800000)
        hm5 = HangMuc(ten_hang_muc="Phanh", don_gia=300000)
        db.session.add_all([hm1, hm2, hm3, hm4, hm5])
        db.session.commit()

        lk1 = LinhKien(ten_linh_kien="Bugi Denso", gia=200000, quanly_id=ql.id, hangmuc_id=hm1.id)
        lk2 = LinhKien(ten_linh_kien="Nhớt Castrol", gia=120000, quanly_id=ql.id, hangmuc_id=hm2.id)
        lk3 = LinhKien(ten_linh_kien="Nhớt Motul 7100", gia=180000, quanly_id=ql.id, hangmuc_id=hm2.id)
        lk4 = LinhKien(ten_linh_kien="Lọc gió K&N", gia=150000, quanly_id=ql.id, hangmuc_id=hm3.id)
        lk5 = LinhKien(ten_linh_kien="Ắc quy GS 12V", gia=850000, quanly_id=ql.id, hangmuc_id=hm4.id)
        lk6 = LinhKien(ten_linh_kien="Ắc quy Đồng Nai 12V", gia=780000, quanly_id=ql.id, hangmuc_id=hm4.id)
        lk7 = LinhKien(ten_linh_kien="Má phanh trước Yamaha", gia=320000, quanly_id=ql.id, hangmuc_id=hm5.id)
        lk8 = LinhKien(ten_linh_kien="Má phanh sau Honda", gia=280000, quanly_id=ql.id, hangmuc_id=hm5.id)
        lk9 = LinhKien(ten_linh_kien="Dây curoa", gia=50000, quanly_id=ql.id, hangmuc_id=hm1.id)
        lk10 = LinhKien(ten_linh_kien="Bugi Iridium", gia=250000, quanly_id=ql.id, hangmuc_id=hm1.id)
        lk11 = LinhKien(ten_linh_kien="Nhớt Motul 5100", gia=160000, quanly_id=ql.id, hangmuc_id=hm2.id)

        db.session.add_all([lk1, lk2, lk3, lk4, lk5, lk6, lk7, lk8, lk9, lk10, lk11])
        db.session.commit()
