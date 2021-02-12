#from uvicore.http.routing import WebRouter
from uvicore.http import Request, response, WebRouter
from uvicore.support.dumper import dd, dump

route = WebRouter()

# If no name like 'about' is defined, the path is used

@route.get('/rapidoc')
async def about(request: Request):
    return response.HTML("""
<!doctype html> <!-- Important: must specify -->
<html>
<head>
  <meta charset="utf-8"> <!-- Important: rapi-doc uses utf8 charecters -->
  <script type="module" src="https://unpkg.com/rapidoc/dist/rapidoc-min.js"></script>
</head>
<body>
  <rapi-doc spec-url = "http://localhost:5000/openapi.json"> </rapi-doc>
</body>
</html>
""")
