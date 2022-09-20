from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from datetime import datetime
from sqlalchemy import create_engine
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    flash,
    send_from_directory,
)
from flask_docs import ApiDoc
import pathlib as pl
import os
from sqlalchemy.orm import sessionmaker
from werkzeug.utils import secure_filename
import check
from models import Person, Phones, Address, Files, Note, Tag, GoogleFiles, create_db
import itertools


FOLDER_ID = ""
directory = "uploads"
current_path = os.getcwd()
ful_path = os.path.abspath(os.path.join(current_path, os.pardir))
UPLOAD_FOLDER = os.path.abspath(os.path.join(ful_path, directory))
LIST_OF_AUDIO_SUFFIX = ["MP3", "OGG", "WAV", "AMR"]
LIST_OF_ARCHIVES_SUFFIX = ["ZIP", "GZ", "TAR"]
LIST_OF_IMAGES_SUFFIX = ["JPEG", "PNG", "JPG", "SVG"]
LIST_OF_VIDEO_SUFFIX = ["AVI", "MP4", "MOV", "MKV"]
LIST_OF_DOCUMENTS_SUFFIX = ["DOC", "DOCX", "TXT", "PDF", "XLSX", "PPTX"]


ALLOWED_EXTENSIONS = list(
    itertools.chain(
        LIST_OF_IMAGES_SUFFIX,
        LIST_OF_VIDEO_SUFFIX,
        LIST_OF_DOCUMENTS_SUFFIX,
        LIST_OF_AUDIO_SUFFIX,
        LIST_OF_ARCHIVES_SUFFIX,
    )
)

create_db()
gauth = GoogleAuth()
gauth.LoadCredentialsFile("mycreds.txt")
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()
# Save the current credentials to a file
gauth.SaveCredentialsFile("mycreds.txt")


engine = create_engine(
    "sqlite:///contacts.db", connect_args={"check_same_thread": False}
)
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)


@app.route("/files/<id>", methods=["POST", "GET"], strict_slashes=False)
@app.route("/files_show/<id>", methods=["GET"], strict_slashes=False)
def files(id):
    if request.method == "POST":
        files_all = session.query(Files).filter(Files.person_id == id).all()
        audio = bool(request.form.get("audio"))
        archives = bool(request.form.get("archives"))
        images = bool(request.form.get("images"))
        video = bool(request.form.get("video"))
        documents = bool(request.form.get("documents"))
        all = bool(request.form.get("all"))
        list_of_all_files = []

        if all:
            for file in files_all:
                list_of_all_files.append(["All files", file])
        else:
            for file in files_all:
                if audio and file.file_extension.upper() in LIST_OF_AUDIO_SUFFIX:
                    list_of_all_files.append(["audio", file])
                if archives and file.file_extension.upper() in LIST_OF_ARCHIVES_SUFFIX:
                    list_of_all_files.append(["archives", file])
                if images and file.file_extension.upper() in LIST_OF_IMAGES_SUFFIX:
                    list_of_all_files.append(["images", file])
                if video and file.file_extension.upper() in LIST_OF_VIDEO_SUFFIX:
                    list_of_all_files.append(["video", file])
                if (
                    documents
                    and file.file_extension.upper() in LIST_OF_DOCUMENTS_SUFFIX
                ):
                    list_of_all_files.append(["documents", file])
        list_of_all_files = sorted(list_of_all_files, key=lambda days: days[0])
        # return render_template("contact-details.html", person=person)
        return render_template("files.html", files=list_of_all_files)
    if request.method == "GET":
        return render_template("files.html")


# contact contact details page
@app.route("/contacts", methods=["POST"], strict_slashes=False)
@app.route("/contact-details/", methods=["GET"], strict_slashes=False)
# find contact
def finding_contacts():
    if request.method == "POST":
        finding_name = request.form.get("find_name")
        finding_file_name = request.form.get("find_file")
        person_list = []
        files_list = []

        if finding_name:
            for person in session.query(Person).all():
                if finding_name in person.name:
                    person_list.append(person)

        if finding_file_name:
            for file in session.query(Files).all():
                if finding_file_name in file.file_name:
                    files_list.append(file)

        if person_list and not files_list:
            return render_template("contacts.html", persons=person_list)

        if files_list and not person_list:
            return render_template("contacts.html", information_name=files_list)

        if finding_name and not person_list:
            return render_template(
                "contacts.html",
                information_name_warning=f"Sorry no {finding_name} in persons name",
            )

        if finding_file_name and not files_list:
            return render_template(
                "contacts.html",
                information_name_warning=f"Sorry no {finding_file_name} in persons files",
            )

        if files_list and person_list:
            return render_template(
                "contacts.html", persons=person_list, information_name=files_list
            )
        if not finding_file_name and not finding_name:
            return render_template("contacts.html")


