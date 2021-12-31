from sqlalchemy import Column, Integer, Float, String, ForeignKey, Boolean, Date, Enum, DateTime
from sqlalchemy.orm import relationship, backref
from flask_login import UserMixin
from datetime import datetime
from enum import Enum as UserEnum
from manageApp import db


class SaleBase(db.Model):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)

    def __str__(self):
        return self.name


# Bảng sách
class Book(SaleBase):
    __tablename__ = 'book'

    name = Column(String(50), nullable=False)
    description = Column(String(255))
    image = Column(String(255))
    price = Column(Float, default=0)
    categories = relationship('Category', secondary='book_cate', lazy='subquery', backref=backref('books', lazy=True))
    authors = relationship('Author', secondary='book_author', lazy='subquery', backref=backref('books', lazy=True))
    images = relationship('Bookimage', backref=backref('books', lazy=True))

    invoices = relationship('Invoice', secondary='detail_invoice', lazy='subquery', backref=backref('books', lazy=True))
    inventory_reports = relationship('InventoryReport', secondary='detail_inventory_report', lazy='subquery',
                                     backref=backref('books', lazy=True))
    received_notes = relationship('ReceivedNote', secondary='detail_received_note', lazy='subquery',
                                  backref=backref('books', lazy=True))


class Bookimage(db.Model):
    __tablename__ = 'book_image'

    id = Column(Integer, primary_key=True, autoincrement=True)
    image = Column(String(255), nullable=False)
    book_id = Column(Integer, ForeignKey(Book.id), nullable=False)


# Bảng thể loại
class Category(SaleBase):
    __tablename__ = 'category'

    name = Column(String(50), nullable=False)


# Bảng tác giả
class Author(SaleBase):
    __tablename__ = 'author'

    name = Column(String(50), nullable=False)
    image = Column(String(255))


# Bảng hóa đơn
class Invoice(db.Model):
    __tablename__ = 'invoice'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date_of_invoice = Column(Date, default=datetime.now())
    total = Column(Float, default=0)
    paid = Column(Float, default=0)
    customer_id = Column(Integer, ForeignKey('customer.id'))
    user_id = Column(Integer, ForeignKey('user.id'))

    def __str__(self):
        return "Mã háo dơn %s, ngày tạo %s" % (str(self.id), str(self.date_of_invoice))


# Bảng phiếu thu tiền
class DebtCollectionNote(SaleBase):
    __tablename__ = 'debt_collection_note'

    customer_id = Column(Integer, ForeignKey('customer.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    collection_date = Column(Date, default=datetime.now())
    proceeds = Column(Float, default=0)


# Bảng phiếu nhập sách
class ReceivedNote(db.Model):
    __tablename__ = 'received_note'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date_received = Column(Date, default=datetime.now())
    user_id = Column(Integer, ForeignKey('user.id'))
    detail_received_notes = relationship('DetailReceivedNote', backref=backref('received_note', lazy=True))

    def __str__(self):
        return "Mã phiếu nhập sách %s, ngày tạo %s" % (str(self.id), str(self.date_received))


# Bảng báo cáo tồn
class InventoryReport(db.Model):
    __tablename__ = 'inventory_report'

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_date = Column(Date, default=datetime.now())
    detail_inventory_reports = relationship('DetailInventoryReport', backref=backref('inventory_report', lazy=True))

    def __str__(self):
        return "Mã báo cáo tồn kho %s, ngày tạo %s" % (str(self.id), str(self.report_date))


# Bảng báo cáo công nợ
class DeptReport(db.Model):
    __tablename__ = 'dept_report'

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_date = Column(Date, default=datetime.now())

    def __str__(self):
        return "Mã báo cáo công nợ số %s, ngày tạo %s" % (str(self.id), str(self.report_date))


# Bảng sách-thể loại
class BookCate(db.Model):
    __tablename__ = 'book_cate'

    book_id = Column(Integer, ForeignKey('book.id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('category.id'), primary_key=True)


# Bảng sách-tác giả
class BookAuthor(db.Model):
    __tablename__ = 'book_author'

    book_id = Column(Integer, ForeignKey('book.id'), primary_key=True)
    author_id = Column(Integer, ForeignKey('author.id'), primary_key=True)


# Bảng chi tiết hóa đơn
class DetailInvoice(db.Model):
    __tablename__ = 'detail_invoice'

    invoice_id = Column(Integer, ForeignKey('invoice.id'), primary_key=True)
    book_id = Column(Integer, ForeignKey('book.id'), primary_key=True)
    quantity = Column(Integer, default=0)
    price = Column(Float, default=0)
    books = relationship('Book', backref=backref('detail_invoice', lazy=True))
    invoices = relationship('Invoice', backref=backref('detail_invoice', lazy=True))

    def __str__(self):
        return "%s x %s" % (str(self.books), str(self.quantity))


# Bảng chi tiết phiếu nhập sách
class DetailReceivedNote(db.Model):
    __tablename__ = 'detail_received_note'

    note_id = Column(Integer, ForeignKey('received_note.id'), primary_key=True)
    book_id = Column(Integer, ForeignKey('book.id'), primary_key=True)
    quantity = Column(Integer, default=0)
    books = relationship('Book', backref=backref('detail_received_note', lazy=True))
    received_notes = relationship('ReceivedNote', backref=backref('detail_received_note', lazy=True))

    def __str__(self):
        return "%s x %s" % (str(self.books), str(self.quantity))


# Bảng chi tiết báo cáo tồn
class DetailInventoryReport(db.Model):
    __tablename__ = 'detail_inventory_report'

    report_id = Column(Integer, ForeignKey('inventory_report.id'), primary_key=True)
    book_id = Column(Integer, ForeignKey('book.id'), primary_key=True)
    quantity_before = Column(Integer, default=0)
    quantity_after = Column(Integer, default=0)
    arise = Column(String(255))
    books = relationship('Book', backref=backref('detail_inventory_report', lazy=True))


# Bảng chi tiết báo cáo công nợ
class DetailDeptReport(db.Model):
    __tablename__ = 'detail_dept_report'

    report_id = Column(Integer, ForeignKey('dept_report.id'), primary_key=True)
    customer_id = Column(Integer, ForeignKey('customer.id'), primary_key=True)
    money_before = Column(Float, default=0)
    money_after = Column(Float, default=0)
    arise = Column(String(255))

    def __str__(self):
        return self.name


class UserRole(UserEnum):
    USER = 1
    ADMIN = 2


# Bảng user
class User(SaleBase, UserMixin):
    __tablename__ = 'user'

    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=True)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    avatar = Column(String(100))
    active = Column(Boolean, default=True)
    joined_date = Column(Date, default=datetime.now())
    user_role = Column(Enum(UserRole), default=UserRole.USER)


# Bảng khách hàng
class Customer(SaleBase):
    __tablename__ = 'customer'

    name = Column(String(50), nullable=False)
    address = Column(String(255))
    phone = Column(String(20), nullable=True)
    email = Column(String(50), nullable=True)
    debt = Column(Float, default=0)
    deptReports = relationship('DeptReport', secondary='detail_dept_report', lazy='subquery',
                               backref=backref('customers', lazy=True))
    invoices = relationship('Invoice', backref='customer', lazy=True)

    def __str__(self):
        return self.name


if __name__ == '__main__':
    db.create_all()
