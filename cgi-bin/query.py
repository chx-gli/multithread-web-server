import sqlite3
import sys

ini = sys.argv[1]
hostname = sys.argv[2]
port = sys.argv[3]

ini = ini.split("&")

# 解析数据
student_id = ini[0].split("=")[1]
student_gender = ini[1].split("=")[1]
student_class = ini[2].split("=")[1]


db = sqlite3.connect('data\Student_data.db')
cursor = db.cursor()

sql = "SELECT * from student where 1=1 "
if student_id != "":

    sql += "and id = " + "\"" + student_id + "\" " 

if student_gender != "":
    sql += "and gender = " + "\"" + student_gender + "\" " 

if student_class != "":
    sql += "and class = " + "\"" + student_class + "\" "  

sql += ";"
cursor.execute(sql)

data = cursor.fetchall()

student_data = ''
for student in data:
    temp = "<tr >"
    temp += "<th scope=\"row\">" + str(student[0]) + "</th>"
    temp += "<td>" + student[1] + "</td>"
    temp += "<td>" + student[3] + "</td>"
    temp += "<td>" + student[2] + "</td>"
    temp += "</tr>\n"
    student_data += temp
res = f'''<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8" />
    <title>Student Data Query Result</title>
    <link rel="stylesheet" href="../css/bootstrap.min.css" />
    <link rel="stylesheet" href="../css/query.css" />
  </head>
  <body>
  <div class="container">
    <table class="table table-hover">
        <thead>
          <tr>
            <th scope="col">ID</th>
            <th scope="col">NAME</th>
            <th scope="col">GENDER</th>
            <th scope="col">CLASS</th>
          </tr>
        </thead>
        <tbody>
            {student_data}
        </tbody>
      </table>
    </div>
  </body>
  <script src="../js/bootstrap.bundle.min.js"></script>
</html>'''
print(res)
