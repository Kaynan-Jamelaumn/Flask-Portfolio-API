from flask import Blueprint, request, jsonify, url_for, redirect, render_template, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from website import db,  images
from flask_uploads import UploadNotAllowed
from flask_login import login_user, logout_user, current_user, login_required

auth = Blueprint('auth', __name__)


@auth.route('/api/logout', methods=['GET'])
@login_required
def api_logout():
    if current_user.is_authenticated:
        logout_user()
        response_data = {
            "message": "Logged out successfully"
        }
        return jsonify(response_data), 200
    response_data = {
        "message": "user is not logged in"
    }
    return jsonify(response_data), 400


@auth.route('/api/signup',  methods=['POST'])
def api_sign_up():
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        password_confirmation = data.get('password_confirmation')
        image = request.files.get('image')
        errors = []
        user = User.query.filter_by(email=email).first()
        if user:
            errors.append('Email already exists')
        if not email or len(email) < 6:
            errors.append('Email must contain at least 6 characters')
        if not name:
            errors.append('Name cannot be null')
        if password != password_confirmation:
            errors.append('Passwords must match')
        if not password or len(password) < 7:
            errors.append('Password must be at least 7 characters long')

        if len(errors) == 0:
            hashed_password = generate_password_hash(password, method='sha256')
            user = User(email=email, name=name, password=hashed_password)
            if image:  # Check if an image was uploaded
                try:
                    filename = images.save(image)
                    user.image = filename
                except UploadNotAllowed:
                    response_data = {
                        "error": "File type is not allowed"
                    }
                    return jsonify(response_data), 400

            try:
                db.session.add(user)
                db.session.commit()

                response_data = {
                    "message": "Registration successful",
                    "user_id": user.id
                }
                return jsonify(response_data), 201
            except Exception as e:
                response_data = {
                    "error": "An error occurred while registering"
                }
                return jsonify(response_data), 500
        else:
            response_data = {
                "errors": errors
            }
            return jsonify(response_data), 400


@auth.route('/api/login', methods=['POST'])
def api_login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            response_data = {
                "message": "Login was successful",
                "user_id": user.id
            }
            return jsonify(response_data), 200
        else:
            response_data = {
                "error": "Invalid credentials"
            }
            return jsonify(response_data), 401

    response_data = {
        "message": "Method not allowed"
    }
    return jsonify(response_data), 405


@auth.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/signup',  methods=['GET', 'POST'])
def signUp():
    if request.method == 'GET':
        return render_template("auth/signUp.html")

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirmation = request.form.get('password-confirmation')
        image = request.files['image']
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')

        elif not email or len(email) < 6:
            flash('Email deve ter mais de 6 caracteres.', category='error')
        elif not name or len(name) < 2:
            flash('Nome deve ter mais de 2 caracteres.', category='error')
        elif password != password_confirmation:
            flash('Password Doest Match.', category='error')
        elif not password or len(password) < 7:
            flash('Must Contain a lenght of 7.', category='error')
        else:
            user = User(email=email, name=name, password=generate_password_hash(
                password, method='sha256'))
            if image:  # Check if an image was uploaded
                try:
                    filename = images.save(image)
                    user.image = filename
                except UploadNotAllowed:
                    flash('File type is not allowed.', category='error')
                    return render_template("auth/login.html")

            try:
                db.session.add(user)  # adiciona o usuario no banco de dados
                db.session.commit()  # confirma que adicionou

                login_user(user, remember=True)
                flash('The account was created successfuly', category='success')
                return redirect(url_for('views.home'))
            except Exception as e:
                flash('An error occurred while registering', category='error')
    return render_template("auth/login.html")


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("auth/login.html")
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # pega o primeiro usuario com o email
        user = User.query.filter_by(email=email).first()

        if user:
            if check_password_hash(user.password, password):
                flash('Login was Successful!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Wrong Password.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("auth/login.html")
