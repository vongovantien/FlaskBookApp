from flask import render_template, request, session, jsonify, redirect, url_for
from flask_login import login_user, current_user, logout_user
from manageApp import app, login, utils, getData, db
from manageApp.models import *
from manageApp.admins import *
import hashlib
import os


class MyView(BaseView):
    def __init__(self, *args, **kwargs):
        self._default_view = True
        super(MyView, self).__init__(*args, **kwargs)
        self.admin = admin


@app.route("/admin-login", methods=["post", "get"])
def login_usr():
    err_msg = ''
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password", "")
        password = str(hashlib.md5(password.strip().encode("utf-8")).hexdigest())
        user = User.query.filter(User.username == username.strip(), User.password == password).first()

        if user:
            login_user(user=user)
            if user.user_role == UserRole.USER:
                return redirect(url_for("index"))
            else:
                return redirect("/admin")
        else:
            err_msg = "Sai mật khẩu hoặc tên tài khoản!"

    return render_template('admin/login.html', err_msg=err_msg)


@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/logout')
def logout_usr():
    logout_user()
    return redirect(url_for('index'))


@app.route("/register", methods=["post", "get"])
def register():
    err_msg = ''
    if request.method == 'POST':
        name = request.form.get('name_dk')
        email = request.form.get('email_dk')
        username = request.form.get('username_dk')
        password = request.form.get('password_dk', '').strip()
        confirm_password = request.form.get('password-repeat', '').strip()

        if password == confirm_password:
            avatar = request.files["avatar"]
            avatar_path = 'images/upload/%s' % avatar.filename
            avatar.save(os.path.join(app.config['ROOT_PROJECT_PATH'],
                                     'static/', avatar_path))

            if utils.add_user(name=name, email=email, username=username,
                              password=password, avatar=avatar_path):
                return redirect('/admin')
        else:
            err_msg = "Mật khẩu KHÔNG khớp!"

    return render_template('admin/register.html', err_msg=err_msg)


@app.route("/register-form", methods=["post", "get"])
def register_form():
    return render_template("admin/register.html")


@app.route("/my-account", methods=["get", "post"])
def my_account():
    quan, price = utils.cart_stats(session.get('cart'))
    cart_info = {
        'total_quantity': quan,
        'total_amount': price
    }
    return render_template("my-account.html", cart_info=cart_info)


# Trang chủ
@app.route("/")
def index():
    categories = getData.load_cate()
    books = Book.query.all()
    booklm = Book.query.limit(10).all()
    book_list = getData.load_books()
    authors = Author.query.limit(8).all()

    quan, price = utils.cart_stats(session.get('cart'))
    cart_info = {
        'total_quantity': quan,
        'total_amount': price
    }
    return render_template('index.html', categories=categories,
                           booklm=booklm,
                           books=books,
                           authors=authors,
                           book_list=book_list, cart_info=cart_info)


# Tất cả sản phẩm
@app.route("/shop-list/<int:page_num>")
def shop_list(page_num):
    categories = getData.load_cate()
    author_list = getData.load_author()
    books = Book.query.all()
    book_list = getData.load_books()
    book_pagi = Book.query.paginate(per_page=12, page=page_num, error_out=True)
    all_pages = book_pagi.iter_pages()
    quan, price = utils.cart_stats(session.get('cart'))
    cart_info = {
        'total_quantity': quan,
        'total_amount': price
    }

    return render_template('shop_list.html', book_pagi=book_pagi, book_list=book_list, books=books,
                           categories=categories,
                           author_list=author_list,
                           cart_info=cart_info,
                           all_pages=all_pages)


# Lọc theo thể loại và tác giả
@app.route("/shop-list")
def shop_filter():
    categories = getData.load_cate()
    author_list = getData.load_author()
    book_list = getData.load_books()
    kw = request.args.get("kw")
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")
    cate_id = request.args.get("category_id")
    author_id = request.args.get("author_id")
    books = getData.filter_book(cate_id=cate_id, author_id=author_id, min_price=min_price, max_price=max_price, kw=kw)
    quan, price = utils.cart_stats(session.get('cart'))
    cart_info = {
        'total_quantity': quan,
        'total_amount': price
    }

    return render_template('shop_list.html', books=books, book_list=book_list, kw=kw,
                           min_price=min_price,
                           cate_id=cate_id,
                           author_id=author_id,
                           categories=categories,
                           author_list=author_list,
                           cart_info=cart_info)


