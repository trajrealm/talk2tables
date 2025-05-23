from dotenv import load_dotenv
import os

def load_api_key():
    load_dotenv(override=True)

    api_key = os.getenv('OPENAI_API_KEY')

    MODEL = "gpt-4o-mini"
    # Check the key
    if not api_key:
        print("No API key was found - please head over to the troubleshooting notebook in this folder to identify & fix!")
    elif not api_key.startswith("sk-proj-"):
        print("An API key was found, but it doesn't start sk-proj-; please check you're using the right key - see troubleshooting notebook")
    elif api_key.strip() != api_key:
        print("An API key was found, but it looks like it might have space or tab characters at the start or end - please remove them - see troubleshooting notebook")
    else:
        print("API key found and looks good so far!")
