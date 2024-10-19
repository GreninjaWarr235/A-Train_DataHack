import pandas as pd
import os

# Feedback collection (rating on a scale of 1-5) with optional comment
def collect_feedback():
    rating = input("Enter Rating (1-5): ")
    comment = input("Enter Comment (optional): ")
    return rating, comment

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
    # Check if the file exists
    file_exists = os.path.isfile(feedback_file)

    # Create a DataFrame for the new feedback
    feedback_df = pd.DataFrame([[suggestion_id, rating, comment]], columns=['Suggestion_ID', 'Rating', 'Comment'])

    # Save feedback to CSV
    feedback_df.to_csv(feedback_file, mode='a', header=not file_exists, index=False)

# Collect and save feedback
rating, comment = collect_feedback()
suggestion_id = get_next_suggestion_id()
save_feedback(suggestion_id, rating, comment)
