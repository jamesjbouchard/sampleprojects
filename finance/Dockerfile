# Use the official Python image as a parent image
FROM python:3.8

# Set the working directory in the container
WORKDIR /finance

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install -r requirements.txt

# Copy your application code into the container
COPY . .

# Expose the port your app will run on (default for Flask is 5000)
#EXPOSE 5000

# Define the command to run your application
CMD ["python", "app.py"]
