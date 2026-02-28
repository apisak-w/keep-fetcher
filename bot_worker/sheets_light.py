import json
import js
import time
import base64
from pyodide.ffi import to_js

class SheetsLightClient:
    """
    Lightweight Google Sheets client for Cloudflare Workers.
    Uses Web Crypto API (via 'js' module) for RS256 signing of JWTs.
    """
    def __init__(self, service_account_json, sheet_id):
        self.creds = json.loads(service_account_json)
        self.sheet_id = sheet_id
        self.access_token = None
        self.token_expiry = 0

    def _base64_url_encode(self, data):
        if isinstance(data, dict):
            data = json.dumps(data)
        if isinstance(data, str):
            data = data.encode('utf-8')
        return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

    async def _get_access_token(self):
        """Exchange Service Account JWT for an access token."""
        if self.access_token and time.time() < self.token_expiry - 60:
            return self.access_token

        # JWT Header and Payload
        header = {"alg": "RS256", "typ": "JWT"}
        now = int(time.time())
        payload = {
            "iss": self.creds["client_email"],
            "scope": "https://www.googleapis.com/auth/spreadsheets",
            "aud": "https://oauth2.googleapis.com/token",
            "iat": now,
            "exp": now + 3600
        }

        # Encode header and payload
        unsigned_jwt = f"{self._base64_url_encode(header)}.{self._base64_url_encode(payload)}"
        
        # Sign the JWT using Web Crypto API
        # 1. Clean up the private key
        pk_str = self.creds["private_key"]
        # Remove headers/footers and newlines
        pk_content = pk_str.replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "").replace("\n", "").replace("\r", "")
        # Convert base64 to Uint8Array
        pk_buffer = bytes(base64.b64decode(pk_content))
        
        # 2. Import the key via JS
        key_data = js.Uint8Array.new(len(pk_buffer))
        for i, b in enumerate(pk_buffer):
            key_data[i] = b
            
        # Use JSON.parse to ensure we pass native JS objects/arrays
        # as Web Crypto API can be picky about Pyodide proxies.
        algo = js.JSON.parse('{"name": "RSASSA-PKCS1-v1_5", "hash": "SHA-256"}')
        usages = js.JSON.parse('["sign"]')
        
        key = await js.crypto.subtle.importKey(
            "pkcs8",
            key_data,
            algo,
            False,
            usages
        )
        
        # 3. Sign the content
        data_to_sign = js.Uint8Array.new(len(unsigned_jwt))
        for i, c in enumerate(unsigned_jwt):
            data_to_sign[i] = ord(c)
            
        sign_algo = js.JSON.parse('{"name": "RSASSA-PKCS1-v1_5"}')
        signature_buffer = await js.crypto.subtle.sign(
            sign_algo,
            key,
            data_to_sign
        )
        
        # 4. Convert signature to base64url
        sig_bytes = bytes(js.Uint8Array.new(signature_buffer))
        signature = base64.urlsafe_b64encode(sig_bytes).decode('utf-8').rstrip('=')
        
        signed_jwt = f"{unsigned_jwt}.{signature}"

        # Request the access token
        options = js.Object.fromEntries(to_js({
            "method": "POST",
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            "body": f"grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer&assertion={signed_jwt}"
        }))
        resp = await js.fetch("https://oauth2.googleapis.com/token", options)
        
        res_data = (await resp.json()).to_py()
        if "access_token" not in res_data:
            raise Exception(f"Failed to get access token: {res_data}")
            
        self.access_token = res_data["access_token"]
        self.token_expiry = now + int(res_data.get("expires_in", 3600))
        return self.access_token

    async def append_row(self, row_data):
        """Append a single row to the sheet."""
        token = await self._get_access_token()
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.sheet_id}/values/A1:append?valueInputOption=USER_ENTERED"
        
        payload = {
            "values": [row_data]
        }
        
        options = js.Object.fromEntries(to_js({
            "method": "POST",
            "headers": {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            "body": json.dumps(payload)
        }))
        
        resp = await js.fetch(url, options)
        
        return (await resp.json()).to_py()

    async def get_values(self, range_name):
        """Fetch raw values from a specific range/sheet."""
        token = await self._get_access_token()
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.sheet_id}/values/{range_name}?valueRenderOption=UNFORMATTED_VALUE"
        
        options = js.Object.fromEntries(to_js({
            "method": "GET",
            "headers": {
                "Authorization": f"Bearer {token}"
            }
        }))
        
        resp = await js.fetch(url, options)
        data = (await resp.json()).to_py()
        return data.get("values", [])

    async def get_all_records(self):
        """Fetch all data from the first sheet and return as list of dicts."""
        values = await self.get_values("A:Z")
        if not values:
            return []
            
        header = values[0]
        records = []
        for row in values[1:]:
            record = {}
            for i, h in enumerate(header):
                val = row[i] if i < len(row) else ""
                # Convert null to empty string for consistency
                record[h] = val if val is not None else ""
            records.append(record)
        return records
