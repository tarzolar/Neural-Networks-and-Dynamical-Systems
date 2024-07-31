# -*- coding: utf-8 -*-
"""

This script implements a neural network to approximate the solutions of a system of differential equations.
The system is defined by specific parameters, and data is generated by solving these equations numerically.
The generated data is then used to train a neural network, which predicts future states of the system.


@author: Tomas Arzola Röber
"""
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense

# Define the differential equations
def ODE(z, t, H=0.328, xi=0.043, pD=0.06, alpha=0.28, r=0.5, q=2, m=1, delta=0.05, kappa=0.05, v=0.041, b=2, s=1):
    P, F = z
    dzdt = [pD - delta * F - alpha * P + (r * np.power(P, q) / (np.power(m, q) + np.power(P, q))),
            s * F * (1 - F) * (-v + xi * F + (kappa * np.power(P, b) / (np.power(H, b) + np.power(P, b))))]
    return dzdt

# Define the file paths
data_file = 'data.npz'
model_file = 'model.h5'

# Function to generate data
def generate_data(t):
    P_inputs, F_inputs, P_outputs, F_outputs = [], [], [], []

    for i in range(100):  # Generating 100 trajectories
        P0 = np.random.uniform(0, 1.6)  # Random initial condition for P
        F0 = np.random.uniform(0, 1)    # Random initial condition for F
        z0 = [P0, F0]
        
        solution = odeint(ODE, z0, t)
        P_inputs.append(solution[:-1, 0].tolist())  # P values from t=0 to t=999
        F_inputs.append(solution[:-1, 1].tolist())  # F values from t=0 to t=999
        P_outputs.append(solution[1:, 0].tolist())  # P values from t=1 to t=1000
        F_outputs.append(solution[1:, 1].tolist())  # F values from t=1 to t=1000

    # Convert lists to NumPy arrays
    P_inputs = np.array(P_inputs)
    F_inputs = np.array(F_inputs)
    P_outputs = np.array(P_outputs)
    F_outputs = np.array(F_outputs)

    # Save the data
    np.savez(data_file, P_inputs=P_inputs, F_inputs=F_inputs, P_outputs=P_outputs, F_outputs=F_outputs)
    return P_inputs, F_inputs, P_outputs, F_outputs

# Define the time array
t = np.linspace(0, 1000, 1000)  # Simulation time

# Check if data exists
if os.path.exists(data_file):
    data = np.load(data_file)
    P_inputs = data['P_inputs']
    F_inputs = data['F_inputs']
    P_outputs = data['P_outputs']
    F_outputs = data['F_outputs']
else:
    P_inputs, F_inputs, P_outputs, F_outputs = generate_data(t)

# Determine the number of samples
num_samples = P_inputs.shape[0]

# Create indices for splitting
indices = np.arange(num_samples)
np.random.shuffle(indices)

# Calculate split index
split_index = int(0.8 * num_samples)

# Split the data
train_indices = indices[:split_index]
test_indices = indices[split_index:]

# Prepare training and testing data
P_inputs_train = P_inputs[train_indices]
F_inputs_train = F_inputs[train_indices]
P_outputs_train = P_outputs[train_indices]
F_outputs_train = F_outputs[train_indices]

P_inputs_test = P_inputs[test_indices]
F_inputs_test = F_inputs[test_indices]
P_outputs_test = P_outputs[test_indices]
F_outputs_test = F_outputs[test_indices]

# Create the phase line diagrams
fig, axs = plt.subplots(1, 2, figsize=(14, 6))

# Training trajectories
axs[0].set_title('Training Trajectories')
for P, F in zip(P_inputs_train, F_inputs_train):
    axs[0].plot(P, F, 'b-', alpha=0.6)  # Blue for training trajectories
axs[0].scatter(P_inputs_train[:, 0], F_inputs_train[:, 0], c='red', marker='o', edgecolor='black')
axs[0].set_xlabel('P')
axs[0].set_ylabel('F')
axs[0].grid(True)

# Testing trajectories
axs[1].set_title('Testing Trajectories')
for P, F in zip(P_inputs_test, F_inputs_test):
    axs[1].plot(P, F, 'g-', alpha=0.6)  # Green for testing trajectories
