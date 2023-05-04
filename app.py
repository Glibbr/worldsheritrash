import os
import json

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, url_for, request, session, jsonify, send_from_directory
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash, safe_join
from werkzeug.utils import secure_filename
from datetime import datetime, timezone

from helpers import login_required

# Configure application
app = Flask(__name__)
app.secret_key = "?th!sIsANy8inD0fStrlNgf0rFl8sk!"

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
# Make sure that file size is limited
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
# Reject file types that we do not want to handle
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png']
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
#app.config["SESSION_COOKIE_SAMESITE"] ='None'
app.config["SESSION_COOKIE_SECURE"] = 'True'
Session(app)

# Path for saving files / images
app.config['UPLOAD_PATH'] = './img/uploads/'
PATH_TO_IMAGE_DIR = './img/cap/'

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///trash.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"

    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    header['Access-Control-Allow-Methods'] = 'OPTIONS, HEAD, GET, POST, DELETE, PUT'
    return response


@app.errorhandler(413)
def too_large(e):
    return "File is too large", 413


@app.route("/")
def index():

    status1 = "reported"
    status2 = "cleaned"

    trash_pins = db.execute(
        "SELECT latitude AS lat, longitude AS lng from trash WHERE status = ?", status1)
    clean_pins = db.execute(
        "SELECT latitude AS lat, longitude AS lng from trash WHERE status = ?", status2)

    # Housekeeping - Clean up possible leftovers of unfinished reports
    status3 = "capture"
    trash_db = db.execute("SELECT ID FROM trash WHERE status = ?", status3)
    # check if there is even something to delete
    if trash_db != []:
        trashID = db.execute("SELECT ID FROM trash WHERE status = ?", status3)
        img_db = db.execute("SELECT ID FROM img WHERE reportID = ?", trashID[0]["ID"])
        # there is also an entry in img database
        if img_db != []:
            # delete entry in img db first to avoid foreign key constraint
            db.execute("DELETE FROM img WHERE reportID = ?", trashID[0]["ID"])
            db.execute("DELETE FROM trash WHERE ID = ?", trashID[0]["ID"])
        # only entry in trash db exists
        else:
            db.execute("DELETE FROM trash WHERE ID = ?", trashID[0]["ID"])

    return render_template("index.html", trash_pins=trash_pins, clean_pins=clean_pins)


@app.route("/img/<path:filename>")
def static_dir(filename):
    return send_from_directory("img", filename)

# simple imprint / contact page
@app.route("/imprint")
def imprint():
    return render_template("imprint.html")

# image upload and file naming route
@app.route("/upload", methods=['POST'])
@login_required
def upload_files():

    url = request.referrer
    url_cap = url.find("capture")

    user_id = session["user_id"]
    uploaded_file = request.files["file"]
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            return "Invalid image", 400
        else:
            filename = str(user_id) + "_" + datetime.now(timezone.utc).strftime(
                "%Y%m%d-%H%M%S%f")[:-3] + os.path.splitext(filename)[1]
            uploaded_file.save(os.path.join(
                app.config['UPLOAD_PATH'], filename))

            date = datetime.now(timezone.utc)
            file_src = "uploads"
            report_Id = session.get("reportID", None)

            # check where this request was send from
            if url_cap == -1:
                info = "clean"
            else:
                info = "trash"

            db.execute("INSERT INTO img "
                       " (img_date, file_src, file_name, info, reportID) "
                       " VALUES(?, ?, ?, ?, ?)", date, file_src, filename, info, report_Id)
    # upload returns an empty result + proper response code
    return '', 204

# Report capturing routine // includes also trash, report, cancel and delete
@app.route("/capture", methods=["GET", "POST"])
@login_required
def capture():

    # Get the latest reported position
    lat = request.args.get("lat")
    lng = request.args.get("lng")

    # Collect additional information
    user_id = session["user_id"]
    date = datetime.now(timezone.utc)
    status = "capture"

    # store values in database as temp
    db.execute("INSERT INTO trash "
               " (user_id_trash, report_date, status, latitude, longitude) "
               " VALUES(?, ?, ?, ?, ?)", user_id, date, status, lat, lng)

    # get the ID of this database entry
    rows_ID = db.execute("SELECT ID"
                         " FROM trash "
                         " WHERE latitude = ? AND longitude = ? "
                         " ORDER BY report_date DESC LIMIT 1", lat, lng)
    report_ID = rows_ID[0]["ID"]

    # safe ID of database entry in session to allow other routes to consume
    session["reportID"] = report_ID

    return render_template("capture.html", lat=lat, lng=lng)


