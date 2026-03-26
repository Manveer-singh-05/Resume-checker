# Deployment Guide

## Production Deployment Options

### Option 1: Linux VPS / Cloud Server (Recommended)

#### Prerequisites

- SSH access to server
- Linux (Ubuntu recommended)
- Domain/IP address
- 512MB RAM minimum

#### Deployment Steps

1. **SSH into your server**

   ```bash
   ssh user@your_server_ip
   ```

2. **Install dependencies**

   ```bash
   sudo apt update
   sudo apt install python3.9 python3-pip python3-venv git
   ```

3. **Clone repository**

   ```bash
   git clone <your-repo-url>
   cd resume_analyzer_bot
   ```

4. **Setup Python environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Configure environment**

   ```bash
   nano .env
   # Add your credentials
   ```

6. **Create systemd service** (auto-start and restart)

   ```bash
   sudo tee /etc/systemd/system/resume-bot.service > /dev/null <<EOF
   [Unit]
   Description=Resume Analyzer Bot
   After=network.target

   [Service]
   Type=simple
   User=$USER
   WorkingDirectory=$(pwd)
   Environment="PATH=$(pwd)/venv/bin"
   ExecStart=$(pwd)/venv/bin/python bot.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   EOF
   ```

7. **Enable and start service**

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable resume-bot
   sudo systemctl start resume-bot
   ```

8. **Check status**
   ```bash
   sudo systemctl status resume-bot
   sudo journalctl -u resume-bot -f  # View logs
   ```

---

### Option 2: Docker Deployment

#### Prerequisites

- Docker installed
- Docker Compose installed
- .env file configured

#### Steps

1. **Build Docker image**

   ```bash
   docker build -t resume-analyzer-bot:latest .
   ```

2. **Run with Docker Compose**

   ```bash
   docker-compose up -d
   ```

3. **View logs**

   ```bash
   docker-compose logs -f resume-analyzer-bot
   ```

4. **Stop service**
   ```bash
   docker-compose down
   ```

#### Docker Hub (Optional - Share your image)

```bash
# Login to Docker Hub
docker login

# Tag image
docker tag resume-analyzer-bot:latest yourname/resume-analyzer-bot:latest

# Push
docker push yourname/resume-analyzer-bot:latest
```

---

### Option 3: AWS Lambda + API Gateway

#### Setup for Webhook-based deployment

1. **Create Lambda function**
   - Runtime: Python 3.9
   - Upload code as ZIP

2. **Set webhook URL** in bot configuration:

   ```python
   webhook_url = "https://your-api-gateway-url/webhook"
   ```

3. **Configure for Lambda**

   ```python
   # Use this in bot.py for Lambda
   from mangum import Mangum

   app = application
   handler = Mangum(app)
   ```

4. **Deploy with Serverless Framework**
   ```bash
   npm install -g serverless
   serverless deploy
   ```

---

### Option 4: Heroku Deployment

#### Prerequisites

- Heroku account (free tier available)
- Heroku CLI installed

#### Steps

1. **Login to Heroku**

   ```bash
   heroku login
   ```

2. **Create Heroku app**

   ```bash
   heroku create resume-analyzer-bot
   ```

3. **Add buildpack**

   ```bash
   heroku buildpacks:add heroku/python
   ```

4. **Set environment variables**

   ```bash
   heroku config:set TELEGRAM_BOT_TOKEN=your_token
   heroku config:set OPENAI_API_KEY=your_key
   ```

5. **Create Procfile**

   ```
   worker: python bot.py
   ```

6. **Deploy**

   ```bash
   git push heroku main
   ```

7. **View logs**
   ```bash
   heroku logs --tail
   ```

---

### Option 5: DigitalOcean App Platform

1. **Connect GitHub repository**
2. **Create app from repository**
3. **Set environment variables**
4. **Configure App Spec**:
   ```yaml
   name: resume-analyzer-bot
   services:
     - name: bot
       github:
         repo: your/repo
         branch: main
       build_command: pip install -r requirements.txt
       run_command: python bot.py
       envs:
         - key: TELEGRAM_BOT_TOKEN
           value: ${TELEGRAM_BOT_TOKEN}
   ```
5. **Deploy**

---

## Monitoring & Maintenance

### Log Monitoring

```bash
# Systemd service
sudo journalctl -u resume-bot -n 50  # Last 50 lines

# Docker
docker-compose logs -f

# Heroku
heroku logs --tail
```

### Auto-restart Configuration

```bash
# Systemd automatically restarts (configured in service file)
# Docker: Set restart policy in compose
# Heroku: Apps restart if dynos crash
```

### Health Check Script

```bash
#!/bin/bash
# health_check.sh

