from flask import Flask, request, make_response, Response
import bleach
import nh3
from lxml.html.clean import Cleaner

app = Flask(__name__)

def plain_response(text: str) -> Response:
    response = make_response(text)
    response.headers["Content-Type"] = "text/plain"
    return response

@app.route('/bleach')
def bleach_route():
    text = request.args.get('text')
    if not text:
        return plain_response("No text given")
    tags = ['a', 'img', 'strong']
    attributes = {'*': ['href', 'src', 'alt']}
    sanitized_text = bleach.clean(text, tags=tags, attributes=attributes)
    return plain_response(sanitized_text)

@app.route('/nh3')
def nh3_route():
    text = request.args.get('text')
    if not text:
        return plain_response("No text given")
    sanitized_text = nh3.clean(text, tags={'a', 'img', 'strong'},attributes={'a': {'href'}, 'img': {'src', 'alt'}})
    return plain_response(sanitized_text)

@app.route('/lxml')
def lxml_route():
    text = request.args.get('text')
    if not text:
        return plain_response("No text given")
    cleaner = Cleaner(allow_tags=['a', 'img', 'strong'], safe_attrs_only=True, safe_attrs=set(['href', 'src', 'alt']))
    sanitized_text = cleaner.clean_html(text)
    return plain_response(sanitized_text)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
