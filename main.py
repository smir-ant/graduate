from flask import Flask, render_template, redirect, url_for, flash, request, send_from_directory
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from forms import RegisterForm, LoginForm, NewItem, NewMaterialType, NewDepartment, NewTransferInvoice, \
    NewReceiveInvoice, NewSuppliers
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789'

Bootstrap(app)

# логин система
login_manager = LoginManager()
login_manager.init_app(app)

# подключение БД
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# ===================== БД =====================
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    """ Пользователи """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db. String(250), nullable=False, unique=True)
    password = db.Column(db. String(250), nullable=False)
    role = db.Column(db.String(250), nullable=False)


class TipiMatCen(db.Model):
    """ Типы материальных ценностей """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)


class Otdeli(db.Model):
    """ Отделы """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    phone_number = db.Column(db. String(250), nullable=False)


class UchetMatCen(db.Model):
    """ Учет материальных ценностей """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    type = db.Column(db. String(250), nullable=False)  # 1 из TipiMatCen(db.Model)
    locate_in = db.Column(db. String(250), nullable=False)  # 1 из Otdeli(db.Model)
    guarantee = db.Column(db. String(250), nullable=False)
    inventory_number = db.Column(db. String(250), nullable=False)
    work_from = db.Column(db. String(250), nullable=False)


class TransferInvoices(db.Model):
    """ Накладные на передачу """
    id = db.Column(db.Integer, primary_key=True)
    uchet_name = db.Column(db.Integer, nullable=False)  # id UchetMatCen
    from_field = db.Column(db.String(250), nullable=False)  # из Otdeli
    to_field = db.Column(db. String(250), nullable=False)  # из Otdeli
    in_connection_with = db.Column(db. String(250), nullable=False)
    responsible = db.Column(db. String(250), nullable=False)
    is_done = db.Column(db.Boolean)


class ReceiveInvoices(db.Model):
    """ Учет материальных ценностей """
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db. String(250), nullable=False)
    invoice_number = db.Column(db. String(250), nullable=False)
    suppliers_list = db.Column(db. String(250), nullable=False)  # список поставщиков
    receiver = db.Column(db. String(250), nullable=False)

    title = db.Column(db.String(250), nullable=False)
    type = db.Column(db. String(250), nullable=False)  # 1 из TipiMatCen(db.Model)
    locate_in = db.Column(db. String(250), nullable=False)  # 1 из Otdeli(db.Model)
    guarantee = db.Column(db. String(250), nullable=False)
    inventory_number = db.Column(db. String(250), nullable=False)
    work_from = db.Column(db. String(250), nullable=False)
    is_done = db.Column(db.Boolean)


class Suppliers(db.Model):
    """ Поставщики """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    phone_number = db.Column(db. String(250), nullable=False)
    site = db.Column(db. String(250), nullable=False)


class Standards(db.Model):
    """ Нормативы """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    type = db.Column(db.String(250), nullable=False)


db.create_all()
# ========================================


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ================================= INDEX =================================
@app.route('/')
def home():
    mat_cen = UchetMatCen.query.all()  # получаем все посты)
    return render_template("index.html", all_mat_cen=mat_cen)


