import gkeepapi
import keyring
import getpass

class KeepClient:
    def __init__(self):
        self.keep = gkeepapi.Keep()
        self.username = None

    def login(self, username, password=None):
        """Logs into Google Keep.
        
        If password is provided, attempts to log in and save the token.
        If not, attempts to resume a session using a stored token.
        """
        self.username = username
        
        # Try to resume from a saved token
        token = None
        try:
            token = keyring.get_password("google-keep-fetcher", username)
        except Exception as e:
            print(f"Keyring access failed (expected in CI): {e}")

        if token and not password:
            print("Attempting to resume session...")
            try:
                self.keep.resume(username, token)
                print("Session resumed successfully.")
                return True
            except Exception as e:
                print(f"Failed to resume session: {e}")
                # If resume fails, we need a password to re-authenticate
        
        if password:
            print("Logging in...")
            try:
                # Use gpsoauth directly to get the master token
                # This avoids the 'Keep.login' deprecation warning
                import gpsoauth
                import gkeepapi
                
                # Generate a device ID (MAC address based)
                # Some users report empty string works better for BadAuthentication
                device_id = str(gkeepapi.get_mac())
                
                response = gpsoauth.perform_master_login(username, password, device_id)
                
                # If that fails, try with empty device_id
                if "Error" in response:
                    print(f"Login with device_id failed: {response.get('Error')}. Retrying with empty device_id...")
                    response = gpsoauth.perform_master_login(username, password, None)

                if "Error" in response:
                    print(f"Login failed: {response.get('Error')}")
                    if "Url" in response:
                        print(f"Please visit: {response.get('Url')}")
                    return False
                
                token = response.get("Token")
                if not token:
                    print("Login failed: No token received.")
                    return False
                    
                self.keep.resume(username, token)
                try:
                    keyring.set_password("google-keep-fetcher", username, token)
                    print("Login successful. Token saved.")
                except Exception as e:
                    print(f"Login successful, but failed to save token to keyring: {e}")
                return True
            except Exception as e:
                print(f"Login failed: {e}")
                return False
        
        print("No valid token found and no password provided.")
        return False

    def authenticate_with_token(self, username, token):
        """Authenticates using a manually provided master token."""
        self.username = username
        try:
            print("Authenticating with provided master token...")
            # Use resume() for compatibility with older gkeepapi versions
            self.keep.resume(username, token)
            try:
                keyring.set_password("google-keep-fetcher", username, token)
                print("Authentication successful. Token saved.")
            except Exception as e:
                print(f"Authentication successful, but failed to save token to keyring: {e}")
            return True
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False

    def login_with_oauth_token(self, username, oauth_token):
        """Exchanges an oauth_token for a master token and authenticates."""
        self.username = username
        print("Exchanging oauth_token for master token...")
        try:
            import gpsoauth
            import gkeepapi
            
            import urllib.parse
            import secrets
            
            # Ensure token is unquoted just in case
            oauth_token = urllib.parse.unquote(oauth_token)
            
            device_id = str(gkeepapi.get_mac())
            
            response = gpsoauth.exchange_token(username, oauth_token, device_id)
            
            # If that fails, try with empty device_id
            if "Error" in response:
                print(f"Token exchange with device_id failed: {response.get('Error')}. Retrying with empty device_id...")
                response = gpsoauth.exchange_token(username, oauth_token, None)

            # If that also fails, try with a random 16-char hex string (simulating Android ID)
            if "Error" in response:
                print(f"Token exchange with empty device_id failed: {response.get('Error')}. Retrying with random Android ID...")
                random_id = secrets.token_hex(8) # 16 chars
                response = gpsoauth.exchange_token(username, oauth_token, random_id)

            if "Error" in response:
                print(f"Token exchange failed: {response.get('Error')}")
                return False
                
            master_token = response.get("Token")
            if not master_token:
                print("Token exchange failed: No master token received.")
                return False
                
            print("Master token obtained. Authenticating...")
            return self.authenticate_with_token(username, master_token)
            
        except Exception as e:
            print(f"Token exchange failed: {e}")
            return False

    def sync(self):
        """Syncs with Google Keep servers."""
        print("Syncing notes...")
        self.keep.sync()

    def get_notes(self):
        """Returns a list of all notes."""
        return self.keep.all()

    def get_notes_as_dataframe(self):
        """Returns all notes as a pandas DataFrame."""
        import pandas as pd
        
        data = []
        for note in self.keep.all():
            labels = [label.name for label in note.labels.all()]
            data.append({
                'id': note.id,
                'title': note.title,
                'text': note.text,
                'created': note.timestamps.created,
                'updated': note.timestamps.updated,
                'labels': labels,
                'archived': note.archived,
                'trashed': note.trashed,
                'url': f"https://keep.google.com/#NOTE/{note.id}"
            })
            
        return pd.DataFrame(data)

    def print_notes(self):
        """Prints all notes to the console."""
        for note in self.keep.all():
            print("-" * 20)
            print(f"Title: {note.title}")
            print(f"Text: {note.text}")
            print("-" * 20)
