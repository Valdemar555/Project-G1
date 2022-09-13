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
import pathlib as pl
import os
from sqlalchemy.orm import sessionmaker
from werkzeug.utils import secure_filename
import check
from models import Person, Phones, Address, Files, create_db
import itertools

create_db()
UPLOAD_FOLDER = "D:\\учеба\\goit-python\\Python_web\\team\\contacts\\uploads"
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
        audio = bool(request.form.get('audio'))
        archives = bool(request.form.get('archives'))
        images = bool(request.form.get('images'))
        video = bool(request.form.get('video'))
        documents = bool(request.form.get('documents'))
        all = bool(request.form.get('all'))
        list_of_all_files=[]

        if all:
            for file in files_all:
                list_of_all_files.append(["All files", file])
        else: 
            for file in files_all:
                if  audio and  file.file_extension.upper() in  LIST_OF_AUDIO_SUFFIX:
                    list_of_all_files.append(["audio", file])
                if  archives and  file.file_extension.upper() in  LIST_OF_ARCHIVES_SUFFIX:
                    list_of_all_files.append(["archives", file])
                if  images and  file.file_extension.upper() in  LIST_OF_IMAGES_SUFFIX:
                    list_of_all_files.append(["images", file])
                if  video and  file.file_extension.upper() in  LIST_OF_VIDEO_SUFFIX:
                    list_of_all_files.append(["video", file])
                if  documents and  file.file_extension.upper() in  LIST_OF_DOCUMENTS_SUFFIX:
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
    for person_birthday in persons_with_birthday:
        if person_birthday.birthday:
            happy_birthday = datetime(
                year=current_time.year,
                month=person_birthday.birthday.month,
                day=person_birthday.birthday.day,
            )
            if happy_birthday.month > current_time.month:
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
        
        #check birthday
        raw_birthday = request.form.get("birthday")
        
        person_birthday=raw_birthday
        #check phones
        raw_phone = request.form.get("phones")

        
        #check emails
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
                    phone=check.PhoneParser()
                    phone.string = raw_phone
                    person_phone = phone.parse_string()
                    if person.phones:                    
                        person.phones.append(Phones(phone=person_phone))
                    if not person.phones:
                        person.phones = [(Phones(phone=person_phone))]

                if raw_email:
                    email=check.EmailParser()
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
                phone=check.PhoneParser()
                phone.string = raw_phone
                person_phone = phone.parse_string()                
                person.phones.append(Phones(phone=person_phone))                
                session.add(person)

            if raw_email:
                email=check.EmailParser()
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
    if request.method == "POST" and int(person_id):
        path = pl.Path(UPLOAD_FOLDER)
        if not path.exists():
            os.mkdir(UPLOAD_FOLDER)

        if "file" not in request.files:
            flash("Не могу прочитать файл")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("Нет выбранного файла")
            return redirect(request.url)
        if file and allowed_file(file.filename):            
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            person = session.query(Person).filter(Person.id == person_id).first()
            if person.data:
                person.data.append(
                    Files(
                        file_name=file.filename.rsplit(".", 1)[0].lower(),
                        file_extension=file.filename.rsplit(".", 1)[1].lower(),
                        file_storage_path=UPLOAD_FOLDER,
                    )
                )
            if not person.data:
                person.data = [
                    (
                        Files(
                            file_name=file.filename.rsplit(".", 1)[0].lower(),
                            file_extension=file.filename.rsplit(".", 1)[1].lower(),
                            file_storage_path=UPLOAD_FOLDER,
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


@app.route("/download_file/<name>")
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)


@app.route("/contact-delete/<id>", strict_slashes=False)
def delete(id):
    session.query(Person).filter(Person.id == id).delete()
    session.commit()
    return redirect("/")


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


if __name__ == "__main__":
    app.secret_key = "super secret key"
    # app.config['SESSION_TYPE'] = "filesystem"
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.debug = True
    app.env = "development"
    app.run()
