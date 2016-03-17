import os
from flask import Flask, render_template, request, redirect, url_for
from src.render_rfc import render_rfc


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

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
def render_rfc(rfc_number):
    filename = 'text/rfc{}.html'.format(rfc_number)
    rendered = render_rfc(filename)
    return render_template('rfc.html', rendered)

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


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
