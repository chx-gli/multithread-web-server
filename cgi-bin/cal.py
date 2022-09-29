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
    <link rel="stylesheet" href="/css/bootstrap.min.css">
    <link rel="stylesheet" href="/css/pad.css">
</head>
<body>
<nav class="navbar navbar-expand-lg bg-light">
  <div class="container-fluid">
    <a href="/index.html" class="navbar-brand">
        <img src="/img/head.png" alt="BITLogo" style="width: 5rem">
        Python-based Multi-threaded Server
    </a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarSupportedContent">
      <ul class="navbar-nav me-auto">
            <li class="nav-item">
                <a class="nav-link" href="/cal.html">Calculator</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="/query.html">Database Query</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="/Team.html">Team</a>
            </li>
        </ul>
    </div>
  </div>
</nav>

<div class="container">
    <div class="pad">
    <div class="input-group">
        <span class="input-group-text">Result</span>
        <input class="form-control" type="text" name="expr" value="{calculation_result}">
        <a class="input-group-text btn btn-primary" onclick="window.history.go(-1);">Back!</a>
    </div>
</div>
</div>
<script src="/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''
with open('cgi-bin/cal.html', 'w') as f:
    print(res, file=f)
