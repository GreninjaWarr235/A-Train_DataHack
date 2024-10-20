import os
from flask import Flask, render_template, request, send_file
import tempfile
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve the API key from the environment variable
api_key = os.getenv("GEMINI_KEY")

# Configure the generative AI API with the API key
genai.configure(api_key=api_key)

app = Flask(__name__)

# Create an 'uploads' folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to evaluate insights from the first 20 rows
def evaluate_insights(df,category):
    insights = []
    
    # Prepare the data for LLM
    sample_data = df.head(20).to_csv(index=False)
    prompt = f"Here are the first 20 rows of the dataset:\n{sample_data}\n"
    prompt += f"Identify any issues based on the following criteria, the column names might be slightly differnet but understand the underlying meaning of the columns and then match them to the insight given below. the columns which I have given above, you only have those. You dont need to write everything, just write which insights match. Match only the insights which match dont write anything unnecessary. Dont write the insights which do not match. This is the category \n{category}\n. Do not write for any other category. Whichever problem you select write a solution for it too in 1 line below it. For each one write 1 solution :\n"
    prompt += """
    1. Red Aggregators: 
       a. Aggregators_Discount: > 15% Discount
       b. Delivery_Delay: Delivery time > 30 mins
       c. Cancelled Order: Order status == Cancelled
       d. Order Delay: Delivery time > 30 mins
       e. Prep Delay: Prep time > 30 mins

    2. Green Departments:
       a. Item Turn Around Time: Preparation_Time_Taken < 10 mins

    3. Red Departments:
       a. Department_wise_cost: (HOLD) [over costly]
       b. Long Preparation_Time - For Dine In: Preparation time > 60 mins

    4. Yellow Departments:
       a. Missing Recipes and item - (On Hold)

    5. Green Inventory:
       (Nhi samj raha hai/ Nothing)

    6. Orange Inventory:
       a. Department in Consumption: (Hold)
       b. Purchase in consumption: If [consumed_quantity/purchased_quantity] < 85% then Orange
       c. Quantity Change - On Hold

    7. Red Inventory:
       a. Double Order: More than 1 entry in entry_count column
       b. New_Vendor: Getting items from new vendor instead of old supplier
       c. Vendor_change: Higher price

    8. Sales:
       a. Bill Modifications: The bill amount is reduced
       b. Bill Settlement less than 30 seconds: bill is settled in less than 30 seconds
       c. Bill Settlement more than 15 minutes: bill is settled in more than 15 minutes
       d. Discount: Same staff is giving too much discount
       e. KOT Modification: Either too early or either too late
       f. Long Preparation Time: Preparation is long
       g. Cancelled Order: Order is cancelled
       h. Complimentary Bills: Status column is complimentary
       i. Due Payments: Multiple orders at the same time with duplicate invoice number and same staff
       j. No Name, No number, No Covers, No Feedback: name justify itself
    """
    
    # Use Gemini API to check for insights
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    
    # Extract the insights from the response
    candidates = response.candidates
    if candidates:
        insights = candidates[0].content.parts[0].text.splitlines()
    else:
        insights.append("No insights were generated.")
    
    return insights

# Generate the next suggestion ID based on the feedback file
def get_next_suggestion_id(feedback_file='feedback.csv'):
    if os.path.isfile(feedback_file):
        feedback_df = pd.read_csv(feedback_file)
        if 'Suggestion_ID' in feedback_df.columns and not feedback_df.empty:
            last_id = feedback_df['Suggestion_ID'].max()
            return last_id + 1
    return 1

# Save feedback to a CSV file
def save_feedback(suggestion_id, rating, comment, feedback_file='feedback.csv'):
    file_exists = os.path.isfile(feedback_file)

    feedback_df = pd.DataFrame([[suggestion_id, rating, comment]], columns=['Suggestion_ID', 'Rating', 'Comment'])

    feedback_df.to_csv(feedback_file, mode='a', header=not file_exists, index=False)


# Submit route to handle uploaded CSV files
@app.route('/submit', methods=['POST'])
def submit():
    if 'csv_files' not in request.files:
        return 'No file part in the form.'
    category = request.form.get('category')
    csv_files = request.files.getlist('csv_files')

    # Initialize insights in a temporary file
    temp_file_path = tempfile.NamedTemporaryFile(delete=False, suffix='.csv').name
    all_insights = []

    for file in csv_files:
        if file and allowed_file(file.filename):
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Read the CSV file and evaluate insights
            df = pd.read_csv(file_path)
            insights = evaluate_insights(df, category)
            all_insights.extend(insights)

    # Save insights to the temporary CSV file
    insights_df = pd.DataFrame(all_insights, columns=['Insight'])
    insights_df.to_csv(temp_file_path, index=False)

    return render_template('insights.html', insights=all_insights, temp_file_path=temp_file_path)

@app.route('/download_insights', methods=['GET'])
def download_insights():
    # Use the path stored in the template to serve the insights
    temp_file_path = request.args.get('temp_file_path')
    return send_file(temp_file_path, as_attachment=True)

# Route to collect feedback
@app.route('/feedback', methods=['POST'])
def feedback():
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    suggestion_id = get_next_suggestion_id()
    save_feedback(suggestion_id, rating, comment)
    return render_template('thank_you.html')

# Home route to display the upload form
@app.route('/')
def index():
    return render_template('index.html')

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