BOT_STATUS=$(systemctl is-active resume-bot)

if [ "$BOT_STATUS" != "active" ]; then
    echo "Bot down! Restarting..."
    sudo systemctl restart resume-bot
fi
```

### Scheduled Cleanup

```bash
# Add to crontab for cleanup every day at 2 AM
0 2 * * * cd /app && python -c "from modules.pdf_generator import PDFGenerator; PDFGenerator().cleanup_temp_files()"
```

---

## SSL Certificate Setup

### For VPS with Nginx

1. **Install Certbot**

   ```bash
   sudo apt install certbot python3-certbot-nginx
   ```

2. **Get certificate**

   ```bash
   sudo certbot certonly --standalone -d your-domain.com
   ```

3. **Configure Nginx**

   ```nginx
   server {
       listen 443 ssl;
       server_name your-domain.com;

       ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

       # ... rest of config
   }
   ```

4. **Auto-renewal**
   ```bash
   sudo systemctl enable certbot.timer
   ```

---

## Load Balancing (Multiple Instances)

### Using Nginx

```nginx
upstream resume_bot_backend {
    server bot1.example.com:8000;
    server bot2.example.com:8000;
    server bot3.example.com:8000;
}

server {
    listen 80;
    server_name api.example.com;

    location /webhook/ {
        proxy_pass http://resume_bot_backend;
    }
}
```

---

## Database Setup (for production user data)

### PostgreSQL Setup

```bash
# Install
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb resume_analyzer_db

# Create user
sudo -u postgres createuser -P resume_user
```

### Connection in Python

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="resume_analyzer_db",
    user="resume_user",
    password="your_password"
)
```

---

## Performance Optimization

### Redis Caching

```bash
# Install
sudo apt install redis-server

# Use in Python
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
r.set('key', value, ex=3600)  # 1 hour expiry
```

### CDN for PDF Downloads

```python
# Use AWS S3 or Cloudflare for PDF distribution
import boto3
s3 = boto3.client('s3')
s3.upload_file('resume.pdf', 'bucket-name', 'resume.pdf')
```

---

## Disaster Recovery

### Backup Strategy

```bash
# Backup script
#!/bin/bash
BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup code
tar -czf $BACKUP_DIR/bot_$TIMESTAMP.tar.gz .

# Upload to S3
aws s3 cp $BACKUP_DIR/bot_$TIMESTAMP.tar.gz s3://backup-bucket/
```

### Database Backup

```bash
# PostgreSQL backup
pg_dump resume_analyzer_db > backup.sql

# Restore
psql resume_analyzer_db < backup.sql
```

---

## Troubleshooting Production Issues

### Bot stops responding

```bash
# Check process
ps aux | grep bot.py

# Restart
sudo systemctl restart resume-bot

# Check logs
sudo journalctl -u resume-bot -n 100
```

### Memory leak

```bash
# Monitor memory
free -h

# Set memory limit (Docker)
docker-compose.yml - add:
  deploy:
    resources:
      limits:
        memory: 512M
```

### API rate limits

```python
# Add retry with backoff
import time
from telegram.error import RetryAfter

def handle_rate_limit(func):
    def wrapper(*args, **kwargs):
        for attempt in range(3):
            try:
                return func(*args, **kwargs)
            except RetryAfter as e:
                time.sleep(e.retry_after + 1)
    return wrapper
```

---

## Scaling Strategy

### Horizontal Scaling (Multiple Instances)

1. Set up load balancer
2. Run multiple bot instances
3. Use Redis for state management

### Vertical Scaling (Single instance upgrade)

1. Increase server resources (CPU, RAM)
2. Optimize code
3. Use caching

---

## Upgrade Strategy

### Zero-downtime deployment

```bash
# Create new service
sudo systemctl start resume-bot-new

# Verify health
sleep 30

# Switch traffic
sudo systemctl stop resume-bot
sudo systemctl start resume-bot-new

# Cleanup old
sudo systemctl disable resume-bot
```

---

## Support & Monitoring Tools

**Recommended:**

- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Error Tracking**: Sentry
- **Uptime Check**: Uptimerobot or Pingdom

---

## Costs Estimate (Monthly)

| Component                   | Cost                 |
| --------------------------- | -------------------- |
| VPS (1GB RAM)               | $5-10                |
| Domain                      | $1-3                 |
| SSL Certificate             | Free (Let's Encrypt) |
| OpenAI API                  | ~$5-50\*             |
| Google Cloud Storage (PDFs) | ~$1-2                |
| **Total**                   | **~$15-65**          |

\*Depends on usage volume

---

For questions or deployment help, refer to the main README.md file.
