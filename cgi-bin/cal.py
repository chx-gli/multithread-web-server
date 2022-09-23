import cgi

form = cgi.FieldStorage()
data_1 = form.getvalue('expr')

response = f'''<!doctype html>
<html>
<head>
    <title>Document</title>
    <link rel="stylesheet" href="../css/bootstrap.min.css">
    <link rel="stylesheet" href="../css/pad.css">
</head>
<body>
<div class="container">
    <div class="pad">
    <div class="input-group">
        <span class="input-group-text">Result</span>
        <input class="form-control" type="text" name="expr" value="">
        <a class="input-group-text btn btn-primary">Back!</a>
    </div>
</div>
</div>
<script src="../js/bootstrap.bundle.min.js"></script>
</body>
</html>'''

print(response)
