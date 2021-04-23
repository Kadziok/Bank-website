from flask import render_template, flash, redirect, url_for, request, Response, jsonify
from app import app, db, mail
from app.models import User, Transfer, Forgot
from app.forms import LoginForm, RegistrationForm, TransferForm, ForgotForm, ResetForm
from flask_login import login_required, current_user, login_user, logout_user
from flask_mail import Mail, Message
from time import time
from flask_jwt import JWT, jwt_required, current_identity
import json


db_transfer = None

@app.route('/')
@app.route('/index')
@login_required
def index():
    print(current_user.id)
    #msg = Message('Hello', sender = 'kadziola@vp.pl', recipients = ['kkadziola@gmail.com'])
    #msg.body = "Testy maila"
    #mail.send(msg)
    transfers = Transfer.query.filter_by(user_id=current_user.id).all()
    print(transfers)
    if current_user.username == 'admin':
        return redirect(url_for('admin_panel'))
    return render_template('index.html', title='Home', transfers=transfers)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        print(form.username.data)
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))



@app.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    form = TransferForm()
    if request.method == 'POST' and form.validate_on_submit():
        global db_transfer
        db_transfer = Transfer(user_id=current_user.id, sum=form.sum.data,
            account=form.account.data, name=form.receiver.data)
        return redirect(url_for('confirm'))
    return render_template('transfer2.html', title='Przelew', form=form)


@app.route('/confirm', methods=['GET', 'POST'])
@login_required
@login_required
def confirm():
    global db_transfer
    form = TransferForm()
    if request.method == 'POST' and form.validate_on_submit():
        print(form.receiver.data)
        global db_transfer
        if (db_transfer.recipent_account == form.account.data and
            db_transfer.recipent_name == form.receiver.data and
            db_transfer.sum == form.sum.data):
            db.session.add(db_transfer)
            db.session.commit()
        db_transfer = None
        return render_template("confirmed.html", receiver=form.receiver.data,
            sum=form.sum.data, account=form.account.data)
    return render_template('confirm2.html', title='Zatwierdź', form=form,
            receiver=db_transfer.recipent_name,
            sum=db_transfer.sum, account=db_transfer.recipent_account)



@app.route('/confirmed', methods=['GET'])
@login_required
def confirmed():
    return render("confirmed.html")

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    form = ForgotForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        code = str(hash(str(time()) + str(user.id)))
        x = Forgot(user_id=user.id, code=code)
        db.session.add(x)
        db.session.commit()
        msg = Message('Hello', sender = 'kadziola@vp.pl', recipients = ['kkadziola@gmail.com'])
        msg.body = "https://localhost/reset?r=" + code
        mail.send(msg)
        return redirect(url_for('login'))
    return render_template('forgot.html', title='Resetowanie hasła', form=form)

@app.route('/reset', methods=['GET', 'POST'])
def reset():
    forgot = Forgot.query.filter_by(code=request.args['r']).first()
    if forgot:
        form = ResetForm()
        if request.method == 'POST' and form.validate_on_submit():
            user = User.query.filter_by(id=forgot.user_id).first()
            user.set_password(form.password.data)
            db.session.delete(forgot)
            db.session.commit()
            return redirect(url_for('login'))
        return render_template('reset.html', title='Resetowanie hasła', form=form)

    return "ERROR"


@app.route('/admin_panel', methods=['GET'])
@login_required
def admin_panel():
    if current_user.id != 1:
        redirect(url_for("index"))
    transfers = Transfer.query.all()
    return render_template('admin_panel.html', transfers=transfers)
    

@app.route('/accept', methods=['POST'])
@login_required
def accept():
    if current_user.id == 1:
        transfer = request.get_json()['transfer']
        accepted = Transfer.query.filter_by(id=transfer).first()
        accepted.confirmed = 1
        db.session.commit()
        return Response("", status=200, mimetype='application/json')
    return Response("{'cause':'forbidden'}", status=403, mimetype='application/json')


@app.route('/api/login2', methods=['POST'])
def api_login2():
    data = request.get_json()
    print(data['username'], data['password'])
    user = User.query.filter_by(username=data['username']).first()
    if user is None or not user.check_password(data['password']):
        return "Błędne dane\n"
    login_user(user)
    return "Zalogowany\n"


@app.route('/api/transfers', methods=['GET'])
@jwt_required()
def api_transfers():
    transfers = Transfer.query.filter_by(user_id=current_identity.id).all()
    data = {'transfers': [{
                'odbiorca': t.recipent_name,
                'konto': t.recipent_account,
                'kwota': t.sum
                } for t in transfers]}
    return data


@app.route('/api/transfer', methods=['POST'])
@jwt_required()
def api_transfer():
    data = request.get_json()
    global db_transfer
    db_transfer = Transfer(user_id=current_identity.id, sum=data['sum'],
            account=data['account'], name=data['name'])
    return data


@app.route('/api/confirm', methods=['POST'])
@jwt_required()
def api_confirm():
    data = request.get_json()
    global db_transfer
    if (db_transfer.user_id == current_identity.id and
            db_transfer.sum == data['sum'] and
            db_transfer.recipent_account == data['account'] and
            db_transfer.recipent_name == data['name']):

        db.session.add(db_transfer)
        db.session.commit()
        return Response("{'success':'confirmed'}", status=200, mimetype='application/json')
    db_transfer = None
    return Response("{'failed':'different_data'}", status=400, mimetype='application/json')

@app.route('/api/admin/to_accept', methods=['GET'])
@jwt_required()
def api_to_accept():
    if current_identity.id == 1:
        transfers = Transfer.query.filter_by(confirmed=0).all()
        data = {'transfers': [{
                    'id': t.id,
                    'odbiorca': t.recipent_name,
                    'konto': t.recipent_account,
                    'kwota': t.sum
                    } for t in transfers]}
        return data
    return Response("{'cause':'forbidden'}", status=403, mimetype='application/json')


@app.route('/api/admin/accept', methods=['POST'])
@jwt_required()
def api_accept():
    if current_identity.id == 1:
        data = request.get_json()
        transfer = Transfer.query.filter_by(id=data['id']).first()
        transfer.confirmed = 1
        db.session.commit()
        return Response("{'success':'accepted'}", status=200, mimetype='application/json')
    return Response("{'cause':'forbidden'}", status=403, mimetype='application/json')