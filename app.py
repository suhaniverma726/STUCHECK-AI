from flask import Flask, render_template, request
import os
import mysql.connector

from werkzeug.utils import secure_filename

from ocr import extract_text
from extract_details import extract_student_details


app = Flask(__name__)


# ==========================================
# Upload Configuration
# ==========================================

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Maximum upload size = 5 MB
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ==========================================
# Allowed File Extensions
# ==========================================

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg"
}


def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# ==========================================
# Home Route
# ==========================================

@app.route("/", methods=["GET", "POST"])
def home():

    result = None

    if request.method == "POST":

        # ==================================
        # Get Uploaded Document
        # ==================================

        file = request.files.get("document")


        # ==================================
        # Check File
        # ==================================

        if not file or file.filename == "":

            result = {
                "status": "ERROR",
                "message": "Please select a document."
            }

            return render_template(
                "index.html",
                result=result
            )


        # ==================================
        # Check File Extension
        # ==================================

        if not allowed_file(file.filename):

            result = {
                "status": "ERROR",
                "message": "Invalid file type. Please upload JPG, JPEG or PNG."
            }

            return render_template(
                "index.html",
                result=result
            )


        # ==================================
        # Secure Filename
        # ==================================

        filename = secure_filename(file.filename)


        # Prevent empty filename after sanitization
        if not filename:

            result = {
                "status": "ERROR",
                "message": "Invalid filename."
            }

            return render_template(
                "index.html",
                result=result
            )


        # ==================================
        # Save File
        # ==================================

        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(file_path)


        connection = None
        cursor = None


        try:

            # ==================================
            # STEP 1: OCR
            # ==================================

            text = extract_text(file_path)


            # ==================================
            # Check OCR Output
            # ==================================

            if not text or not text.strip():

                result = {
                    "status": "ERROR",
                    "message": "Unable to extract text from the document."
                }

                return render_template(
                    "index.html",
                    result=result
                )


            # ==================================
            # STEP 2: Extract Student Details
            # ==================================

            details = extract_student_details(text)


            name = details.get("Name")

            certificate_no = details.get(
                "Certificate Number"
            )

            total_marks = details.get(
                "Total Marks"
            )

            student_result = details.get(
                "Result"
            )


            # ==================================
            # STEP 3: MySQL Connection
            # ==================================

            connection = mysql.connector.connect(

                host="localhost",

                user="root",

                password="verma2022",

                database="stucheck_db"
            )


            cursor = connection.cursor()


            # ==================================
            # STEP 4: Find Student
            # ==================================

            student = None


            if certificate_no:

                query = """
                    SELECT
                        name,
                        certificate_no,
                        total_marks,
                        result
                    FROM students
                    WHERE certificate_no = %s
                """

                cursor.execute(
                    query,
                    (certificate_no,)
                )

                student = cursor.fetchone()


            # ==================================
            # STEP 5: Default Comparison
            # ==================================

            name_match = False

            certificate_match = False

            marks_match = False

            result_match = False


            # ==================================
            # STEP 6: Compare Data
            # ==================================

            if student:

                db_name, db_certificate, db_marks, db_result = student


                # ------------------------------
                # Name Comparison
                # ------------------------------

                name_match = (

                    name is not None

                    and db_name is not None

                    and name.strip().upper()
                    == db_name.strip().upper()

                )


                # ------------------------------
                # Certificate Comparison
                # ------------------------------

                certificate_match = (

                    certificate_no is not None

                    and db_certificate is not None

                    and certificate_no.strip()
                    == str(db_certificate).strip()

                )


                # ------------------------------
                # Marks Comparison
                # ------------------------------

                marks_match = (

                    total_marks is not None

                    and db_marks is not None

                    and total_marks.strip()
                    == str(db_marks).strip()

                )


                # ------------------------------
                # Result Comparison
                # ------------------------------

                result_match = (

                    student_result is not None

                    and db_result is not None

                    and student_result.strip().upper()
                    == str(db_result).strip().upper()

                )


            # ==================================
            # STEP 7: Verification Score
            # ==================================

            matches = sum([

                name_match,

                certificate_match,

                marks_match,

                result_match

            ])


            score = int(

                (matches / 4) * 100

            )


            # ==================================
            # STEP 8: Final Verification
            # ==================================

            verified = (

                student is not None

                and name_match

                and certificate_match

                and marks_match

                and result_match

            )


            # ==================================
            # Close Database
            # ==================================

            cursor.close()

            connection.close()

            cursor = None

            connection = None


            # ==================================
            # STEP 9: Send Result to HTML
            # ==================================

            result = {

                "name": name,

                "certificate_no": certificate_no,

                "marks": total_marks,

                "student_result": student_result,


                "name_match": name_match,

                "certificate_match": certificate_match,

                "marks_match": marks_match,

                "result_match": result_match,


                "score": score,

                "verified": verified

            }


        except Exception as e:


            # ==================================
            # Close Database on Error
            # ==================================

            if cursor:

                cursor.close()


            if connection:

                connection.close()


            result = {

                "status": "ERROR",

                "message": "An error occurred while processing the document."

            }


    return render_template(

        "index.html",

        result=result

    )


# ==========================================
# File Too Large Error
# ==========================================

@app.errorhandler(413)
def file_too_large(error):

    result = {

        "status": "ERROR",

        "message": "File is too large. Maximum allowed size is 5 MB."

    }

    return render_template(

        "index.html",

        result=result

    ), 413


# ==========================================
# Run Application
# ==========================================

if __name__ == "__main__":

    app.run(debug=True)