@app.route("/birthday", methods=["GET"], strict_slashes=False)
def days_to_birthday():
    persons_with_birthday = session.query(Person).all()
    current_time = datetime.now()
    list_of_contacts_with_birthday = []
    if persons_with_birthday:
        for person_birthday in persons_with_birthday:
            if person_birthday.birthday:
                happy_birthday = datetime(
                    year=current_time.year,
                    month=person_birthday.birthday.month,
                    day=person_birthday.birthday.day,
                )
                if happy_birthday.month >= current_time.month:
                    days_to_birthday = happy_birthday - current_time
                    a = days_to_birthday.days
                    list_of_contacts_with_birthday.append(
                        [person_birthday.name, a, person_birthday.id]
                    )
                else:
                    days_to_birthday = current_time - happy_birthday
                    b = 365 - days_to_birthday.days
                    list_of_contacts_with_birthday.append(
                        [person_birthday.name, b, person_birthday.id]
                    )
            sorted_list = sorted(
                list_of_contacts_with_birthday, key=lambda days: days[1]
            )
        return render_template("birthday.html", persons=sorted_list)
    else:
        return render_template("birthday.html")


# contact index page
@app.route("/contacts", methods=["GET"], strict_slashes=False)
# all contacts showing
def showing_contacts():
    if request.method == "GET":
        persons = session.query(Person).all()
        if persons:
            return render_template(
                "contacts.html", persons=persons, information_name=None
            )
        else:
            return render_template("contacts.html")


# information about contact details
# @app.route("/contact-details/<id>", strict_slashes=False)
@app.route("/contact-information/<person_id>", methods=["GET"], strict_slashes=False)
def contacts(person_id):
    person = session.query(Person).filter(Person.id == person_id).first()
    # return render_template("contact-details.html", person=person)
    return render_template("contact-information_.html", person=person)


# contact adding
@app.route("/contact-information/", methods=["GET", "POST"], strict_slashes=False)
@app.route("/contact-information/<id>", methods=["GET", "POST"], strict_slashes=False)
# adding person and details
def add_person_and_details():
    excist = 0
    if request.method == "POST":
        person_name = request.form.get("name")

        # check birthday
        raw_birthday = request.form.get("birthday")

        person_birthday = raw_birthday
        # check phones
        raw_phone = request.form.get("phones")

        # check emails
        raw_email = request.form.get("email")

        person_country = request.form.get("country")
        person_city = request.form.get("city")
        person_street = request.form.get("street")
        person_building_number = request.form.get("building_number")
        person_flat_number = request.form.get("flat_number")

        for person in session.query(Person).all():

            if str(person_name) == str(person.name):
                excist = 1

                if person_birthday:
                    dt_birthday = datetime(
                        year=int(person_birthday[0:4]),
                        month=int(person_birthday[4:6]),
                        day=int(person_birthday[6:]),
                    ).date()
                    person.birthday = dt_birthday

                if raw_phone:
                    phone = check.PhoneParser()
                    phone.string = raw_phone
                    person_phone = phone.parse_string()
                    if person.phones:
                        person.phones.append(Phones(phone=person_phone))
                    if not person.phones:
                        person.phones = [(Phones(phone=person_phone))]

                if raw_email:
                    email = check.EmailParser()
                    email.string = raw_email
                    person_email = email.parse_string()
                    person.email = person_email

                if (
                    person_country
                    or person_city
                    or person_street
                    or person_building_number
                    or person_flat_number
                ):
                    current_address = (
                        session.query(Address)
                        .filter(Address.person_id == person.id)
                        .first()
                    )
                    if not current_address:
                        adddress = Address(
                            country=person_country,
                            city=person_city,
                            street=person_street,
                            building_number=person_building_number,
                            flat_number=person_flat_number,
                        )
                        person.address.append(adddress)
                        session.add(person)
                        session.commit()
                    else:
                        if person_country:
                            current_address.country = person_country
                        if person_city:
                            current_address.city = person_city
                        if person_street:
                            current_address.street = person_street
                        if person_building_number:
                            current_address.building_number = person_building_number
                        if person_flat_number:
                            current_address.flat_number = person_flat_number
                        session.add(current_address)
                        session.commit()

        if excist == 0:
            person = Person(name=person_name)
            session.add(person)
            if person_birthday:
                dt_birthday = datetime(
                    year=int(person_birthday[0:4]),
                    month=int(person_birthday[4:6]),
                    day=int(person_birthday[6:]),
                ).date()
                person.birthday = dt_birthday
                session.add(person)

            if raw_phone:
                phone = check.PhoneParser()
                phone.string = raw_phone
                person_phone = phone.parse_string()
                person.phones.append(Phones(phone=person_phone))
                session.add(person)

            if raw_email:
                email = check.EmailParser()
                email.string = raw_email
                person_email = email.parse_string()
                person.email = person_email

            if (
                person_country
                or person_city
                or person_street
                or person_building_number
                or person_flat_number
            ):
                adddress = Address(
                    country=person_country,
                    city=person_city,
                    street=person_street,
                    building_number=person_building_number,
                    flat_number=person_flat_number,
                )
                person.address.append(adddress)
            session.add(person)
            session.commit()

        return redirect("/contacts")
    if request.method == "GET":

        return render_template("contact-information_.html", person=None)


