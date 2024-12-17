
import pandas as pd

# Read the CSV file into a DataFrame
file_path = 'french_tweets.csv'  # Replace with the path to your CSV file (You shouldn't have to change this one)
df = pd.read_csv(file_path)

# Check if the DataFrame has at least 10,000 rows
if len(df) < 10000:
    print("The CSV file does not contain 10,000 rows.")
else:
    # Randomly select 10,000 rows
    sampled_df = df.sample(n=10000, random_state=1)  # random_state for reproducibility

    # Save the sampled DataFrame to a CSV file
    sampled_df.to_csv('sampled_tweets.csv', index=False)


