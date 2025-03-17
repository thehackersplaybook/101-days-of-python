import time
import requests

access_token = "" # Replace with your Access Token

def get_linkedin_profile()-> dict:
    """
    Retrieves the LinkedIn profile information for the user.

    Args:
        None
        
    Returns:        
        dict: The LinkedIn profile information.
    """
    url = "https://api.linkedin.com/v2/me"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 429:  
        print("Rate limit reached! Waiting for 10 minutes before retrying...")
        time.sleep(600) 
        return get_linkedin_profile()  
    
    return response.json()

profile_data = get_linkedin_profile()
print(profile_data)