@app.route("/index_delete/<int:item_id>")
def index_delete(item_id):
    item_to_delete = UchetMatCen.query.get(item_id)
    db.session.delete(item_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/index-new', methods=['GET', 'POST'])
def index_new():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    form = NewItem()
    tipi_mat_cen = TipiMatCen.query.all()
    otdeli = Otdeli.query.all()
    form.locate_in.choices = [g.title for g in otdeli]  # передаем список из таблицы бд с локациями
    form.type.choices = [g.title for g in tipi_mat_cen]  # передаем список из таблицы бд с типами МЦ
    if request.method == 'POST':
        if form.validate_on_submit():
            item_to_db = UchetMatCen(
                title=request.form.get('title'),
                type=request.form.get('type'),
                locate_in=request.form.get('locate_in'),
                guarantee=request.form.get('guarantee'),
                inventory_number=request.form.get('inventory_number'),
                work_from=request.form.get('work_from'),
            )
            # заносим запись в бд
            db.session.add(item_to_db)
            db.session.commit()
            return redirect(url_for('home'))
    return render_template("index_new.html", form=form)
# ===========================================================================


# ================================= ТИПЫ МЦ =================================
@app.route('/material-type')
def material_type():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    tipi_mat_cen = TipiMatCen.query.all()  # получаем все посты)
    return render_template("material_type.html", tipi_mat_cen=tipi_mat_cen)


@app.route("/material_type_delete/<int:item_id>")
def material_type_delete(item_id):
    item_to_delete = TipiMatCen.query.get(item_id)
    db.session.delete(item_to_delete)
    db.session.commit()
    return redirect(url_for('material_type'))


@app.route('/material-type-new', methods=['GET', 'POST'])
def material_type_new():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    form = NewMaterialType()
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.validate_on_submit():
                item_to_db = TipiMatCen(
                    title=request.form.get('title'),
                )
                # заносим запись в бд
                db.session.add(item_to_db)
                db.session.commit()
                return redirect(url_for('material_type'))
    return render_template("material_type_new.html", form=form)
# ==========================================================================


# ================================= ОТДЕЛЫ =================================
@app.route('/departments')
def departments():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    departments_list = Otdeli.query.all()  # получаем все посты)
    return render_template("departments.html", departments=departments_list)


@app.route("/departments_delete/<int:item_id>")
def departments_delete(item_id):
    item_to_delete = Otdeli.query.get(item_id)
    db.session.delete(item_to_delete)
    db.session.commit()
    return redirect(url_for('departments'))


@app.route('/departments-new', methods=['GET', 'POST'])
def departments_new():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    form = NewDepartment()
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.validate_on_submit():
                item_to_db = Otdeli(
                    title=request.form.get('title'),
                    phone_number=request.form.get('phone_number'),
                )
                # заносим запись в бд
                db.session.add(item_to_db)
                db.session.commit()
                return redirect(url_for('departments'))
    return render_template("departments_new.html", form=form)
# ==========================================================================


# ================================= ПОСТАВЩИКИ =================================
@app.route('/suppliers')
def suppliers():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    suppliers_query = Suppliers.query.all()
    return render_template("suppliers.html", suppliers=suppliers_query)


@app.route("/suppliers_delete/<int:item_id>")
def suppliers_delete(item_id):
    item_to_delete = Suppliers.query.get(item_id)
    db.session.delete(item_to_delete)
    db.session.commit()
    return redirect(url_for('suppliers'))


@app.route('/suppliers-new', methods=['GET', 'POST'])
def suppliers_new():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    form = NewSuppliers()
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.validate_on_submit():
                item_to_db = Suppliers(
                    title=request.form.get('title'),
                    phone_number=request.form.get('phone_number'),
                    site=request.form.get('site'),
                )
                # заносим запись в бд
                db.session.add(item_to_db)
                db.session.commit()
                return redirect(url_for('suppliers'))
    return render_template("suppliers_new.html", form=form)
# ==========================================================================


# ========================= НАКЛАДНЫЕ НА ПРИНЯТИЕ =========================
@app.route('/receive-invoices')
def receive_invoices():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    receive_invoice = ReceiveInvoices.query.all()
    return render_template("receive_invoices.html", receive_invoice=receive_invoice)


@app.route('/receive-invoices-new', methods=['GET', 'POST'])
def receive_invoices_new():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    form = NewReceiveInvoice()
    otdeli = Otdeli.query.all()
    tipi = TipiMatCen.query.all()
    postavshiki = Suppliers.query.all()
    form.type.choices = [g.title for g in tipi]  # передаем список из таблицы бд с типами МЦ
    form.suppliers_list.choices = [g.title for g in postavshiki]
    form.locate_in.choices = [g.title for g in otdeli]
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.validate_on_submit():
                item_to_db = UchetMatCen(
                    title=request.form.get('title'),
                    type=request.form.get('type'),
                    locate_in=request.form.get('locate_in'),
                    guarantee=request.form.get('guarantee'),
                    inventory_number=request.form.get('inventory_number'),
                    work_from=request.form.get('date'),
                )
                # заносим запись в бд
                db.session.add(item_to_db)
                db.session.commit()

                item_to_db = ReceiveInvoices(
                    date=request.form.get('date'),
                    invoice_number=request.form.get('invoice_number'),
                    suppliers_list=request.form.get('suppliers_list'),
                    receiver=request.form.get('receiver'),

                    title=request.form.get('title'),
                    type=request.form.get('type'),
                    locate_in=request.form.get('locate_in'),
                    guarantee=request.form.get('guarantee'),
                    inventory_number=request.form.get('inventory_number'),
                    work_from=request.form.get('date'),
                    is_done=False,
                )
                # заносим запись в бд
                db.session.add(item_to_db)
                db.session.commit()
                return redirect(url_for('receive_invoices'))
    return render_template("receive_invoices_new.html", form=form)


@app.route("/receive_invoices_delete/<int:item_id>")
def receive_invoices_delete(item_id):
    item_to_delete = ReceiveInvoices.query.get(item_id)
    db.session.delete(item_to_delete)
    db.session.commit()
    return redirect(url_for('transfer_invoices'))


@app.route("/receive_invoices_more/<int:item_id>")
def receive_invoices_more(item_id):
    item_to_see = ReceiveInvoices.query.get(item_id)
    return render_template("receive_invoices_more.html", receive_invoice_more=item_to_see)
# ==========================================================================


# ========================== НАКЛАДНЫЕ НА ПЕРЕДАЧУ ==========================
@app.route('/transfer-invoices')
def transfer_invoices():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    transfer_invoice = TransferInvoices.query.all()  # получаем все посты)
    return render_template("transfer_invoices.html", transfer_invoices=transfer_invoice)


@app.route('/transfer-invoices-new', methods=['GET', 'POST'])
def transfer_invoices_new():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    form = NewTransferInvoice()
    otdeli = Otdeli.query.all()
    tovari = UchetMatCen.query.all()
    form.from_field.choices = [g.title for g in otdeli]  # передаем список из таблицы бд с типами МЦ
    form.to_field.choices = [g.title for g in otdeli]
    form.uchet_field.choices = [g.title for g in tovari]
    if request.method == 'POST':
        if form.validate_on_submit():
            if form.validate_on_submit():
                item_to_db = TransferInvoices(
                    from_field=request.form.get('from_field'),
                    to_field=request.form.get('to_field'),
                    in_connection_with=request.form.get('in_connection_with'),
                    responsible=request.form.get('responsible'),
                    is_done=False,
                    uchet_name=request.form.get('uchet_field')
                )
                # заносим запись в бд
                db.session.add(item_to_db)
                db.session.commit()

                return redirect(url_for('transfer_invoices'))
    return render_template("transfer_invoices_new.html", form=form)


@app.route("/transfer_invoices_delete/<int:item_id>")
def transfer_invoices_delete(item_id):
    item_to_delete = TransferInvoices.query.get(item_id)
    db.session.delete(item_to_delete)
    db.session.commit()
    return redirect(url_for('transfer_invoices'))
# ==========================================================================


# ========================== ЗАПРОСЫ ==========================
@app.route('/requests')
def requests():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    transfer_invoice = TransferInvoices.query.all()  # получаем все посты)
    receive_invoice = ReceiveInvoices.query.all()  # получаем все посты)
    return render_template("requests.html", transfer_invoices=transfer_invoice, receive_invoices=receive_invoice)


@app.route("/transfer_invoices_done/<int:item_id>")
def transfer_invoices_done(item_id):
    item_to_update = TransferInvoices.query.get(item_id)
    item_to_update.is_done = True  # заносим в Requests is_don(сделано?) значение "да"
    db.session.commit()

    uchet_item_to_update = UchetMatCen.query.filter_by(title=item_to_update.uchet_name).first()
    uchet_item_to_update.locate_in = item_to_update.to_field

    db.session.commit()
    return redirect(url_for('requests'))


@app.route("/receive_invoices_done/<int:item_id>")
def receive_invoices_done(item_id):
    item_to_update = ReceiveInvoices.query.get(item_id)
    item_to_update.is_done = True  # заносим в Requests is_don(сделано?) значение "да"
    db.session.commit()

    db.session.commit()
    return redirect(url_for('requests'))
# ==========================================================================


# ========================== НОРМАТИВЫ ==========================
@app.route('/standards')
def standards():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    standards_list = Standards.query.all()  # получаем все посты)
    return render_template("standards.html", standards=standards_list)


@app.route('/standards-new', methods=['GET', 'POST'])
def standards_new():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
            uploaded_file.save(os.path.join('uploads', filename))

            item_to_db = Standards(
                title=os.path.splitext(filename)[0],
                type=os.path.splitext(filename)[1],
            )
            # # заносим запись в бд
            db.session.add(item_to_db)
            db.session.commit()
        return redirect(url_for('standards'))
    return render_template("standards_new.html")


@app.route("/standards_delete/<int:item_id>")
def standards_delete(item_id):
    item_to_delete = Standards.query.get(item_id)
    db.session.delete(item_to_delete)
    db.session.commit()
    os.remove(f'uploads/{item_to_delete.title + item_to_delete.type}')
    return redirect(url_for('standards'))


@app.route("/download/<file>")
def download(file):
    return send_from_directory(directory='uploads', path='uploads', filename=f"{file}", as_attachment=True)
# ==========================================================================


# ___________ РЕГИСТРАЦИЯ ___________
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            if User.query.filter_by(email=request.form.get('email')).first():  # если почта уже существует
                flash("Пользователь с такой электронной почтой уже существует.")
                return redirect(url_for('register'))
            else:  # если такой почты еще нет
                # то ХЭШим пароль
                hash_and_salted_password = generate_password_hash(
                    request.form.get('password'),
                    method='pbkdf2:sha256',
                    salt_length=8,
                )
                # определяем нового пользователя
                new_user = User(
                    email=request.form.get('email').lower(),
                    password=hash_and_salted_password,
                    role="klad",
                )
                # заносим запись в бд
                db.session.add(new_user)
                db.session.commit()
                # login_user(new_user)
                return redirect(url_for('home'))
    return render_template("register.html", form=form)


# ___________ ВХОД ___________
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email = request.form.get('email')  # фиксируем введенный ящик
            password = request.form.get('password')  # фиксируем введенный пароль
            user = User.query.filter_by(email=email).first()  # смотрим совпадения ящиков с бд
            if not user:
                flash("Проверь электронную почту.")
                return redirect(url_for('login'))
            elif not check_password_hash(user.password, password):
                flash("Проверь пароль.")
                return redirect(url_for('login'))
            else:  # если пользователь такой есть и пароли совпадают
                login_user(user)
                return redirect(url_for('home'))
    return render_template("login.html", form=form)


# ___________ ВЫХОД ___________
@app.route('/logout')
def logout():
    logout_user()  # функция flask-login'а
    return redirect(url_for('home'))


# ========================= ОШИБКИ =========================
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404
# ==========================================================


if __name__ == "__main__":
    app.run(debug=True)
