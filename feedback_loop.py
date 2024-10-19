import pandas as pd
# Feedback collection (rating on a scale of 1-5)
def collect_feedback():
    suggestion_id = input("Enter Suggestion ID: ")
    rating = input("Enter Rating (1-5): ")
    return suggestion_id, rating

# Save feedback to a CSV file
def save_feedback(suggestion_id, rating, feedback_file='feedback.csv'):
    feedback_df = pd.DataFrame([[suggestion_id, rating]], columns=['Suggestion_ID', 'Rating'])
    feedback_df.to_csv(feedback_file, mode='a', header=False, index=False)

# Collect and save feedback
suggestion_id, rating = collect_feedback()
save_feedback(suggestion_id, rating)
