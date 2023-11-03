import re
import json
import os
import sys
import logging
from flask import Flask, request, jsonify, abort, after_this_request
from flasgger import Swagger

# Initialize the Flask application
app = Flask(__name__)

# Setup Swagger automatically from the YAML file
Swagger(app)

# Setup logging to output to stderr, with the INFO verbosity level.
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

# Retrieve the expected API Key from an environment variable
API_KEY = os.environ.get('API_KEY')

def parse_time(time_string):
    """
    Parses a time string from SRT format to milliseconds.
    
    Args:
        time_string (str): A time string in the format 'hours:minutes:seconds,milliseconds'.
    
    Returns:
        int: The time in milliseconds.
    
    Raises:
        ValueError: If the time string is not in the correct format.
    """
    try:
        # Extract hours, minutes, seconds and milliseconds using regular expressions
        hours = int(re.findall(r'(\d+):\d+:\d+,\d+', time_string)[0])
        minutes = int(re.findall(r'\d+:(\d+):\d+,\d+', time_string)[0])
        seconds = int(re.findall(r'\d+:\d+:(\d+),\d+', time_string)[0])
        milliseconds = int(re.findall(r'\d+:\d+:\d+,(\d+)', time_string)[0])

        # Convert all time components to milliseconds and return the total
        return (hours * 3600 + minutes * 60 + seconds) * 1000 + milliseconds
    except IndexError as e:
        # If parsing fails, raise an error with a clear explanation
        raise ValueError("Time string is in an incorrect format.") from e

def parse_srt(srt_string):
    """
    Parses SRT formatted string into a list of subtitle dictionaries.

    Args:
        srt_string (str): The SRT file content.

    Returns:
        list: A list of dictionaries with subtitle data.

    Raises:
        ValueError: If the SRT string is empty or incorrectly formatted.
    """
    # Initialize an empty list to hold the subtitle data
    srt_list = []

    # Check if the provided string is empty and raise an error if so
    if not srt_string.strip():
        raise ValueError("The SRT text provided is empty.")

    # Split the SRT string into parts and iterate over each subtitle block
    for block in srt_string.split('\n\n'):
        if block.strip():  # Ignore empty blocks
            try:
                # Split each block into lines
                lines = block.split('\n')
                # The first line should be the index
                index = int(lines[0])
                # The second line should be the timings
                timing_line = lines[1]
                timing_match = re.search(r'(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)', timing_line)
                if not timing_match:
                    raise ValueError(f"Invalid timing format in block: {block}")

                # Extract start and end times from the timing line
                start_time_string, end_time_string = timing_match.groups()
                start_time = parse_time(start_time_string)
                end_time = parse_time(end_time_string)

                # Ensure that the start time is before the end time
                if start_time > end_time:
                    raise ValueError(f"Start time must be less than or equal to end time in block: {block}")

                # The remaining lines are the subtitle content
                content = '\n'.join(lines[2:]).strip()

                # Append the parsed subtitle to the list
                srt_list.append({
                    'index': index,
                    'content': content,
                    'start': start_time,
                    'end': end_time
                })
            except Exception as e:
                # Log the exception details and the problematic block for easier debugging
                # Note: You would typically use a logging library here instead of print
                print(f"Error parsing block: {block}\nException: {e}")
                # Optionally, you could continue parsing the remaining blocks instead of raising an error
                # For now, we'll raise the error to signal that something went wrong
                raise ValueError(f"Error parsing SRT block: {e}")
    return srt_list

def check_api_key(request):
    """
    Checks the provided API key against the expected one.
    
    Args:
        request: The Flask request object.
    
    Raises:
        abort(401): If the API key is missing or incorrect.
    """
    # Retrieve the API key from the request headers
    api_key = request.headers.get('X-API-KEY')
    # If the API key does not match, abort the request with a 401 Unauthorized error
    if not api_key or api_key != API_KEY:
        abort(401, description="Unauthorized: API key is invalid or missing.")

@app.route('/parse_srt', methods=['POST'])
def parse_srt_endpoint():
    """
    API endpoint to parse SRT content.
    This uses the `flasgger` library to generate Swagger documentation automatically.
    """
    # Check if the API key is correct before processing the request
    check_api_key(request)

    # Decode the request data from bytes to a string
    srt_data = request.data.decode('utf-8')

    # Attempt to parse the SRT data and return the result as JSON
    try:
        parsed_srt = parse_srt(srt_data)
        return jsonify(parsed_srt)
    except ValueError as e:
        # If parsing fails, return a 400 Bad Request error with the error message
        abort(400, description=str(e))

@app.after_request
def after_request(response):
    """
    Logging function to execute after each request.
    
    Args:
        response: The Flask response object.
    
    Returns:
        The response object with potentially additional headers.
    """
    # Log the request and response details
    if response.content_length == 0:
        app.logger.info('No content to log.')
    else:
        app.logger.info('%s %s %s %s %s',
                        request.remote_addr,
                        request.method,
                        request.scheme,
                        request.full_path,
                        response.status)
    # Return the response to complete the request lifecycle
    return response

# Error handlers to log and return JSON error responses
@app.errorhandler(400)
def bad_request(error):
    app.logger.error('400 Bad Request: %s', error.description)
    return jsonify({'error': 'Bad request', 'message': error.description}), 400

@app.errorhandler(401)
def unauthorized(error):
    app.logger.error('401 Unauthorized: %s', error.description)
    return jsonify({'error': 'Unauthorized', 'message': error.description}), 401

@app.errorhandler(404)
def not_found(error):
    app.logger.error('404 Not Found: %s', error.description)
    return jsonify({'error': 'Not found', 'message': error.description}), 404

@app.errorhandler(500)
def internal_server_error(error):
    app.logger.error('500 Internal Server Error: %s', error.description)
    return jsonify({'error': 'Internal server error', 'message': error.description}), 500

if __name__ == '__main__':
    # Dynamically set the port using an environment variable, with a default of 8080
    port = os.getenv('PORT', 8080)
    # Run the Flask application on the specified port
    app.run(host='0.0.0.0', port=int(port))