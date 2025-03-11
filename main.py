import sys
import logging
import flask
from template import TemplateEngine

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

app = flask.Flask(__name__)

template_engine = TemplateEngine()

@app.route("/")
def root():
    return template_engine.render("index", {})

if __name__ == "__main__":
    logger.info("Running AppEngine server locally")
    app.run(host="127.0.0.1", port=8080, debug=True)