def allowed_file(filename):
    """Функция проверки расширения файла"""
    return "." in filename and filename.rsplit(".", 1)[1].upper() in ALLOWED_EXTENSIONS


@app.route("/uploads/<person_id>", methods=["GET", "POST"], strict_slashes=False)
# adding person and details
def upload_file(person_id):
    person_data = session.query(Person).filter(Person.id == person_id).first()
    drive = GoogleDrive(gauth)
    if not person_data.folder_id:
        folder_metadata = {
            "title": f"{person_id}uploads",
            "mimeType": "application/vnd.google-apps.folder",
        }
        folder = drive.CreateFile(folder_metadata)
        folder.Upload()
        folderlist = drive.ListFile(
            {"q": "mimeType='application/vnd.google-apps.folder' and trashed=false"}
        ).GetList()
        titlelist = [x["title"] for x in folderlist]
        # print(person_id)
        # print(folderlist)
        # print(titlelist)
        if f"{person_id}uploads" in titlelist:
            for item in folderlist:
                if str(item["title"]) == f"{person_id}uploads":
                    person_data.folder_id = item["id"]
                    session.add(person_data)
                    session.commit()
    if request.method == "POST" and int(person_id):
        path = pl.Path(UPLOAD_FOLDER)
        if not path.exists():
            os.mkdir(path)
        user_path = pl.Path(os.path.join(UPLOAD_FOLDER, f"{person_id}uploads"))
        if not user_path.exists():
            os.mkdir(user_path)

        if "file" not in request.files:
            flash("Не могу прочитать файл")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("Нет выбранного файла")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(user_path, filename))
            person = session.query(Person).filter(Person.id == person_id).first()
            drive = GoogleDrive(gauth)
            folder_metadata = {
                "title": user_path,
                "mimeType": "application/vnd.google-apps.folder",
            }
            folder = drive.CreateFile(folder_metadata)
            gfile = drive.CreateFile(
                {"parents": [{"kind": "drive#fileLink", "id": person.folder_id}]}
            )
            realpath = os.getcwd()
            os.chdir(user_path)
            gfile.SetContentFile(f"{filename}")
            gfile.Upload()
            os.chdir(realpath)            
            if person.data:
                person.data.append(
                    Files(
                        file_name=file.filename.rsplit(".", 1)[0].lower(),
                        file_extension=file.filename.rsplit(".", 1)[1].lower(),
                        file_storage_path=str(user_path),
                    )
                )

            if not person.data:
                fileList = drive.ListFile({"q": f"'{person.folder_id}' in parents and trashed=false"}).GetList()
                person.data = [
                    (
                        Files(
                            file_name=file.filename.rsplit(".", 1)[0].lower(),
                            file_extension=file.filename.rsplit(".", 1)[1].lower(),
                            file_storage_path=str(user_path),
                        )
                    )
                ]
            if person.google_data:
                fileList = drive.ListFile({"q": f"'{person.folder_id}' in parents and trashed=false"}).GetList()
                for files in fileList:
                    if files["title"] == f"{file.filename}":
                        fileID1 = files["id"]
                        person.google_data.append(
                            GoogleFiles(
                                file_name=file.filename.rsplit(".", 1)[0].lower(),
                                file_extension=file.filename.rsplit(".", 1)[1].lower(),
                                file_id=fileID1,
                            )
                        )
            if not person.google_data:
                for files in fileList:
                    if files["title"] == f"{file.filename}":
                        fileID2 = files["id"]
                        person.google_data = [
                            (
                                GoogleFiles(
                                    file_name=file.filename.rsplit(".", 1)[0].lower(),
                                    file_extension=file.filename.rsplit(".", 1)[1].lower(),
                                    file_id=fileID2,
                                )
                            )
                        ]

            session.add(person)
            session.commit()
            return redirect("/contacts")

        if file and not allowed_file(file.filename):
            return "Расширение не поддерживается"
    return """
    <!doctype html>
    <title>Загрузить новый файл</title>
    <h1>Загрузить новый файл</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    </html>
    """


