import mysql.connector
from extract_details import extract_student_details
from ocr import extract_text


# Image path
image_path = "test.jpg.jpeg"


# Step 1: OCR
text = extract_text(image_path)


# Step 2: Extract student details
details = extract_student_details(text)


name = details.get("Name")
total_marks = details.get("Total Marks")
result = details.get("Result")


print("\n================================")
print("       STUCHECK AI")
print("  DOCUMENT VERIFICATION")
print("================================")

print("Student Name :", name)
print("Total Marks  :", total_marks)
print("Result       :", result)


# Step 3: Connect to MySQL
try:

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="verma2022",
        database="stucheck_db"
    )

    cursor = connection.cursor()

    # Step 4: Search student in database
    query = """
        SELECT name, total_marks, result
        FROM students
        WHERE UPPER(name) = UPPER(%s)
    """

    cursor.execute(query, (name,))

    student = cursor.fetchone()


    # Step 5: Verify
    if student:

        db_name, db_marks, db_result = student

        print("\nDatabase Match : FOUND")

        if (
            name.upper() == db_name.upper()
            and total_marks == db_marks
            and result.upper() == db_result.upper()
        ):

            print("\n================================")
            print("✅ DOCUMENT VERIFIED")
            print("================================")

        else:

            print("\n================================")
            print("❌ DOCUMENT NOT VERIFIED")
            print("Reason: Details mismatch")
            print("================================")

    else:

        print("\n================================")
        print("❌ DOCUMENT NOT VERIFIED")
        print("Reason: Student not found")
        print("================================")


except mysql.connector.Error as e:

    print("❌ Database Error:", e)


finally:

    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()