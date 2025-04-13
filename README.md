# 🧠 AI-Powered Niche Resume Generator

An AI-powered resume and cover letter generator designed for freelancers and professionals in niche industries such as cybersecurity, ethical hacking, and legal tech.


```markdown

Built with:
- ⚡ Astro + Vue (Frontend)
- 🚀 FastAPI + GPT/DeepSeek-AI (Backend)
- 🔐 Firebase Auth (Authentication)
- 💰 Stripe (Payments)

---

## ✨ Features

- Login with Firebase (Google or email)
- Interactive resume builder with Vue
- GPT/DeepSeek-AI generated resume content
- PDF and Word export capabilities
- Optional AI-generated cover letters
- Stripe integration for one-time and subscription payments
- Downloadable industry-specific cheat sheets
- Admin-free scalable deployment setup

---

## 🧱 Project Structure

resume-generator/
├── backend/        # FastAPI app with GPT + Stripe integration
├── frontend/       # Astro + Vue app with interactive UI
├── shared/         # Common utils and constants
├── firebase/       # Firebase Auth config
├── stripe/         # Stripe webhook and helper scripts
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/resume-generator.git
cd resume-generator
```

### 2. Frontend Setup (Astro + Vue)

```bash
cd frontend
npm install
npm run dev
```

### 3. Backend Setup (FastAPI)

```bash
cd backend
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 4. Firebase Setup

- Create a Firebase project
- Enable Authentication (Google + Email/Password)
- Add your Firebase config to `/firebase/init.js`

### 5. Stripe Setup

- Create a Stripe account
- Get your API keys and add them to your backend `.env`
- Set up a webhook endpoint (see `stripe/webhook.py`)

---

## 🛠️ Environment Variables

`.env` (Backend)

```
OPENAI_API_KEY=...
DEEPSEEK_API_KEY=...
STRIPE_SECRET_KEY=...
STRIPE_WEBHOOK_SECRET=...
FIREBASE_PROJECT_ID=...
FIREBASE_AUTH_DOMAIN=...
```

---

## 📦 Deployment

Recommended platforms:
- Frontend: Vercel / Netlify
- Backend: Railway / Fly.io / Render
- Firebase Hosting (Optional) for unified domain
- Stripe Webhooks: ngrok or hosted endpoint

---

## 📌 Roadmap

- [x] Resume generation via GPT
- [x] Stripe integration
- [x] Auth with Firebase
- [ ] Resume template selector
- [ ] Job-tailoring AI assistant
- [ ] Interview prep tool
- [ ] LinkedIn auto-fill

---

## 📃 License

MIT License © 2025 Harry Sibbenga

---