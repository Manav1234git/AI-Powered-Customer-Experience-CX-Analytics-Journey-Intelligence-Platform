import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import pickle

# Generate synthetic dataset for training
np.random.seed(42)
n_samples = 1000

ticket_count = np.random.randint(0, 15, n_samples)
inactive_days = np.random.randint(0, 90, n_samples)
avg_sentiment = np.random.uniform(-1.0, 1.0, n_samples)

# Logic for churn: high tickets, high inactive, low sentiment -> high churn
logit = 0.3 * ticket_count + 0.4 * (inactive_days / 30) - 1.5 * avg_sentiment - 2.0
prob = 1 / (1 + np.exp(-logit))

# Binary classification: 1 if churned, 0 otherwise
churn_label = (prob > 0.5).astype(int)

df = pd.DataFrame({
    'ticket_count': ticket_count,
    'inactive_days': inactive_days,
    'avg_sentiment': avg_sentiment,
    'churned': churn_label
})

X = df[['ticket_count', 'inactive_days', 'avg_sentiment']]
y = df['churned']

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train Model
model = LogisticRegression(class_weight='balanced')
model.fit(X_scaled, y)

# Save model and scaler
with open('churn_model.pkl', 'wb') as f:
    pickle.dump({'model': model, 'scaler': scaler}, f)

print("Churn Prediction Model trained and saved successfully.")
