import numpy as np
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import linregress

# Step 1 : Import the csv

df = pd.read_csv('summary_comments.csv')


# Step 2 : Create the proper columns by making operations

df_7_days_comments_avg = df['Number_comments'].rolling(window=7, min_periods=1).mean()
df_30_days_comments_avg = df['Number_comments'].rolling(window=30, min_periods=1).mean()

df_7_days_labels_avg = df['Number_labels'].rolling(window=7, min_periods=1).mean()
df_7_days_labels_percent = df_7_days_labels_avg / df_7_days_comments_avg

df_30_days_labels_avg = df['Number_labels'].rolling(window=30, min_periods=1).mean()
df_30_days_labels_percent = df_30_days_labels_avg / df_30_days_comments_avg

# We have to attend to the fact that the number of comments will raise with time
df['Date'] = pd.to_datetime(df['Date'])
reference_date = df['Date'].min()
x = (df['Date'] - reference_date).dt.days
y_30 = df_30_days_comments_avg
y_7 = df_7_days_comments_avg
slope_30, intercept_30, r_value_30, p_value_30, std_err_30 = linregress(x, y_30)
slope_7, intercept_7, r_value_7, p_value_7, std_err7_ = linregress(x, y_7)

Growing_comments_mean_7 = slope_7*df.index + intercept_7
Growing_comments_mean_30 = (slope_30+0.001)*df.index + intercept_30

values_comments_30 = df_30_days_comments_avg - Growing_comments_mean_30
values_comments_7 = df_7_days_comments_avg - Growing_comments_mean_7

# bound the result
scaling_factor = 0.01
bounded_values_tanh_30 = np.tanh(scaling_factor * values_comments_30) - ((np.tanh(scaling_factor * values_comments_30)).max() + (np.tanh(scaling_factor * values_comments_30)).min())/2
bounded_values_tanh_7 = np.tanh(scaling_factor * values_comments_7) - ((np.tanh(scaling_factor * values_comments_7)).max() + (np.tanh(scaling_factor * values_comments_7)).min())/2

day_index_7 = 1000*(bounded_values_tanh_7.abs() * (df_7_days_labels_percent - (df_7_days_labels_percent-0.0275).mean() ))
day_index_30 = 1000*(bounded_values_tanh_30.abs() * (df_30_days_labels_percent - (df_30_days_labels_percent-0.0275).mean() ))


# Step 3 : Create the plot 

st.title("Interactive Sentiment Analysis Plot")

# Create the figure
fig = go.Figure()

# Add the day_index_7 plot
fig.add_trace(go.Scatter(
    x=df['Date'],
    y=day_index_7,
    mode='lines+markers',
    name='Day Index (7 days)',
    hovertemplate='Date: %{x}<br>Index: %{y}<extra></extra>'
))

# Customize the layout
fig.update_layout(
    title="Interactive Sentiment Analysis Index",
    xaxis_title="Date",
    yaxis_title="Day Index (7 days)",
    xaxis=dict(showgrid=True, rangeslider=dict(visible=True)),  # Add range slider for x-axis
    yaxis=dict(showgrid=True),
    template="plotly_white",
    width=1200,  # Set the width of the plot (in pixels)
    height=800   # Set the height of the plot (in pixels)
)

# Render the plot in Streamlit
st.plotly_chart(fig, use_container_width=True)