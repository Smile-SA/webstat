import requests

def get_ip_location(args=None):
    """
    Get IP-based location information using ipinfo.io.
    """
    response = requests.get('https://ipinfo.io/json')
    ip_info = response.json()

    if args.location and args.ip:
        return {'ip': ip_info.get('ip', 'Unknown'), 'city': ip_info.get('city', 'Unknown')} # Return IP address and Location
           
    elif args and args.location:
        return {'city': ip_info.get('city', 'Unknown'), 'ip': 'Unknown'}  # Return city information
    
    elif args and args.ip:
        return {'ip': ip_info.get('ip', 'Unknown'), 'city': 'Unknown'}  # Return IP information

    else:
        return {'ip': 'Unknown', 'city': 'Unknown'}  # Provide default values when args is None or neither -ip nor -location flags are present
