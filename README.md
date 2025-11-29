# 📱 Social Media Agent

AI-powered Streamlit app to help you **brainstorm content ideas, write captions, and plan your social media calendar** using the **Groq API** (Llama 3.3 70B Versatile).

---

## 🧠 What This Agent Does

The **Social Media Agent** is your assistant for:

- Generating **social media content ideas** for multiple platforms  
- Writing **engaging, platform-optimized captions** with emojis & hashtags  
- Creating **weekly content calendars** with dates, themes, platforms & posting times  
- Building a **full content plan** (ideas + captions + posting tips) for up to 30 days  

It’s designed for **creators, marketers, small businesses, and agencies** who want structured, AI-assisted social media planning.

---

## ✨ Features

### 1. 💡 Content Ideas (Tab 1)
- Generate **3–10 ideas** for a chosen:
  - **Topic/Theme**
  - **Platform** (Instagram, Twitter/X, LinkedIn, Facebook, TikTok, or All)
- Each idea includes:
  - Catchy angle
  - Content format suggestion (carousel, reel, tweet, etc.)
  - Engagement hook
- Ideas are saved in session and shown with platform badges.

### 2. ✍️ Caption Generator (Tab 2)
- Input any **content idea or description**
- Choose platform: Instagram, Twitter, LinkedIn, Facebook
- Generates:
  - Platform-optimized caption
  - Call-to-action
  - Emojis
  - 5–10 relevant hashtags
- Option to **copy caption** or generate another one.

### 3. 📅 Content Calendar (Tab 3)
- Set a **weekly theme**
- Choose **date range** (start & end date)
- Select platforms (Instagram, Twitter, LinkedIn, Facebook, TikTok)
- Generates a **7-day content calendar style plan**:
  - Day, platform, time, content type & idea
- Each calendar:
  - Saved in session
  - Viewable in expanders
  - Downloadable as `.txt`

### 4. 🚀 Full Content Plan (Tab 4)
- Create a **1–30 day content strategy** for a primary platform
- Configure:
  - Number of days
  - Brand voice (Professional/Casual/Humorous/etc.)
  - Content focus (Educational, Entertaining, Promotional, etc.)
  - Daily posting frequency
  - Main topic/theme
- For each day, AI generates:
  - Content idea
  - Short caption
  - Hashtags
  - Best posting time
  - Engagement tips
- Plan can be:
  - Viewed in the app
  - Saved into the internal calendar store
  - Downloaded as `.txt`

---

## 🧩 Tools, APIs & Models Used

- **Framework:** [Streamlit](https://streamlit.io/)
- **Language:** Python
- **HTTP Requests:** `requests`
- **Date & Time Handling:** `datetime`, `timedelta`
- **Randomization:** `random` (used in fallback ideas)
- **LLM Provider:** [Groq API](https://console.groq.com)
- **Model:** `llama-3.3-70b-versatile`  
  Used via Groq **Chat Completions** endpoint:
  ```text
  POST https://api.groq.com/openai/v1/chat/completions
