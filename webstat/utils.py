import requests

def get_ip_location(args=None):
    
    """
    Get IP-based location information using ipinfo.io.
    """
    if args and args.ipinfo:
                
        response = requests.get('https://ipinfo.io/json')
        
        if response.status_code == 200:
            ip_info = response.json()
            return ip_info
        else:
            print(f"Failed to retrieve IP information from ipinfo. Status code: {response.status_code}")
            print(f"Response content: {response.content}")
            return {'city': 'Unknown'}  # Provide a default value for city when IP information retrieval fails
    else:
        return {'NO ARGUMENT': None}  # Provide a default value for city when args is None or -ip flag is not present
