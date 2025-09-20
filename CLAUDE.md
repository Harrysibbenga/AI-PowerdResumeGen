# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered resume generator built with Astro + Vue frontend and FastAPI backend. Users authenticate via Firebase, generate resumes using GPT/DeepSeek AI, and export to PDF/DOCX formats with Stripe payment integration.

## Development Commands

### Frontend (Astro + Vue)
```bash
cd frontend
npm install
npm run dev      # Start development server
npm run build    # Build for production  
npm run preview  # Preview production build
```

### Backend (FastAPI)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload  # Start development server
```

Alternative: Use `./run.sh` script in backend directory.

## Architecture

### Backend Structure
- **FastAPI app** with modular router organization
- **Firebase Firestore** for data persistence and authentication
- **AI Services**: GPT (OpenAI) and DeepSeek for content generation
- **Export Services**: PDF (WeasyPrint) and DOCX generation
- **Stripe Integration** for payments and subscriptions

Key directories:
- `app/routes/` - API endpoints (auth, resume, payments)
- `app/models/` - Pydantic models and enums
- `app/services/` - Business logic (AI generation, exports, email)
- `app/core/` - Configuration and Firebase setup

### Frontend Structure  
- **Astro** as static site generator with **Vue** components
- **Firebase Auth** for authentication
- **Tailwind CSS** for styling
- **Vue composables** for state management

Key directories:
- `src/components/vue/` - Vue components organized by feature
- `src/lib/` - Client classes (AuthClient, ResumeClient)
- `src/composables/` - Reusable Vue composition functions
- `src/utils/` - Utility functions and API configuration

### Data Flow
1. User authenticates via Firebase Auth
2. Frontend sends resume data to FastAPI backend
3. Backend validates, processes with AI service (GPT/DeepSeek)
4. Resume stored in Firestore with user association
5. Export functionality generates PDF/DOCX via backend services

### Key Models and Enums
- `ExportFormat`: PDF, DOCX
- `ResumeTone`: Professional, Creative, Formal, Casual  
- `ResumeTemplate`: Modern, Classic, Creative, Minimal, Executive
- `SubscriptionPlan`: Free, Premium, Enterprise

### Authentication Flow
- Firebase handles user authentication
- Backend validates tokens via Firebase Admin SDK
- User sessions managed through Firebase Auth state
- Protected routes use `get_current_user` dependency

### AI Integration
- Primary: DeepSeek API (if configured)
- Fallback: OpenAI GPT API
- Content generation based on user profile data and preferences
- Configurable tone, length, and template selection

## Environment Variables

Backend `.env` required:
- `OPENAI_API_KEY` - OpenAI API key
- `DEEPSEEK_API_KEY` - DeepSeek API key  
- `STRIPE_SECRET_KEY` - Stripe secret key
- `FIREBASE_SERVICE_ACCOUNT_PATH` - Path to Firebase service account JSON
- `SMTP_USERNAME` - Email service configuration

## Database Schema

Firestore collections:
- `users/` - User profiles and subscription data
- `resumes/` - Generated resume documents with metadata
- `sessions/` - User session management

## Testing and Linting

No specific test commands found in package.json. Check with user for testing setup.