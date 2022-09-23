import cgi

form = cgi.FieldStorage()
data_1 = form.getvalue('expr')
try:
    calculation_result = str(eval(data_1))
except Exception as e:
    calculation_result = str(type(e)) + str(e)

res = f'''
<!doctype html>
<html>
<head>
    <title>Calculation Result</title>
    <link rel="stylesheet" href="../css/bootstrap.min.css">
    <link rel="stylesheet" href="../css/pad.css">
</head>
<body>
<div class="container">
    <div class="pad">
    <div class="input-group">
        <span class="input-group-text">Result</span>
        <input class="form-control" type="text" name="expr" value="{calculation_result}">
        <a class="input-group-text btn btn-primary">Back!</a>
    </div>
</div>
</div>
<script src="../js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''
print(res)
