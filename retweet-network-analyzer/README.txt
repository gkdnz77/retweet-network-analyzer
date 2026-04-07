SOCIAL GRAPH TOOL - API SETUP

This clean package keeps the API integration logic, but your original API key was removed.

========================================
1. WHAT WAS CLEANED
========================================
- Hardcoded API key removed
- No personal data
- No company-specific data
- No private credentials included

========================================
2. HOW TO GET AN API KEY
========================================
1. Create an account on RapidAPI
2. Subscribe to a Twitter/X data API that provides endpoints similar to:
   - /retweets
   - /followings
3. Copy your API key from the RapidAPI dashboard

========================================
3. HOW TO ADD YOUR API KEY
========================================
Windows (PowerShell):
setx RAPIDAPI_KEY "your_api_key_here"

Linux / macOS:
export RAPIDAPI_KEY="your_api_key_here"

Optional:
export RAPIDAPI_HOST="twitter241.p.rapidapi.com"

========================================
4. INSTALLATION
========================================
1. Install Python packages:
pip install flask flask-cors requests

2. Run the app:
python app.py

3. Open:
http://localhost:5000

========================================
5. NOTES
========================================
- The app will return an error if RAPIDAPI_KEY is missing
- You can replace RAPIDAPI_HOST if you use another compatible provider
- This package is for demo / development purposes
