# AI Chatbot — Cloud-Ready (Gemini)

A minimal, production-shaped chatbot: Flask backend + Google Gemini API (free tier) + simple web UI, containerized with Docker so it deploys the same way to AWS, GCP, or Azure.

## Get a free API key
1. Go to https://aistudio.google.com
2. Sign in with your Google account
3. Click **Get API Key** → **Create API Key**
4. Copy the key (starts with `AIza...`)

## 1. Run locally first

```bash
cd ai-chatbot
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export GEMINI_API_KEY=your_key_here
python app.py
```
Visit http://localhost:8080

Or with Docker:
```bash
docker build -t ai-chatbot .
docker run -p 8080:8080 -e GEMINI_API_KEY=your_key_here ai-chatbot
```

## 2. Push the image to a registry

```bash
docker tag ai-chatbot <registry>/ai-chatbot:latest
docker push <registry>/ai-chatbot:latest
```
- AWS: push to ECR (`aws ecr get-login-password | docker login ...`)
- GCP: push to Artifact Registry (`gcloud auth configure-docker`)
- Azure: push to ACR (`az acr login --name <registry>`)

## 3. Deploy — pick your cloud

### AWS (easiest: App Runner)
```bash
aws apprunner create-service \
  --service-name ai-chatbot \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "<ecr-image-uri>",
      "ImageConfiguration": {"Port": "8080", "RuntimeEnvironmentVariables": {"GEMINI_API_KEY":"<your-gemini-key>"}},
      "ImageRepositoryType": "ECR"
    }
  }'
```
Alternative: ECS Fargate or Elastic Beanstalk (Docker platform) if you need more control over networking/scaling.

### GCP (easiest: Cloud Run)
```bash
gcloud run deploy ai-chatbot \
  --image gcr.io/<project-id>/ai-chatbot \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=<your-gemini-key>
```

### Azure (easiest: Container Apps)
```bash
az containerapp up \
  --name ai-chatbot \
  --resource-group <rg> \
  --image <acr-name>.azurecr.io/ai-chatbot:latest \
  --target-port 8080 \
  --ingress external \
  --env-vars GEMINI_API_KEY=<your-gemini-key>
```

## 4. Secrets — do this properly
Never bake the API key into the image. Use:
- AWS: Secrets Manager or App Runner/ECS env vars linked to Secrets Manager
- GCP: Secret Manager, referenced via `--set-secrets`
- Azure: Key Vault, referenced via Container Apps secret references

## 5. Production notes
- **Conversation storage**: currently in-memory (`conversations` dict in `app.py`) — fine for a demo, but resets on restart and won't work across multiple instances. Swap in Redis (ElastiCache/Memorystore/Azure Cache) or a small DB table for real deployments.
- **Scaling**: all three platforms above (App Runner, Cloud Run, Container Apps) autoscale on request volume out of the box.
- **Cost control**: the history trimming in `/api/chat` caps context to the last 20 messages — tune this and `max_tokens` based on your budget.
- **Health check**: `/health` endpoint is included for load balancer checks.
- **HTTPS**: all three managed services above provide HTTPS automatically.

## File structure
```
ai-chatbot/
├── app.py              # Flask backend + Anthropic API integration
├── templates/index.html
├── static/style.css
├── static/script.js
├── requirements.txt
├── Dockerfile
└── README.md
```
