import csv
import os
from flask import Flask, flash, request, redirect, url_for
from twilio.rest import TwilioRestClient
from werkzeug.utils import secure_filename

# put your own credentials here
TWILIO_ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
TWILIO_FROM_NUMBER = os.environ['TWILIO_FROM_NUMBER']

UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
       filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def bulk_send_sms(filepath):
    client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    with open(filepath, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            date, name, phone_number, message = row
            message = message.rstrip()
            res = client.messages.create(
                to = phone_number,
                from_ = TWILIO_FROM_NUMBER,
                body = message,
            )
            print(res)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
          filename = secure_filename(file.filename)
          filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
          file.save(filepath)
          bulk_send_sms(filepath)
          return redirect(request.url)
    return '''
    <!doctype html>
    <title>Upload new CSV</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''