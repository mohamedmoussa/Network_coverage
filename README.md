# Network Coverage API

This is a Flask-based API that allows users to query the network coverage (2G/3G/4G) of different mobile operators in France based on a textual address.

## Installation
1. **Install the required Python packages**:
    pip install -r requirements.txt

## Running the Application

1. **Start the Flask server**:

   gunicorn -w 4 -b 127.0.0.1:5000 app:app

