# api-requests

## Overview
This script is designed to make asynchronous HTTP GET requests to APIs defined in a Swagger (OpenAPI) JSON file. It supports authentication via OAuth tokens and allows for dynamic parameterization of API requests. The script can operate both with and without authentication, depending on whether client credentials are provided.

## Requirements
Python 3.7+
aiohttp library
Installation
Ensure you have Python installed on your system. You can then install the required Python package using pip:
```
pip install aiohttp
```
## Usage
Basic usage of the script requires specifying the path to the Swagger JSON file with the --api-file argument. Additional options allow for customization of requests, including client authentication, proxy usage, and API parameterization.

### Without Authentication
To run the script without authentication, simply omit the --client-id and --client-secret arguments.
```
python api-requests.py --api-file path/to/your/swagger.json
```
### With Authentication
If the APIs require authentication, include the --client-id and --client-secret arguments, along with the optional --token-url for the authentication server.
```
python api-requests.py --api-file path/to/your/swagger.json --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET --token-url YOUR_TOKEN_URL
```
Additional Options
--proxy: Specify a proxy server URL.
--api-parameters: Define specific API parameters in a 'key value, key value' format. Supports ranges for numeric values.
--max-connections: Set the maximum number of concurrent connections (default is 10).
--filter-status: Provide a comma-separated list of HTTP status codes to ignore.

### Example with Parameters
Running the script with API parameters and filtering specific status codes:

```
python api-requests.py --api-file path/to/your/swagger.json --api-parameters "page 1-3, size 10" --filter-status "404,500"
```

## More Examples:

### Authenticated
```
python api_requests.py --api-file apis.json --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET --proxy http://localhost:8080 --max-connections 1 --api-parameters "id 1-100, productId 4, pageNo 1, itemsPerPage 1" --filter 400 --token-url https://example.com/OAuth/Token
```
### Unauthenticated
```
python api-requests.py --api-file apis.json --proxy http://localhost:8080 --max-connections 1 --api-parameters "id 1-100, productId 4, pageNo 1, itemsPerPage 1" --filter 400,401
```
