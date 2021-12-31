import hashlib
from manageApp import db
from manageApp.models import *
from sqlalchemy import extract


# Thêm tài khoản
def add_user(name, email, username, password, avatar):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    u = User(name=name, email=email, username=username, password=password, avatar=avatar)
    try:
        db.session.add(u)
        db.session.commit()

        return True
    except Exception as ex:
        print(ex)
        return False


# Tính tổng giỏ hàng
def cart_stats(cart):
    if cart is None:
        return 0, 0

    books = cart.values()

    quantity = sum([b['quantity'] for b in books])
    total = sum([b['price'] * b['quantity'] for b in books])

    return quantity, total


def delete_cart(cart, book_id, t_quantity, t_price):
    count, price = t_quantity, t_price
    for idx, b in enumerate(cart.values()):
        if b["id"] == int(book_id):
            count = count - b["quantity"]
            price = price - b["quantity"] * b["price"]
            del cart[idx]
            break

    return count, price


# Lưu hóa đơn
def add_invoice(cart):
    total = 0
    if cart:
        try:
            for b in list(cart.values()):
                total = total + float(b["subTotal"])
            invoice = Invoice(customer_id=1, total=total, paid=total)
            db.session.add(invoice)
            db.session.commit()

            for b in list(cart.values()):
                detail = DetailInvoice(invoice_id=invoice.id,
                                       book_id=int(b["id"]),
                                       quantity=b["quantity"],
                                       price=float(b["price"]))
                db.session.add(detail)

            db.session.commit()

            return True
        except:
            pass

    return False


# Lưu thông tin khách hàng
def add_customer(c):
    try:
        db.session.add(c)
        db.session.commit()

        return True
    except Exception as ex:
        print(ex)
        return False

    return False


def report_revenue(month):
    tong = 0
    invoices = Invoice.query.filter(extract('month', Invoice.date_of_invoice) == int(month)).all()
    for i in invoices:
        tong = tong + i.total

    return tong
