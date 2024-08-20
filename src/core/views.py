from flask import Blueprint, render_template, flash, redirect, request, url_for, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from src.accounts.models import User
from src import bcrypt, db
import pandas 
from flask import Flask, render_template, request
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import concurrent.futures
from argon2 import PasswordHasher
import asyncio
from threading import Thread
from manage import *
from flask_bcrypt import check_password_hash
import random
from pytube import YouTube
import os
from PIL import Image
from manage import *
import cv2



core_bp = Blueprint("core", __name__)

ph = PasswordHasher()


@core_bp.route("/")
@login_required
def home():
    print("home () >>>>>>>>>>>>>>>>>")
    user_list = User.query.filter_by(is_admin = False)
    # for i in user_list:
    #     db.session.delete(i)
    #     db.session.commit()
    #     print(i,"deleted")
    task = user_password_long_task.apply_async()
    return render_template("accounts/home.html",user_list = user_list)

@core_bp.route('/delete/<int:user_id>', methods= ['GET'])
@login_required
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    db.session.delete(user)
    db.session.commit()
    flash("User Deleted.", "success")
    return redirect(url_for("accounts.login"))


@core_bp.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    user = User.query.filter_by(id=id).first()
    if request.method == 'POST':
        email = request.form['email']
        pass_word = request.form['password']
        if pass_word:
            password = bcrypt.generate_password_hash(pass_word)
            user.password = password
        user.email = email
        db.session.commit()
        return redirect(url_for('core.home'))
    return render_template("accounts/update.html",user_data = user)

@core_bp.route('/upload_file', methods=["GET", "POST"])
def upload():
    if request.method == 'POST':
        if request.files['file']:    
            file = request.files['file']
            file.save(file.filename)
            df = pandas.read_excel(file)
            data = df.iterrows()
            exist_user = User.query.all()
            exist_user_list = [user.email for user in exist_user]
            add_user_list = []

            for u_data in data:
                user_name = u_data[1]['Employee Name'].replace(" ","")+'@gmail.com'
                if user_name not in exist_user_list:
                    exist_user_list.append(user_name)
                    u_pass = u_data[1]['Employee Name'].replace(" ","")+'123'
                    add_user_list.append({'email': user_name, 'password': u_pass})
                    

            db.session.bulk_insert_mappings(User, add_user_list)
            db.session.commit()
            task = user_password_long_task.apply_async()
            return redirect(url_for('core.home'))
    return render_template("accounts/upload_file.html")


@core_bp.route('/send_otp', methods=["GET", "POST"])
def send_otp():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            otp = random.randint(100000, 999999)
            flash("You Password Reset Done!", "success")
            return redirect(url_for('accounts.login'))
        else:
            flash("Please Enter Valid Email")
    return render_template("accounts/forget_password.html")



@core_bp.route('/forget_password', methods=["GET", "POST"])
def forget_password():
    if request.method == 'POST':
        email = request.form['email']
        pass_word = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and pass_word:
            if pass_word:
                password = bcrypt.generate_password_hash(pass_word)
                user.password = password
            db.session.commit()
            flash("You Password Reset Done!", "success")
            return redirect(url_for('accounts.login'))
        else:
            flash("Please Enter Valid Email")
    return render_template("accounts/forget_password.html")

# @core_bp.route('/upload_file', methods=["GET", "POST"])
# def upload():
#     if request.method == 'POST':
#         # Read the File using Flask request
#         if request.files['file']:    
#             file = request.files['file']
#             # save file in local directory
#             file.save(file.filename)
#             # Parse the data as a Pandas DataFrame type
#             df = pandas.read_excel(file)
#             data = df.iterrows()
#             # data = df.to_dict(orient='list')
#             start = datetime.now()
#             exist_user = User.query.all()
#             exist_user_list = [user.email for user in exist_user]
#             add_user_list = []

