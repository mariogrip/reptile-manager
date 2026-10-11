# Contributing

Thanks for your interest. PRs and issues are welcome.

## Setting up a development environment

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

DATABASE_URL=sqlite:///./dev.db \
FIRST_ADMIN_USERNAME=admin \
FIRST_ADMIN_PASSWORD=admin123 \
SECRET_KEY=dev-key-not-for-production \
uvicorn app.main:app --reload
```

The API is then available at http://localhost:8000/api/docs

**Frontend:**
```bash
cd frontend
npm install
VITE_API_URL=http://localhost:8000/api npm run dev
```

## Adding a new language

See `frontend/src/i18n/ADDING_LANGUAGES.md`

## Code style

Nothing special – Python with type hints where it makes sense, Vue 3 Composition API.
Commit messages describe what changed, not why (that goes in the PR description).

## What's welcome

- Bug fixes with reproduction steps in the issue
- Translations (missing languages or corrections)
- Improvements I'd probably have needed myself at some point

## What's less likely to fit

- Complete architecture rewrites without prior discussion
- Dependencies that are only needed for a small feature
