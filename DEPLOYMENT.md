# 🌍 Earthquake Prediction API - Production Deployment Guide

## 📋 Overview

This guide covers deploying the Earthquake Prediction API to production using Docker and GitHub Actions.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- GitHub repository with appropriate permissions
- Production server with SSH access
- ML model artifacts trained and available

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit with your production values
nano .env
```

### 2. Local Testing

```bash
# Test production build locally
docker-compose up --build

# Check health endpoint
curl http://localhost:8000/health
```

### 3. Production Deployment

#### Option A: Docker Compose (Recommended)
```bash
# Deploy to production server
scp docker-compose.yml user@your-server:/opt/earthquake-prediction/
scp .env user@your-server:/opt/earthquake-prediction/

# SSH into server and deploy
ssh user@your-server
cd /opt/earthquake-prediction
chmod +x start_production.sh
./start_production.sh
```

#### Option B: GitHub Actions (Automated)
1. Set up GitHub Secrets:
   - `PROD_HOST`: Your production server IP
   - `PROD_USER`: SSH username
   - `PROD_SSH_KEY`: SSH private key

2. Push to main branch:
```bash
git add .
git commit -m "Production deployment setup"
git push origin main
```

## 🔧 Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `false` |
| `HOST` | Bind address | `0.0.0.0` |
| `PORT` | Application port | `8000` |
| `WORKERS` | Gunicorn workers | `4` |
| `DATABASE_URL` | Database connection | `sqlite:///./earthquake_data.db` |
| `CORS_ORIGINS` | Allowed origins | `*` |
| `SECRET_KEY` | Security key | Required |

### Health Checks
- **Endpoint**: `/health`
- **Method**: GET
- **Response**: JSON with service status
- **Interval**: 30 seconds

## 🐳 Docker Configuration

### Production Image
- **Base**: Python 3.11-slim
- **Size**: Optimized for production
- **Security**: Non-root user
- **Health**: Built-in health checks

### Container Features
- **Multi-stage build** for smaller image size
- **Health checks** with automatic restart
- **Volume mounting** for data persistence
- **Environment isolation** for security

## 📊 Monitoring

### Application Logs
```bash
# View real-time logs
docker-compose logs -f earthquake-api

# Check specific errors
docker-compose logs earthquake-api | grep ERROR
```

### Performance Metrics
- **Response time**: Monitor API latency
- **Memory usage**: Track container resources
- **Error rates**: Monitor 5xx responses
- **Database queries**: Monitor slow queries

## 🔒 Security

### Production Security
- **HTTPS**: Configure SSL/TLS termination
- **Firewall**: Only expose necessary ports
- **Updates**: Regular security patches
- **Secrets**: Use environment variables, not hardcoding

### CORS Configuration
```python
# Production CORS setup
origins = [
    "https://yourdomain.com",
    "https://www.yourdomain.com"
]
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Model Not Found
```
Error: FileNotFoundError: earthquake_model.pkl
```
**Solution**: Train the ML model first using `python app/ml/train_model.py`

#### 2. Database Connection Failed
```
Error: sqlalchemy.exc.OperationalError
```
**Solution**: Check DATABASE_URL and permissions

#### 3. Port Already in Use
```
Error: Address already in use
```
**Solution**: Kill existing processes or change PORT

#### 4. High Memory Usage
```
Error: Container OOM killed
```
**Solution**: Reduce WORKERS or increase server memory

### Health Check Responses
```json
// Healthy
{
  "status": "healthy",
  "model": "available",
  "timestamp": "2024-01-01T12:00:00Z"
}

// Degraded
{
  "status": "degraded",
  "model": "unavailable",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 📈 Scaling

### Horizontal Scaling
```yaml
# docker-compose.yml for multiple instances
version: '3.8'
services:
  earthquake-api-1:
    <<: *earthquake-api
  earthquake-api-2:
    <<: *earthquake-api
    environment:
      - PORT=8001
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### Load Balancer Configuration
```nginx
upstream earthquake_api {
    server earthquake-api-1:8000;
    server earthquake-api-2:8001;
}

server {
    listen 80;
    location / {
        proxy_pass http://earthquake_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
1. **Test**: Run automated tests
2. **Build**: Create Docker image
3. **Push**: Deploy to registry
4. **Deploy**: Update production server

### Manual Deployment
```bash
# Update production
git pull origin main
docker-compose down
docker-compose pull
docker-compose up -d
```

## 📞 Support

### Monitoring Services
- **Application logs**: Docker logs
- **Server metrics**: htop, iostat
- **Network monitoring**: netstat, ss
- **Database performance**: SQLite EXPLAIN QUERY PLAN

### Emergency Procedures
1. **Rollback**: Use previous Docker image
2. **Scale down**: Reduce worker count
3. **Maintenance mode**: Return 503 responses
4. **Data backup**: Export SQLite database

---

## 🎯 Production Checklist

- [ ] ML models trained and available
- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Firewall rules configured
- [ ] Monitoring set up
- [ ] Backup procedures documented
- [ ] Load testing completed
- [ ] Security audit performed

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Production Deployment Guide](https://docs.github.com/en/actions/deployment)

---

**🎉 Your Earthquake Prediction API is now ready for production deployment!**
