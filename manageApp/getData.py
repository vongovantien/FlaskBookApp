from manageApp import db
from manageApp.models import *


def load_cate():
    return Category.query.all()


def load_author():
    return Author.query.all()


def load_all_book(lm=None):
    books = Book.query
    if lm:
        books = books.limit(lm)
    return books.all()


def get_author_of_book(book_id):
    authors = Author.query.join(BookAuthor, Author.id == BookAuthor.author_id) \
        .filter(BookAuthor.book_id == book_id)
    return authors.all()


def get_detail_book(book_id):
    return Book.query.get(book_id)


def load_image(cat, book_id=None):
    image = Bookimage.query.filter(Bookimage.image.contains(cat))
    if book_id:
        image = Bookimage.query.join(Book, Book.id == Bookimage.book_id) \
            .filter(Bookimage.image.contains(cat), Bookimage.book_id == book_id)
    return image.all()


def load_books():
    books = db.session.query(Book.id, Book.name, Book.description, Book.image, Book.price, Author.name.label('author'),
                             Category.name.label('cate')) \
        .join(BookAuthor, BookAuthor.book_id == Book.id) \
        .join(Author, Author.id == BookAuthor.author_id) \
        .join(BookCate, BookCate.book_id == Book.id) \
        .join(Category, Category.id == BookCate.category_id)

    return books.all()


def filter_book(cate_id=None, author_id=None, min_price=None, max_price=None, kw=None):
    books = Book.query

    if kw:
        books = books.filter(Book.name.contains(kw))

    if cate_id:
        books = books.join(BookCate, Book.id == BookCate.book_id) \
            .filter(BookCate.category_id == cate_id)

    if author_id:
        books = books.join(BookAuthor, Book.id == BookAuthor.book_id) \
            .filter(BookAuthor.author_id == author_id)

    if min_price and max_price:
        books = books.filter(Book.price.__gt__(min_price), Book.price.__lt__(max_price))

    return books.all()


def get_data_report():
    data = db.session.query(Book.name.label('book_name'),
                            Book.price.label('price'),
                            DetailInventoryReport.quantity_before.label('quantity_before'),
                            DetailInventoryReport.quantity_after.label('quantity_after'),
                            InventoryReport.report_date.label('report_date')) \
        .join(Book, Book.id == DetailInventoryReport.book_id) \
        .join(InventoryReport, DetailInventoryReport.report_id == InventoryReport.id)
    return data.all()
