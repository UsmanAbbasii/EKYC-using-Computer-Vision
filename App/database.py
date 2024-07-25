import mysql.connector
from datetime import datetime

def connect():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="qmobiles6s",
            database="cards"  
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            
            cursor = connection.cursor()
            cursor.execute("USE cards;")
            print("Selected database 'cards'")
            return connection
    except mysql.connector.Error as error:
        print(f"Error connecting to MySQL database: {error}")
        return None

def record_exists(connection, identity_number):
    try:
        cursor = connection.cursor()
        query = "SELECT * FROM id_card_data WHERE IdentityNumber = %s"
        cursor.execute(query, (identity_number,))
        result = cursor.fetchone()
        return result is not None
    except mysql.connector.Error as error:
        print(f"Error checking record existence: {error}")
        return False

def insert_record(connection, data):
    try:
        cursor = connection.cursor()

        # Convert date strings to datetime objects
        date_of_birth = datetime.strptime(data["Date of Birth"], "%d.%m.%Y").date()
        date_of_issue = datetime.strptime(data["Date of Issue"], "%d.%m.%Y").date()
        date_of_expiry = datetime.strptime(data["Date of Expiry"], "%d.%m.%Y").date()

        query = """
            INSERT INTO id_card_data (Name, FatherName, Gender, CountryOfStay,
                                      IdentityNumber, DateOfBirth, DateOfIssue, DateOfExpiry)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        record = (
            data["Name"], data["Father Name"], data["Gender"], data["Country of Stay"],
            data["Identity Number"], date_of_birth, date_of_issue, date_of_expiry
        )
        cursor.execute(query, record)
        connection.commit()
        print("Record inserted successfully.")
    except mysql.connector.Error as error:
        print(f"Error inserting record: {error}")
    except ValueError as v_error:
        print(f"Error converting date: {v_error}")

    finally:
        cursor.close()

def close_connection(connection):
    if connection:
        connection.close()
        print("MySQL connection closed.")

if __name__ == "__main__":
    connection = connect()
    close_connection(connection)
