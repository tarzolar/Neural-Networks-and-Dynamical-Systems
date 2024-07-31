# -*- coding: utf-8 -*-
"""
This script implements a neural network to approximate the solutions of the chaotic System Lorenz Attractor.
The system is defined by specific parameters, and data is generated by solving these equations numerically.
The generated data is then used to train a neural network, which predicts future states of the system.

@author: Tomas Arzola Röber
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.integrate import odeint
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

# Define the Lorenz system differential equations
def lorenz(z, t, sigma=10, rho=28, beta=8/3):
    x, y, z = z
    dxdt = sigma * (y - x)
    dydt = x * (rho - z) - y
    dzdt = x * y - beta * z
    return [dxdt, dydt, dzdt]

# Define the time array
t = np.linspace(0, 25, 10000)  # Simulation time

# Initialize lists to store results
X_inputs = []
Y_inputs = []
Z_inputs = []
X_outputs = []
Y_outputs = []
Z_outputs = []

# Generate 100 trajectories with random initial conditions
for i in range(100):
    x0 = np.random.uniform(-20, 20)  # Random initial condition for x
    y0 = np.random.uniform(-30, 30)  # Random initial condition for y
    z0 = np.random.uniform(0, 50)    # Random initial condition for z
    initial_conditions = [x0, y0, z0]
    
    # Integrate the differential equations
    solution = odeint(lorenz, initial_conditions, t)
    
    # Store input and output data in lists of lists
    X_inputs.append(solution[:-1, 0].tolist())  # X values from t=0 to t=9999
    Y_inputs.append(solution[:-1, 1].tolist())  # Y values from t=0 to t=9999
    Z_inputs.append(solution[:-1, 2].tolist())  # Z values from t=0 to t=9999
    X_outputs.append(solution[1:, 0].tolist())  # X values from t=1 to t=10000
    Y_outputs.append(solution[1:, 1].tolist())  # Y values from t=1 to t=10000
    Z_outputs.append(solution[1:, 2].tolist())  # Z values from t=1 to t=10000

# Convert lists to NumPy arrays
X_inputs = np.array(X_inputs)
Y_inputs = np.array(Y_inputs)
Z_inputs = np.array(Z_inputs)
X_outputs = np.array(X_outputs)
Y_outputs = np.array(Y_outputs)
Z_outputs = np.array(Z_outputs)

# Determine the number of samples
num_samples = X_inputs.shape[0]

# Create indices for splitting
indices = np.arange(num_samples)
np.random.shuffle(indices)

# Calculate split index
split_index = int(0.8 * num_samples)

# Split the data
train_indices = indices[:split_index]
test_indices = indices[split_index:]

# Prepare training and testing data
X_inputs_train = X_inputs[train_indices]
Y_inputs_train = Y_inputs[train_indices]
Z_inputs_train = Z_inputs[train_indices]
X_outputs_train = X_outputs[train_indices]
Y_outputs_train = Y_outputs[train_indices]
Z_outputs_train = Z_outputs[train_indices]

X_inputs_test = X_inputs[test_indices]
Y_inputs_test = Y_inputs[test_indices]
Z_inputs_test = Z_inputs[test_indices]
X_outputs_test = X_outputs[test_indices]
Y_outputs_test = Y_outputs[test_indices]
Z_outputs_test = Z_outputs[test_indices]

# Create the phase line diagrams
fig, axs = plt.subplots(1, 2, figsize=(14, 6))

# Training trajectories
axs[0].set_title('Training Trajectories')
for x, y, z in zip(X_inputs_train, Y_inputs_train, Z_inputs_train):
    axs[0].plot(x, y, 'b-', alpha=0.6)  # Blue for training trajectories
axs[0].scatter(X_inputs_train[:, 0], Y_inputs_train[:, 0], c='red', marker='o', edgecolor='black')
axs[0].set_xlabel('X')
axs[0].set_ylabel('Y')
axs[0].legend()
axs[0].grid(True)

# Testing trajectories
axs[1].set_title('Testing Trajectories')
for x, y, z in zip(X_inputs_test, Y_inputs_test, Z_inputs_test):
    axs[1].plot(x, y, 'g-', alpha=0.6)  # Green for testing trajectories
axs[1].scatter(X_inputs_test[:, 0], Y_inputs_test[:, 0], c='red', marker='o', edgecolor='black')
axs[1].set_xlabel('X')
axs[1].set_ylabel('Y')
axs[1].legend()
axs[1].grid(True)

plt.tight_layout()
plt.show()

# Flatten the data for training
X_inputs_train = np.array(X_inputs_train).flatten()
Y_inputs_train = np.array(Y_inputs_train).flatten()
Z_inputs_train = np.array(Z_inputs_train).flatten()
X_outputs_train = np.array(X_outputs_train).flatten()
Y_outputs_train = np.array(Y_outputs_train).flatten()
Z_outputs_train = np.array(Z_outputs_train).flatten()

X_inputs_test = np.array(X_inputs_test).flatten()
Y_inputs_test = np.array(Y_inputs_test).flatten()
Z_inputs_test = np.array(Z_inputs_test).flatten()
X_outputs_test = np.array(X_outputs_test).flatten()
Y_outputs_test = np.array(Y_outputs_test).flatten()
Z_outputs_test = np.array(Z_outputs_test).flatten()



X_train = np.column_stack((X_inputs_train,Y_inputs_train,Z_inputs_train))
y_train = np.column_stack((X_outputs_train,Y_outputs_train,Z_outputs_train))
X_test = np.column_stack((X_inputs_test,Y_inputs_test,Z_inputs_test))
y_test = np.column_stack((X_outputs_test,Y_outputs_test,Z_outputs_test))

# Convert dataframes to numpy arrays


# Define the model
model = Sequential([
    Dense(10, activation='relu', input_shape=(3,)),
    Dense(10, activation='relu'),
    Dense(10, activation='relu'),
    Dense(10, activation='relu'),
    Dense(3)  # Output layer with 3 units (X, Y, Z)
])

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
model.fit(X_train, y_train, epochs=20, batch_size=16, validation_split=0.1)

# Prepare the initial conditions for prediction
initial_conditions_test = X_test[0].reshape(1, -1)  # Convert the 1D array to 2D

# Make predictions
last = initial_conditions_test
predictions = []
predictions.append(last)
for time in t:
    last = model.predict(last)
    predictions.append(last)

predictions = np.array(predictions).reshape(-1, 3)

predicted_X = []
predicted_Y = []
predicted_Z = []
for prediction in predictions:
    predicted_X.append(prediction[0])
    predicted_Y.append(prediction[1])
    predicted_Z.append(prediction[2])

sol = odeint(lorenz, X_test[0], t)

X_sol = sol[:, 0]
Y_sol = sol[:, 1]
Z_sol = sol[:, 2]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Plot trajectories
ax1.plot(X_sol, Y_sol, 'g-')
ax1.plot(X_sol[0], Y_sol[0], 'ro', markeredgecolor='black')
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_title('Test Trajectory - ODE Solution')
ax1.set_xlim(-30, 30)
ax1.set_ylim(-40, 40)
ax1.grid(True)

ax2.plot(predicted_X, predicted_Y, 'g-')
ax2.plot(predicted_X[0], predicted_Y[0], 'ro', markeredgecolor='black')
ax2.set_xlabel('X')
ax2.set_ylabel('Y')
ax2.set_title('Test Trajectory - Neural Network Prediction')
ax2.set_xlim(-30, 30)
ax2.set_ylim(-40, 40)
ax2.grid(True)

plt.show()

fig2, (ax3, ax4) = plt.subplots(1, 2, figsize=(16, 6))

# Plot temporal evolution of X from the ODE solution
ax3.plot(t, X_sol, 'g-')
ax3.set_xlabel('Time')
ax3.set_ylabel('X')
ax3.set_title('Temporal Evolution of X - ODE Solution')
ax3.grid(True)

# Plot temporal evolution of X from the Neural Network predictions
predicted_length = len(predicted_X) - 1
ax4.plot(t[:predicted_length], predicted_X[:predicted_length], 'g-')
ax4.set_xlabel('Time')
ax4.set_ylabel('X')
ax4.set_title('Temporal Evolution of X - Nueral Network Prediction')
ax4.grid(True)

plt.show()