# Thông tin sách
@app.route("/shop-list/book-detail/<int:book_id>")
def book_detail(book_id):
    book = getData.get_detail_book(book_id)
    books = Book.query.all()
    book_list = getData.load_books()
    authors = getData.get_author_of_book(book_id)
    images = getData.load_image('300x452', book_id=book_id)
    quan, price = utils.cart_stats(session.get('cart'))
    cart_info = {
        'total_quantity': quan,
        'total_amount': price
    }

    return render_template('book_detail.html', book=book, books=books, book_list=book_list,
                           authors=authors, images=images, cart_info=cart_info)


# Thêm sản phẩm vào giỏ hàng
@app.route('/api/cart', methods=['post'])
def add_to_cart():
    if 'cart' not in session:
        session['cart'] = {}

    data = request.json
    book_id = str(data.get('id'))
    book_name = data.get('name')
    image = data.get('image')
    price = data.get('price')

    cart = session['cart']

    if book_id in cart:  # co san pham trong gio
        quan = cart[book_id]['quantity']
        cart[book_id]['quantity'] = int(quan) + 1
        subp = cart[book_id]['subTotal']
        cart[book_id]['subTotal'] = float(subp) + price
    else:  # chua co san pham trong gio
        cart[book_id] = {
            "id": book_id,
            "name": book_name,
            "image": image,
            "price": price,
            "quantity": 1,
            "subTotal": price
        }

    session['cart'] = cart

    total_quan, total_amount = utils.cart_stats(session['cart'])

    return jsonify({
        "message": "Thêm giỏ hàng thành công",
        'total_amount': total_amount,
        'total_quantity': total_quan
    })


# Bớt một sản phẩm khỏi giỏ hàng
@app.route('/api/remove-item-cart', methods=['post'])
def remove_from_cart():
    data = request.json
    book_id = str(data.get('id'))
    book_name = data.get('name')
    image = data.get('image')
    price = data.get('price')

    cart = session['cart']
    if book_id in cart:  # co san pham trong gio
        quan = cart[book_id]['quantity']
        cart[book_id]['quantity'] = int(quan) - 1
        subp = cart[book_id]['subTotal']
        cart[book_id]['subTotal'] = float(subp) - price
    else:  # chua co san pham trong gio
        cart[book_id] = {
            "id": book_id,
            "name": book_name,
            "image": image,
            "price": price,
            "quantity": 1,
            "subTotal": price
        }

    session['cart'] = cart

    total_quan, total_amount = utils.cart_stats(session['cart'])
    cart_info = {
        'total_quantity': total_quan,
        'total_amount': total_amount
    }

    return jsonify({
        "message": "Cập nhật giỏ hàng thành công",
        'total_amount': total_amount,
        'total_quantity': total_quan
    })


# Trang giỏ hàng
@app.route("/shop-cart", methods=['get', 'post'])
def shop_cart():
    if request.method == 'POST':

        if utils.add_invoice(session.get('cart')):
            del session['cart']

            return jsonify({"message": "Đặt hàng thành công!!!"})

    quan, price = utils.cart_stats(session.get('cart'))
    cart_info = {
        'total_quantity': quan,
        'total_amount': price
    }
    return render_template('shop_cart.html', cart_info=cart_info)


@app.route("/checkout", methods=['get', 'post'])
def checkout():
    if request.method == 'POST':

        if utils.add_invoice(session.get('cart')):
            del session['cart']

            return jsonify({"message": "Đặt hàng thành công"})

    quan, price = utils.cart_stats(session.get('cart'))
    cart_info = {
        'total_quantity': quan,
        'total_amount': price
    }
    return render_template('checkout.html', cart_info=cart_info)


@app.route('/report')
def report():
    data = []
    for i in range(1, 13):
        data.append(utils.report_revenue(i))

    m = int(max(data))
    a = list(str(m))
    for i in range(0, len(a)):
        if i == 0:
            a[i] = str(int(a[i]) + 1)
        else:
            a[i] = '0'
    c = int(''.join(a))
    reports = getData.get_data_report()
    return MyView().render('admin/thongke.html', data=data, c=c, reports=reports)


if __name__ == "__main__":
    app.run(debug=True)
