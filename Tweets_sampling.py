
import pandas as pd

# Step 1: Read the CSV file into a DataFrame
file_path = 'twitter_stemmed_data.csv'  # Replace with the path to your CSV file
df = pd.read_csv(file_path)

# Step 2: Check if the DataFrame has at least 10,000 rows
if len(df) < 10000:
    print("The CSV file does not contain 10,000 rows.")
else:
    # Step 3: Randomly select 10,000 rows
    sampled_df = df.sample(n=10000, random_state=1)  # random_state for reproducibility

    # Step 4: Optionally, save the sampled DataFrame to a new CSV file
    sampled_df.to_csv('sampled_tweets.csv', index=False)


