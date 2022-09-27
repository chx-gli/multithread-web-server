import sqlite3
import sys

ini = sys.argv[1]
# hostname = sys.argv[2]
# port = sys.argv[3]

ini = ini.split("&")

# 解析数据
student_id = ini[0].split("=")[1]
student_gender = ini[1].split("=")[1]
student_class = ini[2].split("=")[1]


db = sqlite3.connect('data/Student_data.db')
cursor = db.cursor()

sql = "select * from student where 1=1 "
if student_id != "":
    sql += f"and id = \"{student_id}\" "
if student_gender != "":
    sql += f"and gender = \"{student_gender}\" "
if student_class != "":
    sql += f"and class = \"{student_class}\""

sql += ";"
cursor.execute(sql)

data = cursor.fetchall()

student_data = ''
for student in data:
    student_data += f'<tr>' \
                    f'    <th scope="row">{student[0]}</th>' \
                    f'    <td>{student[1]}</td>' \
                    f'    <td>{student[2]}</td>' \
                    f'    <td>{student[3]}</td>' \
                    f'</tr>\n'
res = f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8"/>
    <title>Student Data Query Result</title>
    <link rel="stylesheet" href="../css/bootstrap.min.css"/>
    <link rel="stylesheet" href="../css/query.css"/>
</head>
<body>
<nav class="navbar navbar-expand-lg bg-light">
    <div class="container-fluid">
        <a href="index.html" class="navbar-brand">Python-based Multi-threaded Server</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent"
                aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarSupportedContent">
            <ul class="navbar-nav me-auto">
                <li class="nav-item">
                    <a class="nav-link" href="cal.html">Calculator</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="query.html">Database Query</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="about.html">About</a>
                </li>
            </ul>
        </div>
    </div>
</nav>

<div class="container">
    <table class="table table-hover">
        <thead>
        <tr>
            <th scope="col">ID</th>
            <th scope="col">NAME</th>
            <th scope="col">CLASS</th>
            <th scope="col">GENDER</th>
        </tr>
        </thead>
        <tbody>
        {student_data}
        </tbody>
    </table>
</div>
</body>
<script src="../js/bootstrap.bundle.min.js"></script>
</html>
'''
print(res)

cursor.close()