@app.route("/download_file/<file_id>")
def download_file(file_id):
    file = session.query(Files).filter(Files.id == file_id).first()
    return send_from_directory(file.file_storage_path, f"{file.file_name}.{file.file_extension}")


@app.route("/contact-delete/<id>", strict_slashes=False)
def delete(id):
    session.query(Person).filter(Person.id == id).delete()
    session.commit()
    return redirect("/contacts")


@app.route("/phone-delete/<id>", strict_slashes=False)
def delete_phone(id):
    session.query(Phones).filter(Phones.id == id).delete()
    session.commit()
    return redirect("/contacts")


@app.route("/phones/<id>", methods=["GET", "POST"], strict_slashes=False)
def edit_phone(id):

    if request.method == "POST":
        old_phone = session.query(Phones).filter(Phones.id == id).first()
        new_phone = request.form.get("new_phone")
        old_phone.phone = int(new_phone)
        session.add(old_phone)
        session.commit()
        return redirect("/contacts")

    else:
        old_phone = session.query(Phones).filter(Phones.id == id).first()
        return render_template("phones.html", phone=old_phone.phone)

@app.route('/note-information', strict_slashes=False)
def index_note():
    notes = session.query(Note).all()
    
    return render_template('note-information.html', notes=notes)

@app.route("/delete/note/<id>", strict_slashes=False)
def delete_note(id):
    session.query(Note).filter(Note.id == id).delete()
    session.commit()

    return redirect("/note-information")

@app.route("/done/<id>", strict_slashes=False)
def done(id):
    session.query(Note).filter(Note.id == id).first().done = True
    session.commit()
    return redirect("/note-information")

@app.route("/note/", methods=["GET", "POST"], strict_slashes=False)
def add_note():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        tags = request.form.getlist("tags")
        tags_obj = []
        for tag in tags:
            tags_obj.append(session.query(Tag).filter(Tag.name == tag).first())
        note = Note(name=name, description=description, tags=tags_obj)
        session.add(note)
        session.commit()
        return redirect("/note-information")
    else:
        tags = session.query(Tag).all()

    return render_template("note.html", tags=tags)


@app.route("/tag/", methods=["GET", "POST"], strict_slashes=False)
def add_tag():
    if request.method == "POST":
        name = request.form.get("name")
        tag = Tag(name=name)
        session.add(tag)
        session.commit()
        return redirect("/note-information")

    return render_template("tag.html")

@app.route('/edit-note/<note_id>', methods=['GET', 'POST'], strict_slashes=False)
def note_edit(note_id):
    old_note = session.query(Note).filter(Note.id == note_id).first()
    if request.method == "POST":
        new_name = request.form.get("name")
        description = request.form.get("description")
        tags = request.form.getlist("tags")
        tags_obj = []
        for tag in tags:
            tags_obj.append(session.query(Tag).filter(Tag.name == tag).first())
        old_note.name = new_name
        old_note.description = description
        old_note.tags = tags_obj
        session.add(old_note)
        session.commit()
        return render_template('note-information.html')
    else:
        tags1 = session.query(Tag).all()

        return render_template('edit-note.html', tags=tags1)

@app.route("/find-note", methods=["POST","GET"], strict_slashes=False)
@app.route("/note-detalis/", methods=["GET"], strict_slashes=False)
# find note
def finding_notes():
    if request.method == "POST":
        finding_note = request.form.get("find_note")
        finding_tag_name = request.form.get("find_tag")
        note_list = []
        tag_list = []
        if finding_note:
            for notes in session.query(Note).all():
                if finding_note in notes.name:
                    note_list.append(notes)
        if finding_tag_name:
            for tag in session.query(Tag).all():
                if finding_tag_name in tag.name:
                    tag_list.append(tag)
        if note_list and not tag_list:
            return render_template("find-note.html", info_note=note_list)
        if tag_list and not note_list:
            return render_template("find-note.html", info_tag=tag_list)
        if finding_note and not tag_list:
            return render_template(
                "find-note.html",
                information=f"Sorry no {finding_note} in notes name",
            )
        if finding_tag_name and not note_list:
            return render_template(
                "find-note.html",
                information=f"Sorry no {finding_tag_name} in tags",
            )
        if tag_list and note_list:
            return render_template(
                "find-note.html", info_note=note_list, info_tag=tag_list
            )
        if not finding_tag_name and not finding_note:
            return render_template("find-note.html")
    if request.method == "GET":
        return render_template("note-detalis.html")        
    
if __name__ == "__main__":
    app.secret_key = "super secret key"
    # app.config['SESSION_TYPE'] = "filesystem"
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.debug = True
    app.env = "development"
    app.run()
