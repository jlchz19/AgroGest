import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import the Flask app
from app_simple import app

def handler(event, context):
    """
    Netlify Function handler for the Flask app
    """
    try:
        # Get request details from Netlify event
        path = event.get('path', '/')
        http_method = event.get('httpMethod', 'GET')
        headers = event.get('headers', {})
        query_params = event.get('queryStringParameters', {}) or {}
        body = event.get('body', '')

        # Create a Flask test request context
        with app.test_request_context(
            path=path,
            method=http_method,
            headers=headers,
            query_string=query_params,
            data=body
        ):
            # Process the request
            response = app.full_dispatch_request()

            # Return response in Netlify format
            return {
                'statusCode': response.status_code,
                'headers': dict(response.headers),
                'body': response.get_data(as_text=True)
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': f'{{"error": "{str(e)}"}}'
        }
