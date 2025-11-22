import getpass
import sys
from keep_client import KeepClient

def main():
    print("Google Keep Fetcher")
    print("-------------------")

    username = input("Email: ")
    
    client = KeepClient()
    
    # Try to login without password first (using token)
    if not client.login(username):
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
    df.to_csv("keep_notes.csv", index=False)
    print("\nSaved to keep_notes.csv")

if __name__ == "__main__":
    main()