axs[1].scatter(P_inputs_test[:, 0], F_inputs_test[:, 0], c='red', marker='o', edgecolor='black')
axs[1].set_xlabel('P')
axs[1].set_ylabel('F')
axs[1].grid(True)

plt.tight_layout()
plt.show()

# Flatten the data
P_inputs_train = np.array(P_inputs_train).flatten()
F_inputs_train = np.array(F_inputs_train).flatten()
P_outputs_train = np.array(P_outputs_train).flatten()
F_outputs_train = np.array(F_outputs_train).flatten()

P_inputs_test = np.array(P_inputs_test).flatten()
F_inputs_test = np.array(F_inputs_test).flatten()
P_outputs_test = np.array(P_outputs_test).flatten()
F_outputs_test = np.array(F_outputs_test).flatten()

# Prepare the data for the neural network
X_train = np.column_stack((P_inputs_train, F_inputs_train))
y_train = np.column_stack((P_outputs_train, F_outputs_train))
X_test = np.column_stack((P_inputs_test, F_inputs_test))
y_test = np.column_stack((P_outputs_test, F_outputs_test))

# Check if the model exists
if os.path.exists(model_file):
    model = load_model(model_file)
else:
    # Define the model
    model = Sequential([
        Dense(10, activation='relu', input_shape=(2,)),
        Dense(10, activation='relu'),
        Dense(10, activation='relu'),
        Dense(10, activation='relu'),
        Dense(2)  # Output layer with 2 units (P and F)
    ])

    # Compile the model
    model.compile(optimizer='adam', loss='mean_squared_error')

    # Train the model
    model.fit(X_train, y_train, epochs=20, batch_size=16, validation_split=0.1)

    # Save the model
    model.save(model_file)

# Evaluate the model
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f'Mean Squared Error: {mse}')
print(f'Mean Absolute Error: {mae}')
print(f'R² Score: {r2}')

# Prepare the initial conditions for prediction
initial_conditions_test = X_test[0].reshape(1, -1)  # Convert the 1D array to 2D

# Make predictions
last = initial_conditions_test
predictions = []
predictions.append(last)
for time in t:
    last = model.predict(last)
    predictions.append(last)

predictions = np.array(predictions).reshape(-1, 2)

predicted_P = []
predicted_F = []
for prediction in predictions:
    predicted_P.append(prediction[0])
    predicted_F.append(prediction[1])

sol = odeint(ODE, X_test[0], t)

P_sol = sol[:, 0]
F_sol = sol[:, 1]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

ax1.plot(P_sol, F_sol, 'g-') 
ax1.plot(P_sol[0], F_sol[0], 'ro', markeredgecolor='black')  
ax1.set_xlabel('P')
ax1.set_ylabel('F')
ax1.set_title('Test Trajectory - ODE Solution')
ax1.set_xlim(0, 1.6)  
ax1.set_ylim(0, 1)    
ax1.grid(True)

ax2.plot(predicted_P, predicted_F, 'g-')  
ax2.plot(predicted_P[0], predicted_F[0], 'ro', markeredgecolor='black') 
ax2.set_xlabel('P')
ax2.set_ylabel('F')
ax2.set_title('Test Trajectory - Neural Network Prediction')
ax2.set_xlim(0, 1.6)  
ax2.set_ylim(0, 1)  
ax2.grid(True)

plt.show()

fig2, (ax3, ax4) = plt.subplots(1, 2, figsize=(16, 6))

ax3.plot(t, P_sol, 'g-')
ax3.set_xlabel('Time')
ax3.set_ylabel('P')
ax3.set_title('Temporal Evolution of P - ODE Solution')
ax3.grid(True)

predicted_length = len(predicted_P) - 1  

ax4.plot(t[:predicted_length], predicted_P[:predicted_length], 'g-')
ax4.set_xlabel('Time')
ax4.set_ylabel('P')
ax4.set_title('Temporal Evolution of P - Neural Network Prediction')
ax4.grid(True)

plt.show()
