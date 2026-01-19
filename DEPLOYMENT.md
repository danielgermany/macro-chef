# Macro Chef - Deployment Guide

## Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- Environment variables configured (see `.env.example`)

### Development Setup

1. **Start all services:**
```bash
docker-compose up -d
```

2. **Access the application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

3. **View logs:**
```bash
docker-compose logs -f
```

4. **Stop services:**
```bash
docker-compose down
```

## Production Deployment

### Option 1: Railway (Recommended)

1. **Connect Repository:**
   - Go to Railway.app
   - Create new project
   - Connect GitHub repository

2. **Deploy Backend:**
   - Create new service from `backend/` directory
   - Set root directory to `backend`
   - Add environment variables:
     - `DATABASE_URL` (PostgreSQL connection string)
     - `SPOONACULAR_API_KEY`
     - `USDA_API_KEY`
     - `SECRET_KEY` (generate strong secret)
     - `CORS_ORIGINS` (your frontend URL)

3. **Deploy Frontend:**
   - Create new service from `frontend/` directory
   - Set root directory to `frontend`
   - Build command: `npm run build`
   - Start command: `npm run preview` (or use nginx)
   - Add environment variable:
     - `VITE_API_URL` (your backend URL)

4. **Add PostgreSQL:**
   - Add PostgreSQL service
   - Update `DATABASE_URL` in backend service

### Option 2: Render

1. **Backend Service:**
   - Create new Web Service
   - Build command: `cd backend && pip install -r requirements.txt`
   - Start command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Add environment variables

2. **Frontend Service:**
   - Create new Static Site
   - Build command: `cd frontend && npm install && npm run build`
   - Publish directory: `frontend/dist`

3. **PostgreSQL Database:**
   - Create new PostgreSQL database
   - Update `DATABASE_URL` in backend service

### Option 3: Self-Hosted VPS

1. **Install Dependencies:**
```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install nginx
sudo apt-get update
sudo apt-get install nginx certbot python3-certbot-nginx
```

2. **Clone Repository:**
```bash
git clone <your-repo-url>
cd macro-chef
```

3. **Configure Environment:**
```bash
cp .env.example .env
# Edit .env with your values
```

4. **Update docker-compose.yml for Production:**
```yaml
# Use production Dockerfiles
# Add nginx reverse proxy
# Configure SSL
```

5. **Deploy:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

6. **Configure Nginx:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location / {
        proxy_pass http://localhost:5173;
    }
}
```

7. **Set up SSL:**
```bash
sudo certbot --nginx -d your-domain.com
```

## Database Migration

### SQLite to PostgreSQL

1. **Export SQLite data:**
```bash
sqlite3 database/meal_planner.db .dump > backup.sql
```

2. **Create PostgreSQL database:**
```bash
createdb macrochef
```

3. **Import schema:**
```bash
psql macrochef < backup.sql
```

4. **Update DATABASE_URL:**
```bash
export DATABASE_URL=postgresql://user:password@localhost/macrochef
```

## Environment Variables

### Backend
- `DATABASE_URL` - Database connection string
- `SPOONACULAR_API_KEY` - Spoonacular API key
- `USDA_API_KEY` - USDA API key (optional)
- `SECRET_KEY` - JWT secret key (generate with: `openssl rand -hex 32`)
- `CORS_ORIGINS` - Comma-separated list of allowed origins
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration (default: 30)

### Frontend
- `VITE_API_URL` - Backend API URL (default: http://localhost:8000)

## Monitoring

### Health Checks

- Backend: `GET /health`
- Frontend: Check if app loads

### Logs

```bash
# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Application logs
# Check application logs in your hosting platform
```

## Troubleshooting

### Backend won't start
- Check database connection
- Verify environment variables
- Check port availability (8000)

### Frontend can't connect to backend
- Verify `VITE_API_URL` is correct
- Check CORS settings
- Ensure backend is running

### Database errors
- Verify database connection string
- Check database permissions
- Ensure migrations are run

## Security Checklist

- [ ] Change default `SECRET_KEY`
- [ ] Use strong passwords
- [ ] Enable HTTPS in production
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Regular security updates
- [ ] Database backups
- [ ] Environment variables secured
