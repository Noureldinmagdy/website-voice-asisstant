backend:
    - cd backend
    - uv sync (only once)
    - uv run agent.py dev
    - uv run backend.py

popup_front:
    - cd popup_front
    - pnpm install (only once)
    - pnpm build-embed-popup-script (every time you edit the script)
    - pnpm dev 

user_website:
    - cd user_website
    - npm install (only once)
    - npm run dev
    