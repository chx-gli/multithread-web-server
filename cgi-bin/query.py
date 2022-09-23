# import pymysql
import sqlite3
import sys

ini = sys.argv[1]
hostname = sys.argv[2]
port = sys.argv[3]
# ini = ini.split("&")
student_id = ini.split("=")[1]
# student_name = ini[1].split("=")[1]
# student_class = ini[2].split("=")[1]
# value = " (" + student_id + ',"' + student_name + '","' + student_class + '")'

# db = pymysql.connect(host="localhost",
#                      user="root",
#                      password="123456",
#                      database="Student_data",
#                      charset='utf8')
# cursor = db.cursor()

db = sqlite3.connect('data\Student_data.db')
cursor = db.cursor()

sql = ""
if student_id == "000000":
    sql = "SELECT * from student;"
else:
    sql = "SELECT * from student where id = " + student_id +";"
cursor.execute(sql)

data = cursor.fetchall()
res = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Student Data</title>
</head>
<body>

    <table border="1">
        <caption>Student Data</caption>
        <tr>
            <th> ID </th>
            <th> NAME </th>
            <th> CLASS </th>
        </tr>
        $data
    </table>

</body>

</html>'''

student_data = ''
for student in data:
    temp = "<tr>"
    temp += "<th>" + str(student[0]) + "</th>"
    temp += "<th>" + student[1] + "</th>"
    temp += "<th>" + student[2] + "</th>"
    temp += "</tr>\n"
    student_data += temp
res = res.replace("$data", student_data)
print(res)
