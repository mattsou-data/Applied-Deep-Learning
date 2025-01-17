from datetime import datetime, timedelta
import re
import pandas as pd
import torch
from transformers import CamembertTokenizer, CamembertForSequenceClassification


# Relative path to the model folder in the GitHub Actions environment
save_path = './fine_tuned_camembert/fine_tuned_camembert'

tokenizer = CamembertTokenizer.from_pretrained(save_path)
model = CamembertForSequenceClassification.from_pretrained(save_path)


df_comments = pd.read_csv('comments.csv')


df_summary = pd.read_csv('summary_comments.csv') 
#Columns are Date, Number_comments, Number_labels

# Check if the DataFrame is empty
if df_comments.empty:

    df_summary['Date'] = pd.to_datetime(df_summary['Date']).dt.date

    # Ensure the DataFrame is sorted by date
    df_summary = df_summary.sort_values(by='Date')

    last_date = df_summary['Date'].iloc[-1]

    # Handle time in the string
    last_date = datetime.strptime(last_date.split()[0], '%Y-%m-%d')

    # Add one day
    new_date = last_date + timedelta(days=1)

    # Convert the new date back to string in 'YYYY-MM-DD' format
    new_date = new_date.strftime('%Y-%m-%d')
    

    # Calculate the average of the last 7 rows for 'Number of Comments' and 'Percentage of Positive Labels'
    avg_comments = df_summary['Number_comments'].tail(7).mean()
    avg_labels = df_summary['Number_labels'].tail(7).mean()

    # Create the new row
    new_row = pd.DataFrame({
        'Date': [new_date],
        'Number_comments': [avg_comments],
        'Number_labels' : [avg_labels]
    })

    # Append the new row to the DataFrame
    df_summary = pd.concat([df_summary, new_row], ignore_index=True)

    df_summary.to_csv('summary_comments.csv', index=False)


else:
     

    def preprocess_text(text):
        # Ensure the input is a string; replace NaN or non-string types with an empty string. Only if the number of Nan message is small, because otherwise 
        # we need to reconsider the data set
        if not isinstance(text, str):
            text = ''  # Handle NaN or non-string cases
        text = text.lower()  # Convert in lower case
        text = re.sub(r'[^a-zA-Zà-ÿ\s]', '', text)  # Suppress the special characters
        return text

    df_comments['Processed_comment'] = df_comments['Comment'].apply(preprocess_text)
    
    text1 = []

    for i in range(df_comments['Processed_comment'].size):
        text1.append(df_comments['Processed_comment'].iloc[i])

    # Initialize lists to store results
    all_logits = []
    all_probabilities = []
    all_predictions = []

    # Loop through each text individually
    for text in text1:
        # Tokenize the text
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        
        # Perform inference
        with torch.no_grad():
            outputs = model(**inputs)
        
        # Extract logits
        logits = outputs.logits
        
        # Convert logits to probabilities
        probabilities = torch.nn.functional.softmax(logits, dim=-1)
        
        predicted_class = torch.argmax(probabilities, dim=-1)
        
        # Store results
        all_logits.append(logits)
        all_probabilities.append(probabilities)
        all_predictions.append(predicted_class.item())

    df_comments['label'] = all_predictions

    last_date = df_summary['Date'].iloc[-1]

    # Handle time in the string
    last_date = datetime.strptime(last_date.split()[0], '%Y-%m-%d')

    # Add one day
    new_date = last_date + timedelta(days=1)

    # Convert the new date back to string in 'YYYY-MM-DD' format
    new_date = new_date.strftime('%Y-%m-%d')

    new_row = pd.DataFrame({
        'Date':[new_date],
        'Number_comments': [df_comments.shape[0]],
        'Number_labels': [df_comments[df_comments['label'] == 1].shape[0]]
    })

    df_summary = pd.concat([df_summary, new_row], ignore_index=True)

    df_summary.to_csv('summary_comments.csv', index=False)
   


    
