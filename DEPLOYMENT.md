# Deployment

## Run locally

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app opens at http://localhost:8501.

## Streamlit Community Cloud (free)

1. Push this folder to a GitHub repository.
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Choose **New app**, select your repository, branch `main` and the main file `app.py`.
4. Click **Deploy**. The dataset in `data/vivaan_shipments.csv` is part of the repository, so no extra setup is needed.

## Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
```

```bash
docker build -t vivaan-dashboard .
docker run -p 8501:8501 vivaan-dashboard
```
