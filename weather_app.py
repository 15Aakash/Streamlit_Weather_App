import streamlit as st
import requests
import openai
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd


# Function to get weather data from OpenWeatherMap API
def get_weather_data(city, weather_api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=" + weather_api_key + "&q=" + city
    response = requests.get(complete_url)
    return response.json()


# Mock function to generate a weather description
def generate_weather_description(data, openai_api_key):
    # Mock response for development and testing
    temperature = data['main']['temp'] - 273.15
    description = data['weather'][0]['description']
    return f"The current weather in your city is: {description} with a temperature of {temperature:.1f} ̊C."


# Function to get weekly forecast data from OpenWeatherMap API
def get_weekly_forecast(weather_api_key, lat, lon):
    base_url = "http://api.openweathermap.org/data/2.5/forecast?"
    complete_url = f"{base_url}lat={lat}&lon={lon}&appid={weather_api_key}"
    response = requests.get(complete_url)
    return response.json()


# Function to display weekly weather forecast
def display_weekly_forecast(data):
    try:
        if 'list' not in data:
            st.error("No forecast data available!")
            return

        st.write("=================================================================================")
        st.write("### Weekly Weather Forecast")

        dates = []
        min_temps = []
        max_temps = []
        descriptions = []

        for day in data['list']:
            date = datetime.fromtimestamp(day['dt']).strftime('%A, %B %d')
            if date not in dates:
                dates.append(date)
                min_temps.append(day['main']['temp_min'] - 273.15)  # Convert Kelvin to Celsius
                max_temps.append(day['main']['temp_max'] - 273.15)
                descriptions.append(day['weather'][0]['description'])

        df = pd.DataFrame({
            'Date': dates,
            'Min Temperature (°C)': min_temps,
            'Max Temperature (°C)': max_temps,
            'Description': descriptions
        })

        st.write(df)

        # Plotting the data
        plt.figure(figsize=(10, 5))
        plt.plot(dates, min_temps, label='Min Temperature (°C)', marker='o')
        plt.plot(dates, max_temps, label='Max Temperature (°C)', marker='o')
        plt.fill_between(dates, min_temps, max_temps, color='gray', alpha=0.1)
        plt.xlabel('Date')
        plt.ylabel('Temperature (°C)')
        plt.title('Weekly Weather Forecast')
        plt.legend()
        plt.xticks(rotation=45)
        st.pyplot(plt)

    except Exception as e:
        st.error("Error in displaying weekly forecast: " + str(e))


# Main function to run the streamlit app
def main():
    # Sidebar configuration
    try:
        st.sidebar.image('Logo.jpg', width=120)
    except FileNotFoundError:
        st.sidebar.image('default_logo.jpg', width=120)  # Ensure you have a 'default_logo.png' file

    st.sidebar.title("Weather Forecasting with LLM")
    city = st.sidebar.text_input("Enter the city name", "London")

    # API keys
    weather_api_key = "b3871dae1418ab0236f69d0ba0e1ef8c"
    openai_api_key = "sk-proj-VWCQAURRrwd7nnT7GcE0T3BlbkFJ5O9svKnsDjiRzKKkdl9f"

    # Button to fetch and display weather data
    submit = st.sidebar.button("Get Weather")

    if submit:
        st.title("Weather Updates for " + city)
        with st.spinner('Fetching weather data...'):
            weather_data = get_weather_data(city, weather_api_key)
            print(weather_data)

            # Check if the city is found and display weather data
            if weather_data.get("cod") != 404:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Temperature", f"{weather_data['main']['temp'] - 273.15:.2f} ̊C")
                    st.metric("Humidity", f"{weather_data['main']['humidity']}%")
                with col2:
                    st.metric("Pressure", f"{weather_data['main']['pressure']} hPa")
                    st.metric("Wind Speed", f"{weather_data['wind']['speed']} m/s")

                # Display current temperature as a chart
                current_temp = weather_data['main']['temp'] - 273.15
                st.write("### Current Temperature")
                st.bar_chart(pd.DataFrame([current_temp], columns=['Temperature (°C)']))

                lat = weather_data['coord']['lat']
                lon = weather_data['coord']['lon']

                # Generate and display a friendly weather description
                weather_description = generate_weather_description(weather_data, openai_api_key)
                st.write(weather_description)

                # Call function to get weekly forecast
                forecast_data = get_weekly_forecast(weather_api_key, lat, lon)

                print(forecast_data)
                if forecast_data.get("cod") != "404":
                    display_weekly_forecast(forecast_data)
                else:
                    st.error("Error fetching weekly forecast data!")
            else:
                # Display an error message if the city is not found
                st.error("City not found or an error occurred!")


if __name__ == "__main__":
    main()
