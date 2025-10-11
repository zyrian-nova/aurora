# Aurora

## Working Directory

The following is the sugested directory tree (subject to changes).

```
aurora/
│
├── backend/
│   ├── Dockerfile
│   ├── main.py                     # FastAPI app entry point
│   ├── pyproject.toml              # PDM dependencies
│   ├── pyrightconfig.json
│   ├── .env.example
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── celery_app.py           # Celery config (at app root)
│   │   │
│   │   ├── settings/
│   │   │   ├── __init__.py
│   │   │   ├── config.py           # Pydantic settings (DB, Redis, JWT secret)
│   │   │   ├── logging.py          # Structured logging
│   │   │   └── security.py         # Password hashing, JWT utilities
│   │   │
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # Tortoise init & TORTOISE_ORM config
│   │   │   └── migrations/         # Aerich migrations
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py             # User model (email, hashed_password, created_at)
│   │   │   ├── daily_cache.py      # Cache for quotes, words, weather
│   │   │   ├── site_status.py      # Website monitoring history
│   │   │   └── user_preferences.py # User settings (language, sites to monitor)
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── router.py           # Main router aggregator
│   │   │   ├── routes_auth.py      # /register, /login, /refresh
│   │   │   ├── routes_daily.py     # /daily (weather, quote, word)
│   │   │   ├── routes_status.py    # /status/check (website monitoring)
│   │   │   ├── routes_news.py      # /news (RSS + Reddit)
│   │   │   └── routes_user.py      # /user/preferences
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth_schema.py      # LoginRequest, TokenResponse, UserCreate
│   │   │   ├── daily_schema.py     # DailyData, WeatherData, WordData
│   │   │   ├── news_schema.py      # NewsItem, FeedSource
│   │   │   └── user_schema.py      # UserPreferences, UserProfile
│   │   │
│   │   ├── services/
│   │   │   ├── external/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── weather_service.py    # OpenWeatherMap/wttr.in
│   │   │   │   ├── rss_service.py        # feedparser for RSS
│   │   │   │   └── reddit_service.py     # PRAW or API calls
│   │   │   │
│   │   │   ├── internal/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── daily_service.py      # Aggregates daily data
│   │   │   │   ├── status_service.py     # Website health checks
│   │   │   │   └── user_service.py       # User CRUD operations
│   │   │   │
│   │   │   └── ai_service.py            # Ollama integration
│   │   │
│   │   ├── tasks/                        # Celery tasks
│   │   │   ├── __init__.py
│   │   │   ├── generate_daily.py         # Refresh quotes/words (daily)
│   │   │   ├── check_sites.py            # Monitor websites (every 5 min)
│   │   │   └── fetch_news.py             # Pull RSS/Reddit (hourly)
│   │   │
│   │   └── middleware/
│   │       ├── __init__.py
│   │       └── auth_middleware.py        # JWT verification dependency
│   │
│   └── tests/
│       ├── __init__.py
│       ├── test_auth.py
│       ├── test_daily.py
│       └── test_services.py
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── .env.example                     # VITE_API_URL
│   │
│   ├── public/
│   │   ├── favicon.ico
│   │   └── backgrounds/                 # Daily rotating backgrounds (Test)
│   │       ├── monday.jpg
│   │       ├── tuesday.jpg
│   │       ├── wednesday.jpg
│   │       ├── thursday.jpg
│   │       ├── friday.jpg
│   │       ├── saturday.jpg
│   │       └── sunday.jpg
│   │
│   └── src/
│       ├── main.jsx                     # React entry point
│       ├── App.jsx                      # Root component with routing
│       ├── index.css                    # Tailwind import
│       │
│       ├── pages/                       # Page components
│       │   ├── Dashboard.jsx            # Main authenticated page
│       │   ├── Login.jsx
│       │   ├── Register.jsx
│       │   └── Settings.jsx
│       │
│       ├── components/
│       │   ├── layout/
│       │   │   ├── Layout.jsx
│       │   │   ├── ProtectedRoute.jsx
│       │   │   └── BackgroundImage.jsx
│       │   │
│       │   └── widgets/
│       │       ├── Clock.jsx
│       │       ├── Quote.jsx
│       │       ├── Weather.jsx
│       │       ├── WordCard.jsx
│       │       ├── NewsWidget.jsx
│       │       └── StatusGrid.jsx
│       │
│       ├── hooks/
│       │   ├── useAuth.js
│       │   ├── useDailyData.js
│       │   ├── useBackgroundImage.js
│       │   └── useFetch.js              # Custom fetch hook
│       │
│       ├── context/
│       │   └── AuthContext.jsx
│       │
│       ├── api/
│       │   ├── client.js                # Fetch wrapper
│       │   ├── auth.js
│       │   ├── daily.js
│       │   ├── news.js
│       │   └── status.js
│       │
│       └── utils/
│           ├── date.js
│           ├── storage.js               # localStorage for JWT
│           └── constants.js
│
├── .gitignore
├── .env.example                         # Global env template
└── README.md
```
