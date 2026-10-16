# Energy Monitoring Platform

A Python project for monitoring energy consumption and detecting anomalies using statistical methods and machine learning.

The project includes an interactive dashboard developed with Streamlit to visualize energy consumption and analyze detected anomalies.

## Dashboard Preview

![Energy Dashboard](assets/dashboard.png)
---


## Project Overview

The objective of this project is to identify unusual energy consumption patterns by combining two detection methods:

- **Rolling Statistics:** detects significant deviations from recent consumption trends.
- **Isolation Forest:** uses unsupervised machine learning to identify unusual observations.

The results of both methods are combined to classify anomalies according to their severity.

## Anomaly Detection

### 1. Rolling Statistics

A rolling window of 24 hours is used to calculate a local consumption baseline.

Anomalies are identified when energy consumption exceeds a dynamic threshold based on the rolling mean and standard deviation.

### 2. Isolation Forest

An Isolation Forest model is used to detect unusual consumption patterns without requiring labeled training data.

The model uses two features:

- Energy consumption (`energy_kwh`)
- Hour of the day (`hour`)

The model produces an anomaly score used to identify unusual observations.

### 3. Severity Classification

The results of both detection methods are combined to assign a severity level.

| Rolling Detection | Isolation Forest | Severity |
|-------------------|------------------|----------|
| False | False | NORMAL |
| True | False | WARNING |
| False | True | WARNING |
| True | True | CRITICAL |

### 4. Alert Levels

Each observation is also assigned an alert level based on the detected anomalies:

- NORMAL
- MEDIUM
- HIGH
- CRITICAL

## Dashboard

The dashboard is developed using Streamlit and Plotly.

It provides the following features:

- Interactive energy consumption time series
- Rolling mean visualization
- Highlighting of detected anomalies
- Severity filtering
- Alert level filtering

### Dashboard Preview

![Energy Monitoring Dashboard](assets/dashboard.png)

## Technologies Used

- Python
- Pandas
- Scikit-learn
- Streamlit
- Plotly

## Installation

Clone the repository:

```bash
git clone https://github.com/Abdourrahman-Mokeddem/energy-monitoring-platform.git
cd energy-monitoring-platform
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Run the Streamlit dashboard:

```bash
streamlit run streamlit_app.py
```

## Project Context

This project was developed to explore anomaly detection methods applied to energy consumption data.

It demonstrates how statistical analysis and unsupervised machine learning can be combined to detect unusual consumption patterns and visualize the results through an interactive dashboard.
