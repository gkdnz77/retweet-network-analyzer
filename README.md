# Social Network Analysis Tool

A web-based application for analyzing social interactions on Twitter/X using external APIs.

This tool collects retweet data, analyzes user relationships, and classifies users into meaningful groups such as interaction clusters, potential bots, and independent users.

---

## 🚀 Features

* Analyze retweet networks from a tweet URL
* Fetch retweeter data using external APIs
* Classify users into groups:

  * Mutual interaction groups
  * Interaction-based users
  * New accounts
  * Potential bot accounts
  * Viral / high-impact users
* Group users based on connections
* Simple web interface (Flask + HTML)

---

## 🛠️ Tech Stack

* **Backend:** Python (Flask)
* **Frontend:** HTML, CSS, JavaScript
* **API:** RapidAPI (Twitter/X data)
* **Libraries:** requests, flask-cors

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/social-network-analysis-tool.git
cd social-network-analysis-tool
```

---

### 2. Install dependencies

```bash
pip install flask flask-cors requests
```

---

### 3. Get an API Key

1. Go to RapidAPI
2. Subscribe to a Twitter/X API provider
3. Copy your API key

---

### 4. Set environment variables

#### Windows (PowerShell)

```bash
setx RAPIDAPI_KEY "your_api_key_here"
```

#### Linux / macOS

```bash
export RAPIDAPI_KEY="your_api_key_here"
```

Optional:

```bash
export RAPIDAPI_HOST="twitter241.p.rapidapi.com"
```

---

### 5. Run the application

```bash
python app.py
```

Then open:

```
http://localhost:5000
```

---

## 📌 Usage

1. Paste a Twitter/X post URL
2. Click analyze
3. View:

   * User groups
   * Interaction clusters
   * Retweet statistics

---

## ⚠️ Notes

* This project does **not include any API keys**
* You must provide your own API credentials
* Works only with public tweets
* API limits depend on your RapidAPI subscription

---

## 🔐 Security

* No personal or company data is included
* API keys are handled via environment variables
* Safe for public sharing

---

## 📄 License

MIT License

---

## 👤 Author

Developed by [Gökdeniz Sağlam]

---