# Image capturing routine
@app.route("/image", methods=["POST"])
def image():

    url = request.referrer
    url_cap = url.find("capture")
    user_id = session["user_id"]

    i = request.files["image"]  # get the image
    f = ("%s.png" % (str(user_id) + "_" +
         datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S%f")[:-3]))
    i.save('%s/%s' % (PATH_TO_IMAGE_DIR, f))

    date = datetime.now(timezone.utc)
    file_src = "cap"
    report_Id = session.get("reportID", None)

    # check where this request was send from
    if url_cap == -1:
        info = "clean"
    else:
        info = "trash"

    db.execute("INSERT INTO img "
               " (img_date, file_src, file_name, info, reportID) "
               " VALUES(?, ?, ?, ?, ?)", date, file_src, f, info, report_Id)

    return (f)


# Delete existing report procedure
@app.route("/delete")
@login_required
def delete_report():

    report_Id = session.get("reportID", None)
    status = "deleted"

    # TODO check if we can remove files from non static folder with server routine on deployment
    info = "del"
    # mark the images for delete
    db.execute("UPDATE img SET info = ? WHERE ID = ?", info, report_Id)

    # don´t delete existing reports but mark them deleted and remove them from view
    db.execute("UPDATE trash SET status = ? WHERE ID = ?",
               status, report_Id)

    flash("Report deleted!", "success")
    return redirect("/")


# Report cancellation procedure
@app.route("/cancel")
def cancel_report():

    report_Id = session.get("reportID", None)

    # TODO check if we can remove files from non static folder
    info = "del"
    # mark the images for delete
    db.execute("UPDATE img SET info = ? WHERE ID = ?", info, report_Id)

    # remove the database entry as cancelled
    db.execute("DELETE FROM trash WHERE ID = ?", report_Id)

    flash("Report cancelled!", "error")
    return redirect("/")


# Report processing procedure
@app.route("/report", methods=["GET", "POST"])
@login_required
def report_submit():

    if request.method == "POST":

        title = request.form.get("title")
        comment = request.form.get("details")
        status = "reported"

        # read temp Id from session // ID from current position
        report_Id = session.get("reportID", None)

        # update SQL database
        db.execute("UPDATE trash SET title = ?, "
                   " comment = ?, "
                   " status = ? "
                   " WHERE ID = ?", title, comment, status, report_Id)

        flash("Succesfully reported!", "success")
        return redirect("/")


# Load report details
@app.route("/trash", methods=["GET", "POST"])
def showTrash():

    try:

        lat = request.args.get('lat')
        lng = request.args.get('lng')

        # look for the closest position as marker is not always precise
        trash_info = db.execute("SELECT ID, title, user_id_trash, report_date, comment, latitude , longitude "
                                " FROM trash "
                                " ORDER BY ABS(latitude - ?), ABS(longitude - ?) "
                                " LIMIT 1", lat, lng)

        user_name = db.execute(
            "SELECT username FROM users WHERE ID = ?", trash_info[0]["user_id_trash"])

        report_ID = trash_info[0]["ID"]

        # safe ID of database entry in session to allow other routes to consume
        session["reportID"] = report_ID

        info = "trash"

        # load image names from db
        imgs = db.execute("SELECT file_src, file_name "
                          " FROM img "
                          " WHERE info = ? AND reportID = ?", info, report_ID)

        return render_template("trash.html", trash_info=trash_info, imgs=imgs, user_name=user_name)

    except Exception as e:
        return str(e)


# Load clean report details
@app.route("/cleanup", methods=["GET", "POST"])
@login_required
def cleanup():

    if request.method == "GET":

        id = request.args.get('id')
        user_id_clean = session["user_id"]

        # look for the closest position as marker is not always precise
        trash_info = db.execute("SELECT ID, title, user_id_trash, user_id_clean, report_date, latitude , longitude "
                                " FROM trash "
                                " WHERE ID = ?", id)

        user_name_trash = db.execute(
            "SELECT username FROM users WHERE ID = ?", trash_info[0]["user_id_trash"])

        if user_id_clean == None or user_id_clean == "":
            user_name_clean = "Guest"
        else:
            # only the current user can clean
            user_name_clean = session["user_name"]

        # safe ID of database entry in session to allow other routes to consume
        session["reportID"] = id
        info = "trash"

        # loading trash images / before
        imgs_trash = db.execute("SELECT file_src, file_name "
                                " FROM img "
                                " WHERE info = ? AND reportID = ?", info, id)

        return render_template("cleanup.html", trash_info=trash_info, imgs_trash=imgs_trash, user_name_trash=user_name_trash, user_name_clean=user_name_clean)

    if request.method == "POST":

        report_Id = session.get("reportID", None)
        user_id_clean = session["user_id"]

        clean_comment = request.form.get("clean_details")
        clean_date = datetime.now(timezone.utc)
        status = "cleaned"

        # update SQL database
        db.execute("UPDATE trash SET clean_comment = ?, "
                   " clean_date = ?, "
                   " user_id_clean = ?, "
                   " status = ? "
                   " WHERE ID = ?", clean_comment, clean_date, user_id_clean, status, report_Id)

        flash("Place cleaned up! - Thank you", "success")
        return redirect("/")


# Load clean report details
@app.route("/clean", methods=["GET", "POST"])
def showCleanInfo():

    try:

        lat = request.args.get('lat')
        lng = request.args.get('lng')

        # look for the closest position as marker is not always precise
        trash_info = db.execute("SELECT ID, title, user_id_trash, report_date, latitude , longitude, "
                                " comment, user_id_clean, clean_date, clean_comment "
                                " FROM trash "
                                " ORDER BY ABS(latitude - ?), ABS(longitude - ?) "
                                " LIMIT 1", lat, lng)

        report_ID = trash_info[0]["ID"]
        session["reportID"] = report_ID

        user_name_trash = db.execute(
            "SELECT username FROM users WHERE ID = ?", trash_info[0]["user_id_trash"])
        user_name_clean = db.execute(
            "SELECT username FROM users WHERE ID = ?", trash_info[0]["user_id_clean"])

        info_trash = "trash"
        info_clean = "clean"

        # load trash images
        imgs_trash = db.execute("SELECT file_src, file_name "
                                " FROM img "
                                " WHERE info = ? AND reportID = ?", info_trash, report_ID)
        # load clean up images
        imgs_clean = db.execute("SELECT file_src, file_name "
                                " FROM img "
                                " WHERE info = ? AND reportID = ?", info_clean, report_ID)

        return render_template("clean.html", trash_info=trash_info, imgs_trash=imgs_trash, imgs_clean=imgs_clean, user_name_trash=user_name_trash, user_name_clean=user_name_clean)

    except Exception as e:
        return str(e)


# Route for reporting missuse or wrong files
@app.route("/report_report", methods=["GET"])
@login_required
def report_report():
    # TODO Include a proper reporting routine (maybe via mail or entry in DB)

    # read temp Id from session // ID from current position
    report_Id = session.get("reportID", None)
    # change status to temp remove from map
    status = "check"
    # update SQL database
    db.execute("UPDATE trash SET status = ? "
               " WHERE ID = ?", status, report_Id)

    flash("We will check this report and inform the other users! Thank you!", "success")
    return redirect("/")


# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    flash("Please login or register", "error")
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Please provide a username", "error")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Please provide a password", "error")
            return render_template("login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid username and/or password", "error")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["user_name"] = rows[0]["username"]
        flash("Welcome", "info")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    flash("Log out successful", "info")
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            flash("Please provide a username", "error")
            return render_template("register.html")

        # Ensure password was submitted
        elif not password:
            flash("Please provide a password", "error")
            return render_template("register.html")

        # Lets set some required password length for this (TODO: 4 is NOT secure but maybe enough for non private data)
        if len(password) < 4:
            flash("The password should be at least 4 character long", "error")
            return render_template("register.html")

        # Ensure password and confirmation match
        elif password != confirm_password:
            flash("The passwords do not match", "error")
            return render_template("register.html")

        # Ensure username does not already exist in database
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 0:
            flash("This username already exists", "error")
            return render_template("register.html")

        # Add username and password hash to database
        password_hash = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)",
                   username, password_hash)

        # Add confirmation if successful registration
        flash("Registration successful. Welcome!", "info")

        # Now that user exists Update rows again & remember the user has logged in
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        session["user_id"] = rows[0]["id"]
        session["user_name"] = username

        # Redirect user to home page
        return redirect("/")

        # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
