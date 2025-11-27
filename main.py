import getpass
import sys
import os
from libs.keep_client import KeepClient

def main():
    print("Google Keep Fetcher")
    print("-------------------")

    username = os.environ.get("GOOGLE_ACCOUNT_EMAIL")
    
    # In CI environment, email must be provided via environment variable
    if os.environ.get("CI") and not username:
        print("Error: GOOGLE_ACCOUNT_EMAIL environment variable not set in CI environment.")
        sys.exit(1)

    if not username:
        username = input("Email: ")
    
    client = KeepClient()
    
    # Try to login without password first (using token)
    if not client.login(username):
        # Check for OAuth token in environment variable (Option #3)
        env_oauth_token = os.environ.get("GOOGLE_OAUTH_TOKEN")
        # Check for master token in environment variable (Option #2)
        env_master_token = os.environ.get("GOOGLE_MASTER_TOKEN")
        
        if env_oauth_token:
            print("Using OAuth Token from environment variable...")
            if client.login_with_oauth_token(username, env_oauth_token):
                pass # Auth successful
            else:
                print("Authentication with environment OAuth token failed.")
                sys.exit(1)
        elif env_master_token:
            print("Using Master Token from environment variable...")
            if client.authenticate_with_token(username, env_master_token):
                pass # Auth successful
            else:
                print("Authentication with environment Master token failed.")
                sys.exit(1)
        else:
            # In CI environment, we cannot ask for input
            if os.environ.get("CI"):
                print("Error: No valid authentication token (GOOGLE_OAUTH_TOKEN or GOOGLE_MASTER_TOKEN) found in CI environment.")
                sys.exit(1)

            # If that fails, ask for password or master token
            print("\nAuthentication failed with stored token.")
            print("Choose an authentication method:")
            print("1. App Password (may fail with BadAuthentication)")
            print("2. Master Token (starts with 'aas_et/')")
            print("3. OAuth Token (Alternative Flow - Recommended if #1 fails)")
            
            choice = input("Enter choice (1/2/3): ").strip()
            
            if choice == '1':
                password = getpass.getpass("App Password: ")
                if not client.login(username, password):
                    print("Authentication failed. Exiting.")
                    sys.exit(1)
            elif choice == '2':
                token = getpass.getpass("Master Token: ")
                if not client.authenticate_with_token(username, token):
                     print("Authentication with master token failed. Exiting.")
                     sys.exit(1)
            elif choice == '3':
                print("\n--- Alternative OAuth Flow ---")
                print("1. Open this URL in your browser (incognito recommended):")
                print("   https://accounts.google.com/EmbeddedSetup")
                print("2. Log in with your Google account.")
                print("3. Open Developer Tools (F12) -> Application -> Cookies.")
                print("4. Find the cookie named 'oauth_token' and copy its value.")
                oauth_token = getpass.getpass("Paste 'oauth_token' here: ")
                
                if not client.login_with_oauth_token(username, oauth_token):
                    print("Authentication with oauth token failed. Exiting.")
                    sys.exit(1)
            else:
                print("Invalid choice. Exiting.")
                sys.exit(1)

    client.sync()
    
    print("\nFetching notes...")
    df = client.get_notes_as_dataframe()
    
    print(f"\nFound {len(df)} notes.")
    print("\nFirst 5 notes:")
    print(df.head())
    
    # Optional: Save to CSV
    output_file = "outputs/keep_notes.csv"
    df.to_csv(output_file, index=False)
    print(f"\nSaved to {output_file}")

if __name__ == "__main__":
    main()
