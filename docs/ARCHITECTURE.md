# Architecture

## High-level flow

```
User uploads resume
    │
    ▼
PyPDF2/python-docx → raw text
    │
    ▼
ai/analyzer.py → OpenAI/Gemini → {skills, experience, ATS score, ...}
    │
    ▼
MongoDB: resumes collection (one active per user)
```

```
User searches "Software engineer in Bangalore"
    │
    ▼
backend/routes/jobs.py → automation/job_search.py
    │
    ▼ (parallel)
LinkedIn  Indeed  Naukri  Internshala  Wellfound  Foundit
    │       │       │       │           │          │
    └───────┴───────┴───────┴───────────┴──────────┘
                          │
                          ▼
              ai/matcher.py → score each (concurrency = 4)
                          │
                          ▼
                  Sorted JobMatch list → UI
```

```
User clicks "Apply" / Auto mode kicks in
    │
    ▼
automation/apply.py → adapter.apply_to_job()
    │
    ▼
1. ai/cover_letter.py → personalized letter
2. Playwright opens job page (persistent context)
3. Find form fields → ai/answer_generator.py for each
4. Random delays + human typing
5. Submit
    │
    ▼
MongoDB: applications collection
    │
    ▼
Optionally: Telegram + Email notification
```

## Why these choices

| Choice | Why |
|---|---|
| FastAPI | Async, auto OpenAPI docs, Pydantic validation, fast |
| MongoDB (Motor) | Flexible schema for jobs/resumes; async driver |
| Playwright (not Selenium) | Faster, modern, better stealth options, single API |
| OpenAI + Gemini both | Vendor flexibility; users pick via env var |
| React + Vite | Fast dev loop, modern, ecosystem |
| Tailwind | Consistent design system without custom CSS |
| Framer Motion | Smooth, performant micro-animations |
| Recharts | Lightweight, composable charts |
| APScheduler | Embedded scheduler — no extra services needed |

## Anti-ban strategy

1. **Persistent browser contexts** per platform → cookies, localStorage, fingerprint persist
2. **Random user-agent** rotation from a desktop pool
3. **`navigator.webdriver` stripped** + plugin/languages spoofed
4. **Random delays**: 800-2500ms reads, 50-180ms keypress, 30-90s between applications
5. **Mouse jitter** before clicks (small bezier-like move)
6. **Concurrent apply cap** = 1 (sequential to look natural)
7. **Daily limit** (default 20) per user
8. **CAPTCHA detection hook** in each adapter — caller can prompt user

## Extension points

- **New platform** → subclass `BasePlatformAdapter`, register in `automation/platforms/__init__.py`
- **New AI model** → subclass `AIProvider` in `ai/provider.py`, switch via `AI_PROVIDER` env
- **New notification channel** → add async fn in `backend/app/notifications.py`
- **Custom matchers** → drop into `ai/matcher.py`