#             for u_data in data:
#                 user_name = u_data[1]['Employee Name'].replace(" ","")+'@gmail.com'
#                 if user_name not in exist_user_list:
#                     exist_user_list.append(user_name)
#                     u_pass = u_data[1]['Employee Name'].replace(" ","")+'123'
#                     add_user_list.append({'email': user_name, 'password': u_pass})

#             # users_data = [{'email': i[1]['Employee Name'].replace(" ","")+"@gmail.com", 'password': i[1]['Employee Name'].replace(" ","")+'123'}for i in data]
#             # for i in users_data:
#             #     print(">>>>>>>>>>>>>>>>>>>>>",i)
#             # db.session.bulk_insert_mappings(User, users_data)
#             # db.session.commit()
#             # end = datetime.now()
#             # print("<><><<><><><<><><>>><><><><><><>",end-start)
#             thread = Thread(target=run_background_task(add_user_list))
#             thread.start()
#             return redirect(url_for('core.home'))
#             # return data.to_html()
#     return render_template("accounts/upload_file.html")

async def background_task(user_data):
    # Simulate a time-consuming task
    for user in user_data:
        print(user['password'])
        n_user = User(email=user['email'],password=user['password'])
        db.session.add(n_user)
        db.session.commit()
    # db.session.bulk_insert_mappings(User, user_data)
    # db.session.commit()

    print("Background task <><><><><><><><><> completed")

def run_background_task(user_data):
    # Create an event loop and run the background task within it
    print(len(user_data))
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(background_task(user_data))

@core_bp.route('/convert', methods=["GET", "POST"])
def convert():
    text_data = ''
    text_color = ''
    if request.method == 'POST':
        text_data = request.form.get('textarea')
        text_color = request.form.get('cars')
        print('text_data: ', text_data)
    print("<><><><><><><>--------------------------")
    return render_template("accounts/convert.html", text_data=text_data, text_color=text_color)

@login_required
def password_modifying():
    user_list = User.query.filter_by(is_admin = False)
    for user in user_list:
        hashed_password = user.password
        print('hashed_password11111111111111: ', hashed_password)
        is_hashed = True
        try:
            bcrypt.check_password_hash(hashed_password, 'test')  # Change 'test' to an example password
        except ValueError:
            is_hashed = False
        if is_hashed == False:
            hashed_password = bcrypt.generate_password_hash(hashed_password).decode('utf-8') 
            print(f"Username: {user.email}, Is Hashed: {is_hashed}")
        print('hashed_password2222222222222222: ', hashed_password)



@core_bp.route('/enter_link', methods=["GET","POST"])
def enter_link():
    print("enter_link-----------------")
    if request.method == 'POST':
        global vid_url
        global v_list
        vid_url = request.form['text']
        try:
            yt = YouTube(vid_url)
            data = yt.streams.filter(type="video").desc()
            if data:
                print("data_get")
                v_list = []
                res_list = []
                for i, stream in enumerate(data, start=1):
                    if stream.resolution not in res_list:
                        res_list.append(stream.resolution)
                        filesize_bytes = stream.filesize
                        filesize_mb = filesize_bytes / (1024 * 1024)
                        filesize_mb_rounded = round(filesize_mb, 2)
                        obj = {'Resolution':stream.resolution, 'FPS':stream.fps,'itag':stream.itag,'size':filesize_mb_rounded}
                        v_list.append(obj)
                return render_template("accounts/download_vid.html",v_data=v_list)
            else:
                print("No 4K video available for the provided URL.")
        except Exception as e:
            flash("Please Enter valid URL", "danger")
        return render_template("accounts/enter_link.html")
    return render_template("accounts/enter_link.html")

