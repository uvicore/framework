import uvicore
from ..services import bootstrap

# Bootstrap the Uvicore application
bootstrap.application(is_console=False)

# Http entrypoint for uvicorn or gunicorn
# uvicorn --port 5000 mreschke.wiki.http.server:http --reload
# gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:5000 mreschke.wiki.http.server:http
http = uvicore.app.http.server
