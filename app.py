import os
import glob
from flask import Flask, render_template, request, redirect, url_for
from src.render_rfc import render_html_rfc


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'should be set')

###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('index.html')


###
# The functions below should be applicable to all Flask apps.
###

@app.route('/rfc<int:rfc_number>.html')
def render_text_rfc(rfc_number):
    filename = 'text/rfc{}.txt'.format(rfc_number)
    rendered = render_html_rfc(filename)
    return render_template('rfc.html', **rendered)

@app.route('/list')
def list_rfc():
    rfcs = [rfc[5:].split('.txt')[0] + '.html' for rfc in glob.glob('text/rfc*.txt')]
    return render_template('list.html', rfcs=rfcs)


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
