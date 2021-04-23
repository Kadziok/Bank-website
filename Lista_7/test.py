from flask import Flask
from werkzeug import serving
import ssl

app = Flask(__name__)

@app.route("/")
def main():
    return "Top-level content"

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.verify_mode = ssl.CERT_REQUIRED
context.load_verify_locations("certs/ca.cer")
context.load_cert_chain("certs/server.cer", "certs/server.key")
serving.run_simple("localhost", 8000, app, ssl_context=context)