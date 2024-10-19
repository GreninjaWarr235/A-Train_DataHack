from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# Create an 'uploads' folder to store the uploaded CSV files
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Set upload folder in Flask app
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions (only CSV)
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Home route to display the form
@app.route('/')
def index():
    return render_template('index.html')

# Submit route to handle form data
@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        category = request.form.get('category')  # Get selected category from form

        if 'csv_files' not in request.files:
            return 'No file part in the form.'

        csv_files = request.files.getlist('csv_files')

        saved_files = []
        for file in csv_files:
            if file and allowed_file(file.filename):
                filename = file.filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)  # Save file to upload folder
                saved_files.append(filename)

        # You can add logic here to store `category` and `saved_files` in a database or do other processing.

        return f"Category: {category}, Files saved: {', '.join(saved_files)}"

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
