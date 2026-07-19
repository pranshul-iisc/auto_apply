# Auto Apply Job Application Bot

This repository contains an automated bot that reads a list of job application URLs, fills out application forms using information from a JSON profile, uploads a resume, and optionally submits the applications.

It uses the [browser-use](https://github.com/browser-use/browser-use) library, which utilizes Playwright and LLM Agents (e.g. Gemini, OpenAI, Claude) to interact with forms intelligently without requiring custom HTML element selectors for each site.

---

## Setup Instructions

### 1. Prerequisites
- **Python**: Make sure you have Python 3.11+ installed. (This codebase was verified with Python 3.12).
- **Git**: Ensure Git is installed if cloning.

### 2. Create and Activate Virtual Environment
Open a terminal in the project directory and run:
```bash
python -m venv venv
```

Activate the environment:
- **Windows (PowerShell)**:
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
- **Windows (Command Prompt)**:
  ```cmd
  .\venv\Scripts\activate.bat
  ```
- **macOS / Linux**:
  ```bash
  source venv/bin/activate
  ```

### 3. Install Dependencies
Install the required packages:
```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers
Install the automated Chromium browser used by `browser-use`:
```bash
playwright install chromium
```

---

## Configuration

### 1. Environment Variables (`.env`)
Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```
Open `.env` and configure:
- `LLM_PROVIDER`: Set to `google` (default), `openai`, or `anthropic`.
- Set your respective API key (e.g. `GOOGLE_API_KEY` for Gemini, `OPENAI_API_KEY` for OpenAI, etc.).
- `AUTO_SUBMIT`: Set to `false` (recommended) to fill the forms but pause before submitting so you can review. Set to `true` if you want the bot to submit automatically.
- `HEADLESS`: Set to `false` to see the browser window and watch the bot fill out the form.

### 2. Job Application Profile (`profile_data.json`)
Copy the `profile_data.example.json` file to `profile_data.json`:
```bash
cp .env.example .env
```
Open `profile_data.json` and fill in your details (personal info, education, work experience, EEO options, etc.).
Make sure to configure the `resume_path` field to point to your PDF resume:
```json
"resume_path": "C:\\pranshi\\auto_apply\\resume.pdf"
```

### 3. Job URLs (`urls.txt`)
Open `urls.txt` and add the URLs of the job applications you want to apply to, with one URL per line. (Lines starting with `#` are ignored).

---

## Running the Bot

Ensure your virtual environment is active, then run:
```bash
python apply_bot.py
```

### Review Phase (If `AUTO_SUBMIT=false`)
The bot will navigate to each URL, fill out the form, and upload your resume. If `AUTO_SUBMIT` is `false`, it will complete the details and display a message indicating it is ready for your review. You can manually inspect the page and click the submit button. Once done, press enter or let the script finish to move to the next URL.
