import csv
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'university_db'
}

def init_database():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Student (
                student_id INT PRIMARY KEY,
                name VARCHAR(100),
                spi DECIMAL(3, 2),
                INDEX (spi)
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS CourseRegistration (
                student_id INT,
                course_id VARCHAR(20),
                PRIMARY KEY (student_id, course_id),
                FOREIGN KEY (student_id) REFERENCES Student(student_id),
                INDEX (course_id)
            );
        """)

        conn.commit()
        return conn, cursor
    except Error as e:
        print(f"Database Error: {e}")
        return None, None

def load_data(conn, cursor, student_csv, registration_csv):
    try:
        with open(student_csv, 'r') as f:
            reader = csv.DictReader(f)
            student_data = [(int(r['student_id']), r['name'], float(r['spi'])) for r in reader]
            cursor.executemany("""
                INSERT IGNORE INTO Student (student_id, name, spi)
                VALUES (%s, %s, %s)
            """, student_data)

        with open(registration_csv, 'r') as f:
            reader = csv.DictReader(f)
            reg_data = [(int(r['student_id']), r['course_id']) for r in reader]
            cursor.executemany("""
                INSERT IGNORE INTO CourseRegistration (student_id, course_id)
                VALUES (%s, %s)
            """, reg_data)

        conn.commit()
    except Exception as e:
        print(f"Data Insertion Error: {e}")

def run_query(cursor, course_id, spi_threshold):
    query = """
        SELECT s.student_id, s.name, s.spi, r.course_id
        FROM Student s
        INNER JOIN CourseRegistration r ON s.student_id = r.student_id
        WHERE r.course_id = %s AND s.spi > %s
        ORDER BY s.spi DESC, s.student_id ASC
    """
    cursor.execute(query, (course_id, spi_threshold))
    for row in cursor.fetchall():
        print(f"{row[0]} {row[1]} {row[2]} {row[3]}")

if __name__ == '__main__':
    conn, cursor = init_database()
    if conn and cursor:
        load_data(conn, cursor, 'student.csv', 'registration.csv')
        c_id = input("Enter course_id: ").strip()
        threshold = float(input("Enter spi_threshold: ").strip())
        run_query(cursor, c_id, threshold)
        cursor.close()
        conn.close()
