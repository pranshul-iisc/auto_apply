import asyncio
import json
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from browser_use import Agent, Browser, BrowserProfile
from browser_use import ChatGoogle, ChatOpenAI, ChatAnthropic

def get_llm():
    """Initializes and returns the LangChain/Browser-use LLM based on environment variables."""
    provider = os.getenv("LLM_PROVIDER", "google").lower()
    model_name = os.getenv("LLM_MODEL", "gemini-2.5-flash")
    
    print(f"Initializing LLM provider '{provider}' with model '{model_name}'...")
    
    if provider == "google":
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Warning: Neither GOOGLE_API_KEY nor GEMINI_API_KEY found in environment variables.")
        # Google GenAI SDK expects GEMINI_API_KEY or GOOGLE_API_KEY
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
            os.environ["GOOGLE_API_KEY"] = api_key
        return ChatGoogle(model=model_name, api_key=api_key)
        
    elif provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Warning: OPENAI_API_KEY not found in environment variables.")
        return ChatOpenAI(model=model_name, api_key=api_key)
        
    elif provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("Warning: ANTHROPIC_API_KEY not found in environment variables.")
        return ChatAnthropic(model=model_name, api_key=api_key)
        
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}. Choose 'google', 'openai', or 'anthropic'.")

def load_profile():
    """Loads and validates the profile JSON file."""
    profile_path = "profile_data.json"
    if not os.path.exists(profile_path):
        print(f"Error: Profile file '{profile_path}' not found. Please create it using profile_data.json template.")
        sys.exit(1)
        
    with open(profile_path, "r", encoding="utf-8") as f:
        try:
            profile = json.load(f)
            return profile
        except json.JSONDecodeError as e:
            print(f"Error parsing profile JSON: {e}")
            sys.exit(1)

def load_urls():
    """Loads application URLs from urls.txt file."""
    urls_path = "urls.txt"
    if not os.path.exists(urls_path):
        print(f"Error: URLs file '{urls_path}' not found. Please create it.")
        sys.exit(1)
        
    urls = []
    with open(urls_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    return urls

async def apply_to_job(url: str, profile: dict, llm, browser: Browser, auto_submit: bool, resume_path: str):
    """Starts a browser agent task to apply for a job URL."""
    print(f"\n--- Starting Job Application for URL: {url} ---")
    
    # Format EEO options, preferences, education, and experience for the agent
    task = f"""
Your goal is to apply to the job at this URL: {url}
You must navigate to the URL and complete all forms and fields required.

Below is the candidate's profile information to use for filling out the form:
{json.dumps(profile, indent=2)}

Authentication Instructions:
- If the website requires you to sign in or create an account before applying, ALWAYS choose "Continue with Google", "Sign in with Google", or "Login with Google" if that option is available.
- Do NOT create a new account using email/password if Google Sign-In is available.
- If Google asks you to choose an account, select the already signed-in Google account.

Important Instructions:
1. Locate all the text fields, dropdowns, check boxes, radio buttons, and sections (such as Name, Email, Phone, Address, Links like LinkedIn/GitHub, Education, Experience, Skills, Preferences, EEO voluntary fields) and fill them in accurately using the candidate profile.
2. If there is a file input field to upload a resume or CV, you MUST upload the resume located at the path: "{resume_path}". Use the `upload_file` action with the index of the file input and this path.
3. If you encounter any pop-ups, cookie consents, or login dialogs that block the form, close them or accept them to proceed.
4. Fill out the application from top to bottom, one page or section at a time.
5. Submission:
   - If AUTO_SUBMIT is set to True (value: {auto_submit}), click the final submit/apply button to complete the application.
   - If AUTO_SUBMIT is set to False (value: {auto_submit}), DO NOT click the final submit button. Fill out all the fields and upload the resume, navigate to the final page/step, and then stop so the user can review and manually click submit. Tell the user you are ready for review.
6. Use the `done` action once you have completed the application (or are ready for review, if AUTO_SUBMIT is False).
"""
    
    # Initialize the Agent
    # We pass the resume_path in available_file_paths so the agent has permission to upload it
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
        available_file_paths=[resume_path] if resume_path else []
    )
    
    try:
        result = await agent.run()
        print(f"Application finished for: {url}")
        print(f"Result details: {result}")
        return True
    except Exception as e:
        print(f"Error during application for {url}: {e}")
        return False

async def main():
    # Load profile data
    profile = load_profile()
    
    # Retrieve resume path
    resume_path = profile.get("resume_path", "")
    if not resume_path:
        print("Warning: 'resume_path' is not defined in profile_data.json.")
    elif not os.path.exists(resume_path):
        print(f"Warning: Resume file not found at: {resume_path}")
        print("Please ensure the resume file exists or update the path in profile_data.json.")
    
    # Load application URLs
    urls = load_urls()
    if not urls:
        print("No URLs found in urls.txt. Please add job application URLs (one per line).")
        sys.exit(0)
    
    # Load settings
    auto_submit_str = os.getenv("AUTO_SUBMIT", "false").lower()
    auto_submit = auto_submit_str in ("true", "1", "yes")
    
    headless_str = os.getenv("HEADLESS", "false").lower()
    headless = headless_str in ("true", "1", "yes")
    
    print(f"Settings loaded: AUTO_SUBMIT={auto_submit}, HEADLESS={headless}")
    print(f"Found {len(urls)} job application URL(s) to process.")
    
    # Initialize LLM
    llm = get_llm()
    
    # Initialize browser
    # Job application requires persistence and visual review, so we use config
    browser_profile = BrowserProfile(
                                        headless=headless,
                                        executable_path=r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",    
                                    )
    browser = Browser(browser_profile=browser_profile)
    
    try:
        # Loop through each job URL and run application
        for index, url in enumerate(urls, start=1):
            print(f"\nProcessing Job {index}/{len(urls)}")
            success = await apply_to_job(
                url=url,
                profile=profile,
                llm=llm,
                browser=browser,
                auto_submit=auto_submit,
                resume_path=resume_path
            )
            if success:
                print(f"Job {index} processed.")
            else:
                print(f"Job {index} failed processing.")
    finally:
        # Close the browser session
        await browser.close()
        print("\nAll applications processed. Browser closed.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting...")
