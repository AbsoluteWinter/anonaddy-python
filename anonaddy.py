"""
Title: AnonAddy Python
Author: AbsoluteWinter
Status: W.I.P

Yes, messy code -_-
"""

import requests

# Services
BASE_URL = "https://app.anonaddy.com/"
API_TOKEN = "api/v1/api-token-details"
ACC_DETAIL = "api/v1/account-details"
ALIASES = "api/v1/aliases"

# Keywords
GET = "GET"
POST = "POST"
PATCH = "PATCH"
DELETE = "DELETE"

def perform_request(type: str, url: str, token: str, params = None, json = None):
    """
    Perform request on AnonAddy

    type : str
        GET | POST | PATCH | DELETE
    
    url : str
        link
    
    token : str
        account token
    
    params | json
        Custom parameters
    
    Return:
        Response
    """

    error_code_desc = {
        400: "Bad Request -- Your request sucks",
        401: "Unauthenticated -- Your API key is wrong",
        403: "Forbidden -- You do not have permission to access the requested resource",
        404: "Not Found -- The specified resource could not be found",
        405: "Method Not Allowed -- You tried to access an endpoint with an invalid method",
        422: "Validation Error -- The given data was invalid",
        429: "Too Many Requests -- You're sending too many requests or have reached your limit for new aliases",
        500: "Internal Server Error -- We had a problem with our server. Try again later",
        503: "Service Unavailable -- We're temporarially offline for maintanance. Please try again later"
    }

    headers = {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": f"Bearer {token}"
    }
    if params is not None:
        req = requests.request(type, url, headers=headers, params=params)
    elif json is not None:
        req = requests.request(type, url, headers=headers, json=json)
    else:
        req = requests.request(type, url, headers=headers)
    


    error_code = [400, 401, 403, 404, 405, 422, 429, 500, 503]
    if req.status_code in error_code:
        raise SystemError(error_code_desc[req.status_code])
    return req

def clean_alias(data: list):
    """
    Extract needed keys from aliases dict
    """
    out = []
    take = ["id", "email", "active"]
    for x in data:
        temp = dict()
        for y in take:
            temp[y] = x[y]
        if x["description"] is not None:
            temp["description"] = x["description"]
        out.append(temp)
    return out

class AnonAddy:
    """
    [AnonAddy - Anonymous email forwarding](anonaddy.com)
    
    Create a class that can do things
    """

    def __init__(self, token) -> None:
        self.token = token
        self.online = True # Check

        try:
            # Get Account details
            url = BASE_URL + ACC_DETAIL
            res = perform_request(GET, url, self.token).json()["data"]
            self.id = res["id"]
            self.username = res["username"]
            self.subscription = res["subscription"]
            if not res["subscription"].lower().startswith("free"):
                self.subscription_ends_at = res["subscription_ends_at"]
            self.bandwidth = f'{res["bandwidth"]:,}/{res["bandwidth_limit"]:,} bytes'
            self.default_alias_domain = res["default_alias_domain"]
        except:
            self.online = False # No connection
    
    def __str__(self) -> str:
        name = self.__class__.__name__
        try:
            return f"{name}({self.username})"
        except:
            return None

    def __repr__(self) -> str:
        return self.__str__()

    def get_aliases(self):
        """Get aliases"""
        url = BASE_URL + ALIASES
        res = perform_request(GET, url, self.token).json()["data"]
        
        out = clean_alias(res)
        return out
    
    def generate_alias(self, domain = None, description = None, format = None):
        payload = {
            "domain": self.default_alias_domain if domain is None else domain,
            "description": description,
            "format": "random_characters" if format is None else format
        }
        url = BASE_URL + ALIASES
        req = perform_request(POST, url, self.token, json=payload)

        return clean_alias([req.json()["data"]])
    
    def delete_alias(self, alias_id):
        url = BASE_URL + ALIASES + "/" + alias_id
        perform_request(DELETE, url, self.token)
        print("Done")

if __name__ == "__main__":
    from rich import print
    token = ""
    Test = AnonAddy(token)