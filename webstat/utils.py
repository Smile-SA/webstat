import requests

def get_ip_location(args=None):
    """
    Get IP-based location information using ipinfo.io.
    """
    response = requests.get('https://ipinfo.io/json')
    ip_info = response.json()

    if args.location and args.ip:
        return {'ip': ip_info.get('ip'), 'city': ip_info.get('city')} # Return IP address and Location
           
    elif args and args.location:
        return {'city': ip_info.get('city')}  # Return city information
    
    elif args and args.ip:
        return {'ip': ip_info.get('ip')}  # Return IP information