# 🧠 Dream Interpretation Tool

A beautiful, offline dream interpretation web application that matches your dreams to symbols from Gustavus Hindman Miller's "Ten Thousand Dreams Interpreted" (1901) and pairs them with relevant quotes.

## ✨ Features

- **Dream Symbol Matching**: Enter your dream and get matched with up to 2 symbols from a comprehensive database
- **Freud's Insights**: Receive thoughtful interpretations in Freud's voice
- **Dream Yield**: Get a tarot card and emotional emoji pairing based on your dream symbols
- **Offline & Fast**: Everything runs locally, no internet required
- **Beautiful UI**: Premium, dreamy interface with subtle animations

## 🚀 Quick Start (Super Easy!)

### For Windows Users (Easiest Way!)

1. **Download the project** from GitHub:
   - Click the green **"Code"** button → **"Download ZIP"**
   - Extract the ZIP file to any folder (e.g., Desktop)

2. **Double-click `START.bat`**
   - That's it! The server will start automatically

3. **Open your browser** and go to:
   ```
   http://localhost:8000/dream_matcher.html
   ```

### For Mac/Linux Users

1. **Download the project** from GitHub (same as above)

2. **Open Terminal** in the project folder and run:
   ```bash
   python3 server.py
   ```

3. **Open your browser** to:
   ```
   http://localhost:8000/dream_matcher.html
   ```

### Prerequisites

- **Python 3.7 or higher** (most computers already have this!)
  - Check by opening terminal/command prompt and typing: `python --version`
  - If you don't have it, download from [python.org](https://www.python.org/downloads/)
- **A modern web browser** (Chrome, Firefox, Edge, Safari)

## 📖 How to Use

1. **Enter Your Dream**: Type your dream description in the text box
2. **Get Interpretation**: Click the button to analyze your dream
3. **View Results**: 
   - See matched symbols with their meanings
   - View your Dream Yield (tarot card + emotional emoji)
   - Read Freud's remark about your dream

## 🎯 Example

Try entering: *"I was being chased by a wasp while driving my car"*

The system will:
- Match "wasp" and "car" to symbols in the database
- Show their interpretations
- Display a tarot card and emoji pairing
- Provide Freud's insight

## 📁 Project Structure

```
Freud/
├── dream_matcher.html      # Main web interface
├── server.py               # Python HTTP server
├── dream_quote_matcher.py  # Core matching logic
├── data/
│   ├── dream_database.json    # 2,400+ dream symbols
│   └── quotes_database.json   # Curated quotes database
├── without background/      # Emoji images
└── without background BOOK/ # Book/tarot images
```

## 🛠️ Technical Details

- **Backend**: Python 3 with simple HTTP server
- **Frontend**: Pure HTML/CSS/JavaScript (no frameworks)
- **Matching Algorithm**: Deterministic token-based matching
- **Data**: JSON databases with normalized dream interpretations

## 📝 Notes

- The database contains over 2,400 dream symbols
- All interpretations are based on Miller's 1901 work
- The system requires exactly 2 unique word matches for full interpretation
- Everything runs completely offline

## 🎨 Credits

- Dream interpretations: Gustavus Hindman Miller (1901)
- UI Design: Custom premium interface
- Images: Custom emoji and book/tarot assets

## 📄 License

This project uses dream interpretations from "Ten Thousand Dreams Interpreted" by Gustavus Hindman Miller (1901), which is in the public domain.

---

**Enjoy exploring your dreams! 🌙**
