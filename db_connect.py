import mysql.connector

try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="verma2022",
        database="stucheck_db"
    )

    if connection.is_connected():
        print("✅ MySQL Database Connected Successfully!")

except mysql.connector.Error as e:
    print("❌ Database Connection Failed!")
    print("Error:", e)

finally:
    if 'connection' in locals() and connection.is_connected():
        connection.close()
        print("🔌 Connection Closed")