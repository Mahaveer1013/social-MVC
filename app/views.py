from flask import render_template, request, flash, redirect, url_for,jsonify,session
from app import app, db, socketio
import json
from . import db
import os
from .models import Login,Post
from sqlalchemy.sql import func
from flask_socketio import emit
from sqlalchemy import desc
import pandas as pd
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user,login_user
from .functions import *

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/user_login_page")
def user_login_page():
    return render_template("index.html")

@app.route("/user_signup_page")
def user_signup_page():
    return render_template("signup.html")

@app.route("/user_signup",methods=['POST','GET'])
def user_signup():
    if(request.method=='POST'):
        name=request.form['name']
        username=request.form['u_name']
        password=request.form['pass']
        confirm_password=request.form['c_pass']
        email=request.form['email']
        dp=request.files['dp']
        if dp:
            file_name=username+".jpg"
            dp_name=secure_filename(dp.filename)
            file_path=os.path.join(app.config['UPLOAD_DP'], file_name)
            dp.save(file_path)
        else:
            file_name=username+".jpg"
            file_path=os.path.join(app.config['UPLOAD_DP'], file_name)

        if(password != confirm_password):
            flash('Password and Confirm password Do not Match')

        user = Login.query.filter_by(username=username).first()
        if(user):
            flash('Username already exists. Please choose a different username.')
        else:
            req=Login(name=name,username=username,password=password,email=email,dp_name=file_name)
            db.session.add(req)
            db.session.commit()

    return render_template("index.html")

@app.route("/user_login",methods=['POST','GET'])
def user_login():
    username=request.form['username']
    password=request.form['password']

    user = Login.query.filter_by(username=username).first()
    if user:
        if user.password == password:
            login_user(user, remember=True)
            session['username'] = username
            session['name'] = user.name
            session['email'] = user.email
            session['dp_name']=user.dp_name
            return redirect(url_for('user_dashboard'))
        else:
            flash("Incorrect Password", category='error')
    else:
        flash("Incorrect Username", category='error')
    return render_template("index.html")

@app.route("/user_dashboard",methods=['POST','GET'])
def user_dashboard():
    username = session.get('username')
    email = session.get('email')
    name = session.get('name')
    dp_name=session.get('dp_name')
    if (Post.query.filter_by(username=username).all()):
        user_post=Post.query.filter_by(username=username).all()
        return render_template("dashboard.html",username=username,email=email,user_post=user_post,name=name,dp_name=dp_name)

    return render_template("dashboard.html",username=username,email=email,name=name,dp_name=dp_name)

@app.route("/feedback")
def feedback():
    return render_template("feedback.html")

@app.route("/user_feedback",methods=['POST','GET'])
def user_feedback():
    feedback=request.form['feedback']
    username = session.get('username')
    email = session.get('email')
    admin_email="mahaveer.panimalar@gmail.com"
    subject="Feedback from {}".format(username)
    send_mail(admin_email, subject, feedback)

    subject="Thank You For Contacting Us "
    body="Your Feedback was Considered And Will Be In Touch Shortly"
    send_mail(email, subject, body)
    return redirect(url_for("user_dashboard"))

@app.route("/add_post",methods=['POST','GET'])
@login_required
def add_post():
    post_msg=request.form['post_msg']
    username = session.get('username')
    user_folder = os.path.join(app.config['UPLOAD_POST'], username)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    post = request.files['post']

    if post:
        # Set the filename to be the username with a .jpg extension
        num=0
        while True:
            user_folder = os.path.join(app.config['UPLOAD_POST'], username, str(num)+".jpg")
            if not os.path.exists(user_folder):
                file_name = str(num) + ".jpg"
                break
            num+=1

        #file_path = os.path.join(user_folder, file_name)
        post.save(user_folder)
        new_post = Post(post_msg=post_msg, username=username, post_name=file_name)
        db.session.add(new_post)
        db.session.commit()

    else:
        # If no post is provided, create an empty file with the username as the filename
        # file_name = username + ".jpg"
        # file_path = os.path.join(user_folder, file_name)
        # open(file_path, 'a').close()
        flash("Error in Uploading File")

    return redirect(url_for('user_dashboard'))

