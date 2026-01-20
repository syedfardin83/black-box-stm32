import pandas as pd
import plotly.express as px

# Load your black box log
df = pd.read_csv('your_recorded_file.csv')

# Plot Accelerometer and Gyroscope data
fig = px.line(df, x='Time', y=['AccX', 'AccY', 'AccZ', 'GyroX', 'GyroY', 'GyroZ'], 
              title='Black Box 2.0 Gesture Analysis')
fig.show()