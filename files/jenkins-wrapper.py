from flask import Flask,request, jsonify
import requests
import argparse
from requests.auth import HTTPBasicAuth
import base64
import logging

app = Flask(__name__)
# Set up the argument parser
parser = argparse.ArgumentParser(description='Jenkins Crumb Retriever')
parser.add_argument('-url', '--jenkins_url', required=True, help='Jenkins URL')

# Parse the command-line arguments
args = parser.parse_args()
jenkins_url = args.jenkins_url

@app.route('/run-jenkins', methods=['POST'])
def callJenkins():
    logging.info("Jenkins wrapper received a request")
    job_name = request.args.get('job_name')  # Get job_name from URL query parameter
    if not job_name:
        return jsonify({'error': 'Missing job_name parameter'}), 400
    
    logging.info(f"Job name: {job_name}")
    post_params = request.json

    logging.info(f"Params: {post_params}")

    # Get the Authorization header from the incoming request
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Basic '):
        # Extract the base64 encoded auth token
        auth_token = auth_header.split(' ')[1]
        
        # Decode the base64 token to get the username and password
        auth_token_decoded = base64.b64decode(auth_token).decode('utf-8')
        username, password = auth_token_decoded.split(':')
    # The base URL of the API you want to call
    target_base_url = jenkins_url

    session = requests.Session()
    session.auth = (username, password)

    ## Get a Crumb
    response = session.get(f"{target_base_url}/crumbIssuer/api/json")
    crumb = response.json()['crumb']
    # Construct the full URL with the job_name and other query parameters
    # The job_name is appended to the URL path
    target_url = f"{target_base_url}/job/{job_name}"

    # Convert the post_params JSON body to a query string to append to target_url
    # If post_params is None or not a dictionary, default to an empty dict
    query_params = post_params if isinstance(post_params, dict) else {}
    headers = {
        'Content-Type': 'application/json',
        'Jenkins-Crumb': crumb
    }

    if (len(query_params) > 0):
    # Make a POST request to the target URL
    # Passing params argument to requests.post will append the parameters as a query string
        response = session.post(f"{target_url}/buildWithParameters", params=query_params, headers=headers)
    else:
        response = session.post(f"{target_url}/build")
    
    # You could handle different response status codes here with conditional statements...
    
    # Return the response content or handle it as needed
    return response.text, response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)