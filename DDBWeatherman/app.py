# Import required modules and initialize Flask app
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Call the API
API_KEY = 'd0c46066655bc5fe727640f35da3096a'
WEATHER_API_URL = 'http://api.openweathermap.org/data/2.5/weather'
FORECAST_API_URL = 'http://api.openweathermap.org/data/2.5/forecast'

# Define the default route for web app
@app.route('/')
def index():
    return render_template('index.html')

# Define a route to get current weather data based on city input
@app.route('/get-weather')
def get_weather():
    city = request.args.get('city')
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric'  
    }
    response = requests.get(WEATHER_API_URL, params=params)
    data = response.json()
    return jsonify(data)

# Define a route to get a 5-day weather forecast based on city input
@app.route('/get-forecast')
def get_forecast():
    city = request.args.get('city')
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric' 
    }
    response = requests.get(FORECAST_API_URL, params=params)
    data = response.json()
    return jsonify(data)

# Run the Flask app when this script is executed
if __name__ == '__main__':
    app.run()
