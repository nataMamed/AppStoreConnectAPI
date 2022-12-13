
import os
import gzip
import logging
import tempfile
import requests
from jose import jwt
from pathlib import Path
from datetime import  datetime, timedelta


class AppStoreConnectApi:
    def __init__(self, issue_id:str, key_id:str, private_key:str) :

        self.api_token = self.fetch_token(issue_id, key_id, private_key)


    @staticmethod
    def fetch_token(issue_id:str, key_id:str, private_key:str) -> str:
        """Generate the apple store connect API jwt token 
        Args:
            issue_id (str): Your issuer ID from the API Keys page in App Store Connect;
            for example, 57246542-96fe-1a63-e053-0824d011072a.
            key_id (str): Your private key ID from App Store Connect; for example 2X9R4HXF34.   
            private_key (str): Your private key generated in the App Store Connect
        Returns:
            str: JWT token
        """

        header = {
        "alg": "ES256",
        "kid": key_id,
        "typ": "JWT"
        }
        payload = {
        "iss": issue_id,
        "aud": "appstoreconnect-v1",
        "iat": int(datetime.now().timestamp()),
        "exp": int(datetime.now().timestamp()) + 1000
        }
        return jwt.encode(claims=payload, key=private_key, 
                        headers=header,  algorithm='ES256')

    @staticmethod
    def get_request_data(request) -> str:
        """Decompress the data that came from the request object
        Args:
            request (Request): The result of a request.get method
        Returns:
            str: Decompressed data in str form
        """
        compressed_data = b""
        for block in request.iter_content(1024 * 1024):
            if block:
                compressed_data = compressed_data + block
            
        data = gzip.decompress(compressed_data)

        return data


    @staticmethod
    def write_data_to_file(data:str, path:str,  filename:str):
        """Writes str data in given filename
        Args:
            data (str): Text data
            filename (str): The filename which the data will be saved
        """
        text = data.decode("utf-8")
        save_path = Path(path)
        save_path.mkdir(parents=True, exist_ok=True)
        Path(os.path.join(save_path , f"{filename}.txt")).write_text(text, 'utf-8')


    def request_data_from_api(
        self,
        url:str)->str:
        """_summary_

        Args:
            url (str): The url to get

        Returns:
            str: returns the path where the file was stored
        """

        headers = {"Accept":"application/a-gzip, application/json",
                    'Authorization':f"Bearer {self.api_token}"}

        result = requests.request("GET", url, headers=headers)

        logging.info(f"-> Got the API data: {result}")

        data = self.get_request_data(result)

        # tmp_path = os.path.join(tempfile.mkdtemp(), f"temp.txt")
        # self.write_data_to_file(data, tmp_path)

        # logging.info("-> Saved the file as txt")

        return data

if __name__ == "__main__":
    
    VERSION = '1_0'
    FREQUENCY = "DAILY"
    REPORT_TYPE="SALES"
    KEY_ID = ""
    VENDOR_NUMBER = ''
    REPORT_SUBTYPE = 'SUMMARY'
    APPLE_AUTH_KEY = """"""
    ISSUE_ID = ""


    DELTA_DAYS = 2
    timestamp = datetime.now().date() - timedelta(days=DELTA_DAYS)

    api_url = f"""https://api.appstoreconnect.apple.com/v1/salesReports?\
filter[frequency]={FREQUENCY}&filter[reportDate]={timestamp}\
&filter[reportSubType]={REPORT_SUBTYPE}&filter[reportType]={REPORT_TYPE}\
&filter[vendorNumber]={VENDOR_NUMBER}"""

    api = AppStoreConnectApi(issue_id=ISSUE_ID, key_id=KEY_ID, private_key=APPLE_AUTH_KEY)

    data = api.request_data_from_api(url=api_url)
    api.write_data_to_file(data, "data/", "appstore_data")
    breakpoint()
