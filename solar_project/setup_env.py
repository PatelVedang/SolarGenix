import os
import shutil

def setup_env():
    """
    Setup script to initialize the .env file from .env.example.
    """
    example_file = '.env.example'
    env_file = '.env'

    print("--- Solar Prediction API Setup ---")

    if not os.path.exists(example_file):
        print(f"Error: {example_file} not found. Please ensure it exists.")
        return

    if os.path.exists(env_file):
        print(f"{env_file} already exists. Skipping creation.")
    else:
        print(f"Creating {env_file} from {example_file}...")
        shutil.copy(example_file, env_file)
        print(f"Successfully created {env_file}.")

    print("\nNext Steps:")
    print(f"1. Open {env_file} and fill in your actual credentials.")
    print("2. Ensure Python dependencies are installed: pip install -r requirements.txt")
    print("3. Run the migrations if necessary: python manage.py migrate")
    print("4. Start the server: python manage.py runserver 5000")

if __name__ == "__main__":
    setup_env()
