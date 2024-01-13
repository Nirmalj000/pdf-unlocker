from flask import Flask, render_template, request, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import io
import os
import pikepdf

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html', status_message="")

@app.route('/decrypt', methods=['POST'])
def decrypt():
    if 'file' not in request.files:
        return redirect(url_for('index', status_message=""))

    file = request.files['file']
    provided_password = request.form['password']
    correct_password = 'your_correct_password'  # Change this to your actual password

    if file.filename == '' or not allowed_file(file.filename):
        return redirect(url_for('index', status_message=""))

    try:
        # Store the file in memory
        file_content = io.BytesIO(file.read())
        file_content.seek(0)

        # Extract the original filename using secure_filename
        original_filename = secure_filename(file.filename)

        # Check if the provided password is correct
        if provided_password == correct_password:
            # Decrypt the PDF in memory
            pdf = pikepdf.Pdf.open(file_content, password=correct_password)
            decrypted_file_content = io.BytesIO()
            pdf.save(decrypted_file_content)
            decrypted_file_content.seek(0)

            # Send the decrypted file for download with the original filename
            return send_file(
                decrypted_file_content,
                as_attachment=True,
                download_name=f'{original_filename.replace(".pdf", "_unlocked.pdf")}',
                mimetype='application/pdf',
                add_etags=False
            )
        else:
            return render_template('index.html', status_message="Incorrect password. Please try again.")
    except Exception as e:
        error_message = f"Error: {str(e)}"
        return render_template('index.html', status_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)
