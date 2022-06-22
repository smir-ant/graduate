from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SelectField
from wtforms.validators import DataRequired, Email, Length, InputRequired


# Форма для регистрации
class RegisterForm(FlaskForm):
    email = StringField(label='*Почта',
                        validators=[DataRequired(message='Обязательно к заполнению'),
                                    Email(message='Укажите действующую почту')])
    password = PasswordField(label='*Пароль',
                             validators=[DataRequired(message='Обязательно к заполнению'),
                                         Length(min=6, message='Минимальная длина 6')],
                             description='(Минимальная длина = 6)')


# форма для входа
class LoginForm(FlaskForm):
    email = StringField(label='Почта', validators=[DataRequired(message='Обязательно к заполнению'),
                                                   Email(message='Укажите действующую почту')])
    password = PasswordField(label='Пароль', validators=[DataRequired(message='Обязательно к заполнению')])


class NewItem(FlaskForm):
    title = StringField(label='Название', validators=[DataRequired(message='Обязательно к заполнению')])
    type = SelectField(label='Тип', coerce=str)  # 1 из TipiMatCen(db.Model)
    locate_in = SelectField(label='Находится в', coerce=str)  # 1 из Otdeli(db.Model)
    guarantee = DateField(label='Гарантия до', validators=[DataRequired(message='Обязательно к заполнению')])
    inventory_number = StringField(label='Инв. №', validators=[DataRequired(message='Обязательно к заполнению')])
    work_from = DateField(label='Работает с', validators=[DataRequired(message='Обязательно к заполнению')])


class NewMaterialType(FlaskForm):
    title = StringField(label='Название', validators=[DataRequired(message='Обязательно к заполнению')])


class NewDepartment(FlaskForm):
    title = StringField(label='Название', validators=[DataRequired(message='Обязательно к заполнению')])
    phone_number = StringField(label='Номер телефона', validators=[DataRequired(message='Обязательно к заполнению')])


class NewTransferInvoice(FlaskForm):
    uchet_field = SelectField(label='Товар', coerce=str)
    from_field = SelectField(label='От', coerce=str)
    to_field = SelectField(label='К', coerce=str)
    in_connection_with = StringField(label='В связи с', validators=[DataRequired(message='Обязательно к заполнению')])
    responsible = StringField(label='Ответственный', validators=[DataRequired(message='Обязательно к заполнению')])


class NewReceiveInvoice(FlaskForm):
    date = DateField(label='Дата накладной', validators=[DataRequired(message='Обязательно к заполнению')])
    invoice_number = StringField(label='№ накладной', validators=[DataRequired(message='Обязательно к заполнению')])
    suppliers_list = SelectField(label='Приобретено в', coerce=str)  # список поставщиков
    receiver = StringField(label='Получил', validators=[DataRequired(message='Обязательно к заполнению')])

    title = StringField(label='Название', validators=[DataRequired(message='Обязательно к заполнению')])
    type = SelectField(label='Тип', coerce=str)  # 1 из TipiMatCen(db.Model)
    locate_in = SelectField(label='Находится в', coerce=str)  # 1 из Otdeli(db.Model)
    guarantee = DateField(label='Гарантия до', validators=[DataRequired(message='Обязательно к заполнению')])
    inventory_number = StringField(label='Инв. №', validators=[DataRequired(message='Обязательно к заполнению')])


class NewSuppliers(FlaskForm):
    title = StringField(label='Название', validators=[DataRequired(message='Обязательно к заполнению')])
    phone_number = StringField(label='Номер телефона', validators=[DataRequired(message='Обязательно к заполнению')])
    site = StringField(label='Сайт', validators=[DataRequired(message='Обязательно к заполнению')])
