import os
import sys
import getpass
from libs.keep_client import KeepClient
from config.constants import OUTPUT_DIR, KEEP_NOTES_CSV
from config.env import ENV


# ============================================================================
# Configuration
# ============================================================================

OUTPUT_FILE = "outputs/keep_notes.csv"


# ============================================================================
# Authentication Functions
# ============================================================================

def get_username():
    """Get username from environment or user input."""
    username = os.environ.get(ENV['GOOGLE_ACCOUNT_EMAIL'])
    
    # In CI environment, email must be provided via environment variable
    if os.environ.get(ENV['CI']) and not username:
        print(f"Error: {ENV['GOOGLE_ACCOUNT_EMAIL']} environment variable not set in CI environment.")
        sys.exit(1)

    if not username:
        username = input("Email: ")
    
    return username


def authenticate_with_env_tokens(client, username):
    """
    Attempt authentication using environment variables.
    
    Returns:
        bool: True if authentication succeeded, False otherwise
    """
    oauth_token = os.environ.get(ENV['GOOGLE_OAUTH_TOKEN'])
    master_token = os.environ.get(ENV['GOOGLE_MASTER_TOKEN'])
    auth_method = os.environ.get(ENV['AUTH_METHOD'], "").lower()

    # Try explicit auth method first
    if auth_method == 'master' and master_token:
        print("Using Master Token (explicitly selected)...")
        return client.authenticate_with_token(username, master_token)
    
    if (auth_method == 'oauth' or not auth_method) and oauth_token:
        print("Using OAuth Token...")
        return client.login_with_oauth_token(username, oauth_token)
    
    # Fallback to master token if available
    if master_token:
        print("Using Master Token (fallback)...")
        return client.authenticate_with_token(username, master_token)
    
    return False


def authenticate_interactively(client, username):
    """Prompt user for authentication credentials."""
    print("\nAuthentication failed with stored token.")
    print("Choose an authentication method:")
    print("1. App Password (may fail with BadAuthentication)")
    print("2. Master Token (starts with 'aas_et/')")
    print("3. OAuth Token (Alternative Flow - Recommended if #1 fails)")
    
    choice = input("Enter choice (1/2/3): ").strip()
    
    if choice == '1':
        password = getpass.getpass("App Password: ")
        return client.login(username, password)
    
    elif choice == '2':
        token = getpass.getpass("Master Token: ")
        return client.authenticate_with_token(username, token)
    
    elif choice == '3':
        print("\n--- Alternative OAuth Flow ---")
        print("1. Open this URL in your browser (incognito recommended):")
        print("   https://accounts.google.com/EmbeddedSetup")
        print("2. Log in with your Google account.")
        print("3. Open Developer Tools (F12) -> Application -> Cookies.")
        print("4. Find the cookie named 'oauth_token' and copy its value.")
        oauth_token = getpass.getpass("Paste 'oauth_token' here: ")
        return client.login_with_oauth_token(username, oauth_token)
    
    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)


def authenticate(client, username):
    """
    Authenticate the client using various methods.
    
    Priority:
    1. Stored token (keyring)
    2. Environment variables
    3. Interactive input
    """
    # Try stored token first
    if client.login(username):
        return
    
    # Try environment variables
    if authenticate_with_env_tokens(client, username):
        return
    
    # In CI, we can't do interactive auth
    if os.environ.get(ENV['CI']):
        print("Error: No valid authentication token found in CI environment.")
        sys.exit(1)
    
    # Interactive authentication
    if not authenticate_interactively(client, username):
        print("Authentication failed. Exiting.")
        sys.exit(1)


# ============================================================================
# Main Function
# ============================================================================

def main():
    """Main entry point for Google Keep Fetcher."""
    print("Google Keep Fetcher")
    print("-------------------")
    
    # Get username and authenticate
    username = get_username()
    client = KeepClient()
    authenticate(client, username)
    
    # Sync and fetch notes
    client.sync()
    print("\nFetching notes...")
    df = client.get_notes_as_dataframe()
    print(f"\nFound {len(df)} notes.")
    
    # Save to CSV
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_csv(KEEP_NOTES_CSV, index=False)
    print(f"Saved to {KEEP_NOTES_CSV}")


if __name__ == "__main__":
    main()
