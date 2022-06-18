from flask import Blueprint, redirect, render_template, request, url_for, flash
from flask_login import login_user,logout_user,login_required, current_user

from website import views
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash 
from . import db

auth = Blueprint("auth",__name__)

@auth.route("/login",methods = ["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        
        if user:
            if user.first_name != "admin":
                if check_password_hash(user.password,password):
                    flash("Logged in successfully",category='success')
                    login_user(user,remember=True)
                    return redirect(url_for('views.index'))
                else:
                    flash("Wrong password",category="error")
            else:
                flash("User doesn't exist",category="error")
        else:
            flash("User doesn't exist",category="error")

    return render_template("auth/login.html", user=current_user)

@auth.route("/signup",methods=["GET","POST"])
def signup():
    if request.method == "POST":
        #Take address as well
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get("password1")
        password2 = request.form.get('password2')
        address = request.form.get('address')


        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email Already exists", category = "error")
        elif len(email) < 4:
            flash("Email must be greater than 4 characters" , category="error")
        elif len(first_name) < 2:
            flash("Firstname must be greater than 3 characters" , category="error")
        elif password1 != password2:
            flash("passwords don't match" , category="error") 
        elif len(password1) < 4:
            flash("password must be greater than 7 characters" , category="error")
        else:
            new_user = User(email=email, first_name= first_name, address=address,password = generate_password_hash(password1,method="sha256"))
            db.session.add(new_user)
            db.session.commit()
            flash("Account created", category = 'success')
            return redirect(url_for("auth.login"))
    return render_template("auth/signup.html",user=current_user)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