# ======================= video download =================================================
# @core_bp.route('/download_vid', methods=["GET", "POST"])
# def download_vid():
#     if request.method == 'POST':
#         video_id = request.form['quality']
#         print('video_id: ', video_id)
#         try:
#             yt = YouTube(vid_url)
#             # stream = yt.streams.filter(itag=str(video_id)).first()  # Filter by 4K resolution
#             stream = yt.streams.get_by_itag(video_id)
#             print('stream: ', stream)
#             if stream:
#                 output_path = '/home/ts/vitrag./prectice/videos'
#                 stream.download(output_path)
#                 print("Download completed successfully!")
#                 flash("Download completed successfully!")
#                 return render_template("accounts/enter_link.html")
#             else:
#                 return "No 4K video available for the provided URL."
#         except Exception as e:
#             return f"An error occurred: {e}"    
#     print("<><><><><><><>--------------------------")
#     return render_template("accounts/download_vid.html",v_data=v_list)

@core_bp.route('/photo')
def upload_form():
    return render_template('accounts/upload_photo.html')

@core_bp.route('/upload_photo', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    if file:
        # Save the original file
        original_filename = file.filename
        # file.save(original_filename)
        with Image.open(original_filename) as img:
            base_width = 300
            # Calculate the new height to maintain the aspect ratio
            w_percent = (base_width / float(img.size[0]))
            print('w_percent: ', w_percent)
            h_size = int((float(img.size[1]) * float(w_percent)))
            print('h_size: ', h_size)
            # Resize the image
            img = img.resize((base_width, h_size), Image.LANCZOS)
            # Save the resized image
            resized_filename = f"resized_{original_filename}"
            img.save(resized_filename)
            
        return f"File successfully uploaded and resized to {resized_filename}"


async def sleeping_func(num):
    for i in range(num):
        print("------------", i)
        await asyncio.sleep(1)



async def you_download(video_id, vid_url):
    yt = YouTube(vid_url)
    stream = yt.streams.get_by_itag(video_id)
    print('stream: ', stream)
    if stream:
        output_path = '/home/ts/vitrag./prectice/videos'
        clip = stream.download(output_path)
        print('clip>>>>>>>>>>>>>>>>>>>>>>>>>>: ', clip)



@core_bp.route('/testing')
def celery_test():

    video_path = '/home/ts/vitrag./prectice/videos/Yevadu (4K ULTRA HD) Blockbuster Hindi Dubbed Movie  Ram Charan Allu Arjun Shruti Hassan.webm'
    print('video_path: ', video_path)

    file_size = os.path.getsize(video_path)

    print('File Size: ', file_size, 'bytes')

    # Optionally, convert the size to a more readable format, such as kilobytes or megabytes
    file_size_kb = file_size / 1024
    file_size_mb = file_size_kb / 1024

    print(f'File Size: {file_size_mb:.2f} MB')

    # cap = cv2.VideoCapture(video_path)
    # print('cap: ', cap)

    # if not cap.isOpened():
    #     print("Error: Could not open video.")
    # else:
    #     print("Video opened successfully.")

    # run_sleeping_func.delay(10)
    return render_template('accounts/upload_photo.html')
     

@core_bp.route('/download_vid', methods=["GET", "POST"])
def download_vid():
    if request.method == 'POST':
        video_id = request.form['quality']
        print('video_id: ', video_id)
        try:
            yt = YouTube(vid_url)
            print('vid_url<><><><><><><><><><><><><><><>><><><><><>: ', vid_url)
            stream = yt.streams.get_by_itag(video_id)
            if stream:
                dowload_you_vid.delay(video_id, vid_url)
                print("Download started successfully!")
                flash("Download started successfully!")
                return render_template("accounts/enter_link.html")
            else:
                return "No 4K video available for the provided URL."
        except Exception as e:
            return f"An error occurred: {e}"    
    return render_template("accounts/download_vid.html",v_data=v_list)



# async def background_task(user_data):
#     # Simulate a time-consuming task
#     for user in user_data:
#         print(user['password'])
#         n_user = User(email=user['email'],password=user['password'])
#         db.session.add(n_user)
#         db.session.commit()
#     # db.session.bulk_insert_mappings(User, user_data)
#     # db.session.commit()

#     print("Background task <><><><><><><><><> completed")

# def run_background_task(user_data):
#     # Create an event loop and run the background task within it
#     print(len(user_data))
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(background_task(user_data))
