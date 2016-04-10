import os
import time
import json
import datetime
from flask import (Flask, render_template, request, redirect,
                   url_for, make_response)
from src.render_rfc import render_html_rfc


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'should be set')

# Load RFC metadata file.
metadata = dict()
with open('metadata.json') as fd:
    metadata = json.load(fd)

###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    date = datetime.datetime.utcnow()
    return render_template('index.html', date=date)


###
# The functions below should be applicable to all Flask apps.
###

@app.route('/rfc<int:rfc_number>.html')
def render_text_rfc(rfc_number):
    start = time.time()

    title = 'RFC {}'.format(rfc_number)
    if rfc_number in metadata and metadata[rfc_number]['subject']:
        title = 'RFC {} - {}'.format(rfc_number, metadata[rfc_number]['subject'])

    filename = 'text/rfc{}.txt'.format(rfc_number)
    rendered = render_html_rfc(filename, metadata)
    rendered['title'] = title
    rendered['total_processing_time'] = start - time.time()

    return render_template('rfc.html', **rendered)


@app.route('/browse')
def list_rfc():
    titled_rfcs = []
    untitled_rfcs = []

    for rfc in metadata.values():
        if rfc.get('subject') is None:
            untitled_rfcs.append(rfc)
        else:
            titled_rfcs.append(rfc)

    sorted_titled_list = sorted(titled_rfcs, key=lambda x: x['rfc'], reverse=True)
    sorted_untitled_list = sorted(untitled_rfcs, key=lambda x: x['rfc'], reverse=True)
    return render_template('list.html',
                           titled_rfcs=sorted_titled_list,
                           untitled_rfc=sorted_untitled_list)


@app.route('/sitemap.xml')
def sitemap_view():
    """Render website's sitemap."""
    sitemap = render_template('sitemap.html', rfcs=metadata.values())

    # We need to set the content-type header correctly.
    response = make_response(sitemap)
    response.headers['Content-Type'] = 'application/xml'
    return response


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
