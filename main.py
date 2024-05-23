from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from prettytable import PrettyTable
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)

def send_email(recoi, name, percent):
    sender_email = "1rn21cs037.ayushpratap@gmail.com"
    password = "qbvc adqj ejlb slgm"  
    subject = "Attendance Warning"
    message = f"Dear {name},\n\nYour attendance is below 60% which is {percent}%.\nPlease attend classes regularly to improve your attendance.\n\nSincerely,\nThe Attendance System"

    try:
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recoi
        msg['Subject'] = subject

        
        msg.attach(MIMEText(message, 'plain'))

        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            text = msg.as_string()
            server.sendmail(sender_email, recoi, text)
            print(f"Email sent to {recoi}")
    except Exception as e:
        print(f"Error: {e}")

@app.route('/')
def index():
    return render_template('index.html')
   

@app.route('/add_student', methods=['POST'])
def add_student():
    if request.method == 'POST':
        usn = request.form['usn']
        namee = request.form['namee']
        email = request.form['email']
        classattended = request.form['classattended']

        try:
            mydb = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password="Rajawat@5776",
                database="attendance"
            )
            mycursor = mydb.cursor()
            
            sql = "INSERT INTO stdet (usn, namee, email, clasattended) VALUES (%s, %s, %s, %s)"
            val = (usn, namee, email, classattended)
            mycursor.execute(sql, val)
            mycursor.execute("UPDATE stdet SET attper = (clasattended*100)/60")
            mydb.commit()
            mydb.close()

            return redirect(url_for('show_shortage_students'))
        except Exception as e:
            print(f"Error: {e}")
            return "An error occurred while adding the student."

@app.route('/show_shortage_students')
def show_shortage_students():
    try:
        mydb = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="Rajawat@5776",
            database="attendance"
        )
        mycursor = mydb.cursor()

        sql = "SELECT * FROM stdet WHERE attper <= 60;"
        mycursor.execute(sql)
        results = mycursor.fetchall()

        table = PrettyTable()
        table.field_names = [desc[0] for desc in mycursor.description]

        shortage_students = []
        for row in results:
            table.add_row(row)
            shortage_students.append(row)

        print(table) 
        
        mydb.close()

        return render_template('shortage_students.html', shortage_students=shortage_students)
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while fetching shortage students."

@app.route('/send_email_to_shortage_students')
def send_email_to_shortage_students():
    try:
        mydb = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="Rajawat@5776",
            database="attendance"
        )
        mycursor = mydb.cursor()

        sql = "SELECT namee, email, attper FROM stdet WHERE attper <= 60;"
        mycursor.execute(sql)
        ret = mycursor.fetchall()

        for i in ret:
            send_email(i[1], i[0], i[2])

        mydb.close()

        return "Emails sent successfully!"
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while sending emails."

if __name__ == '__main__':
    app.run(debug=True)