import requests

url = "https://www.fast2sms.com/dev/bulkV2"

headers = {
    'authorization': "3kgPbxThiuEaSorMpF8c5W6YAClwyRLG9BQtUVqXIenD2sN4Jd9GRps4KJdneM1biV7TthOQ08kZDFgC",
    'Content-Type': "application/x-www-form-urlencoded",
    'Cache-Control': "no-cache",
    }

def send_sms(phone, otp: int):
    payload = f"variables_values={otp}&route=otp&numbers={phone}&sender_id=PYROLE"
    print(payload)
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)
    return response.status_code