from ast import arg


ini = "id=1120198912&gender=female&class=07111905"
args = ini.split('&')
print(args)
student_id = args[0].split('=')[1]
student_gender = args[1].split('=')[1]
student_class = args[2].split('=')[1]



sql = "SELECT * from student where 1=1 "
if student_id != "":

    sql += "and id = " + "\"" + student_id + "\" " 

if student_gender != "":
    sql += "and gender = " + "\"" + student_gender + "\" " 

if student_class != "":
    sql += "and class = " + "\"" + student_class + "\" "  

sql += ";"

print(sql)