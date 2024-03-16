import aiohttp
import asyncio
import json
import argparse
from aiohttp import TCPConnector
from urllib.parse import urlencode
from itertools import product

async def fetch_token(url, client_id, client_secret, session, proxy=None):
    data = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    async with session.post(url, data=data, headers=headers, proxy=proxy, ssl=False) as response:
        resp_json = await response.json()
        return resp_json['access_token']

async def make_request(url, session, headers, query_params, filter_status, proxy=None):
    try:
        if query_params:
            query_string = urlencode(query_params, doseq=True)
            url = f"{url}?{query_string}"
        async with session.get(url, headers=headers, proxy=proxy, ssl=False) as response:
            if str(response.status) in filter_status:
                return  # Skip filtered status codes
            response_content = await response.json() if response.status == 200 else await response.text()
            print(f"URL: {url}, Status: {response.status}, Response: {response_content}")
    except Exception as e:
        print(f"Error accessing {url}: {e}")

def parse_api_parameters(api_parameters_str):
    params = {}
    if api_parameters_str:
        for part in api_parameters_str.split(","):
            key, value = part.strip().split(" ")
            if '-' in value:
                start, end = map(int, value.split('-'))
                params[key] = range(start, end + 1)
            else:
                params[key] = [int(value)]
    return params

def generate_param_combinations(params):
    expanded_params = {k: v if isinstance(v, range) else [v] for k, v in params.items()}
    return [dict(zip(expanded_params.keys(), values)) for values in product(*expanded_params.values())]

async def run(base_url, original_headers, filter_status, proxy, max_connections, api_parameters, api_spec, token_url):
    headers = original_headers.copy()
    params = parse_api_parameters(api_parameters)
    async with aiohttp.ClientSession(connector=TCPConnector(limit=max_connections)) as session:
        if 'client_id' in headers and 'client_secret' in headers:
            token = await fetch_token(token_url, headers['client_id'], headers['client_secret'], session, proxy)
            headers["Authorization"] = f"Bearer {token}"
        else:
            print("Running without authentication token.")
        for path, methods in api_spec['paths'].items():
            for method, details in methods.items():
                if method.lower() == "get":
                    endpoint_params = {p['name'] for p in details.get('parameters', []) if p['in'] in ['query', 'path']}
                    applicable_params = {k: v for k, v in params.items() if k in endpoint_params}
                    for combination in generate_param_combinations(applicable_params):
                        # Convert parameters that are in lists to single values
                        single_value_combination = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in combination.items()}
                        applied_path = path.format(**single_value_combination)
                        query_params = {k: v for k, v in combination.items() if f"{{{k}}}" not in path}
                        full_url = f"{base_url}{applied_path}"
                        #DEBUG print(f"Attempting {method} request to {full_url} with params {query_params}")
                        await make_request(full_url, session, headers, query_params, filter_status, proxy)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="API Caller Script with Enhanced Parameter Handling")
    parser.add_argument('--api-file', required=True, help="Path to the API Swagger JSON file")
    parser.add_argument('--client-id',  default=None, help="Client ID for token")
    parser.add_argument('--client-secret', default=None, help="Client Secret for token")
    parser.add_argument('--token-url', default=None, help="URL to fetch the authentication token")
    parser.add_argument('--proxy', help="Proxy server URL")
    parser.add_argument('--api-parameters', help="API parameters in 'key value, key value' format")
    parser.add_argument('--max-connections', type=int, default=10, help="Maximum number of concurrent connections")
    parser.add_argument('--filter-status', default="", help="Comma-separated HTTP status codes to filter")
    
    args = parser.parse_args()

    with open(args.api_file, 'r') as f:
        api_spec = json.load(f)

    base_url = f"https://{api_spec['host']}{api_spec['basePath']}"
    headers = {"x-api-version": "1.0"}

    if args.client_id and args.client_secret:
        headers["client_id"] = args.client_id
        headers["client_secret"] = args.client_secret

    filter_status = args.filter_status.split(',')

    asyncio.run(run(base_url, headers, filter_status, args.proxy, args.max_connections, args.api_parameters, api_spec, args.token_url))
