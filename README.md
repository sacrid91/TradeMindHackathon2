# 🧠 TradeMind Journal: Your Edge Isn’t Just Strategy — It’s Your Psychee

> **Emotion. Discipline. Insight. Monetization. All in one AI-powered trading journal.**

TradeMind is a behavioral finance platform that helps traders **track emotions**, **enforce discipline**, and **unlock AI-powered insights** — all while integrating **real monetization via IntaSend**.

Built for the **African fintech hackathon**, it aligns with **SDG 3 (Good Health & Well-being)** by promoting mental resilience in trading.

🌐 **Live Demo**: [https://trademindjournal.onrender.com](https://trademindjournal.onrender.com)  
🎯 **Hackathon Ready**: Fully functional and deployed 
📈 **Tech Stack**: Django, Python, Hugging Face,Deepseek(prompt Engineering)& API calls, IntaSend(Montetisation Test), Tailwind CSS(Styling)
   **Pitch deck**: https://gamma.app/docs/Untitled-k27bcsp27fll8fb

---

## 🚀 Features

| Feature                        |   Description                                                   |
|--------------------------------|---------------------------------------------------------------------------|
| ✅ **Emotion Tracking**       | Log pre- and post-trade emotions (Fear, Happy, Chill, etc.) |
| ✅ **Rule-Based Discipline**  | Create, edit, delete checklist rules (e.g., "Enter only on BOS") |
| ✅ **AI Behavioral Coach**    | Real-time insight using **Hugging Face Llama-3.1-8B-Instruct** |
| ✅ **Monetization**           | Unlock premium reports via **IntaSend (KES 50)** |
| ✅ **Dark Mode**              | Built-in dark theme for late-night trading sessions |
| ✅ **Responsive UI**          | Works on mobile & desktop |
| ✅ **Secure Auth**            | Django-powered signup, login, logout |

---

## 📊 AI-Powered Behavioral Insight (Hugging Face) example
{
  "insight": "You maintained discipline with 5/8 rules followed, leading to a profitable trade.",
  "risk_pattern": "None",
  "discipline_score": 8,
  "coaching_tip": "Keep using your checklist to avoid FOMO entries."
}


💰 Monetization with IntaSend
Unlock full report: KES 50
Features: PDF export, deep pattern audit, voice coaching
Test mode: Use card 4242 4242 4242 4242
✅ African fintech integration — perfect for mobile-first traders.

🛠️ Setup & Run Locally
1.Clone the repo
   git clone https://github.com/sacrid91/TradeMindHackathon2.git
   cd TradeMindHackathon2

2.Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   source venv/Scripts/activate #bash

3.Install Dependancies
   pip install -r requirements.txt

4.Set environment variables
   cp .env.example .env # Edit .env with your keys

5.Run migrations
   python manage.py migrate
   python manage.py createsuperuser

6.Start your server
   python manage.py runserver

7.Open in browser(Ha!Ha!Ha! Pick your poison!!!)

```json

