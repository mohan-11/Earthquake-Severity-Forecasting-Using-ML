# 🌍 Earthquake Prediction API - Render.com Deployment Guide

## 📋 Overview

Complete guide for deploying your earthquake prediction API on Render.com with Docker containerization.

## 🚀 Quick Start

### Prerequisites
- [x] GitHub repository with production-ready code
- [x] Render.com account (Free tier available)
- [x] Trained ML models (.pkl files)
- [x] Docker configuration files

---

## 📁 Step-by-Step Deployment

### **Step 1: Prepare Your Repository**

Ensure your GitHub repository contains:
```bash
# Verify essential files
ls -la
✅ Dockerfile
✅ requirements.txt
✅ render.yaml
✅ app/main.py
✅ earthquake_model.pkl
✅ label_encoder.pkl
✅ location_kmeans.pkl
✅ depth_encoder.pkl
```

### **Step 2: Create Render Account**

1. Go to [Render.com](https://render.com)
2. Sign up with GitHub (recommended)
3. Connect your GitHub account
4. Select **Free plan** to start

### **Step 3: Create New Web Service**

#### **Option A: Using render.yaml (Recommended)**

1. **Create New Service** → **Web Service**
2. **Connect Repository**: Select `Earthquake-Severity-Forecasting-Using-ML`
3. **Branch**: `master`
4. **Root Directory**: `/`
5. **Runtime**: **Docker**
6. **Instance Type**: **Free**
7. **Auto-Deploy**: ✅ Enabled

#### **Option B: Manual Configuration**

1. **Service Name**: `earthquake-api`
2. **Environment**: **Docker**
3. **Dockerfile Path**: `./Dockerfile.render`
4. **Build Command**: (Auto-detected)
5. **Start Command**: (Auto-detected)

### **Step 4: Configure Environment Variables**

#### **Required Environment Variables**

| Variable | Value | Description |
|-----------|---------|-------------|
| `DEBUG` | `false` | Production mode |
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `10000` | Render's port |
| `WORKERS` | `1` | Free tier limit |
| `DATABASE_URL` | `sqlite:///./earthquake_data.db` | SQLite database |
| `CORS_ORIGINS` | `https://your-service.onrender.com` | Your domain |
| `SECRET_KEY` | Auto-generated | Security key |
| `FETCH_INTERVAL_SECONDS` | `300` | 5 minutes |
| `LOG_LEVEL` | `info` | Logging level |

#### **Render-Specific Variables**
```bash
# Render automatically provides:
RENDER_EXTERNAL_URL=https://your-service.onrender.com
RENDER_EXTERNAL_HOSTNAME=your-service.onrender.com
```

### **Step 5: Deploy the Service**

1. **Create Service** button
2. Wait for **Build & Deploy** (2-5 minutes)
3. **Monitor Logs** for any errors
4. **Test Health Endpoint**: `https://your-service.onrender.com/health`

---

## 🔧 Advanced Configuration

### **Database Options**

#### **Option A: SQLite (Default)**
```yaml
# render.yaml
envVars:
  - key: DATABASE_URL
    value: sqlite:///./earthquake_data.db
```

#### **Option B: PostgreSQL (Production)**
```yaml
# Add to render.yaml
- type: pserv
  name: earthquake-db
  runtime: image
  image:
    url: postgres:15
  plan: free
  envVars:
    - key: POSTGRES_DB
      value: earthquake_db
    - key: POSTGRES_USER
      value: postgres
    - key: POSTGRES_PASSWORD
      generateValue: true
```

### **Custom Domain Setup**

1. Go to **Service Settings** → **Custom Domains**
2. Add your domain: `api.yourdomain.com`
3. Update DNS records:
   ```
   Type: CNAME
   Name: api
   Value: your-service.onrender.com
   ```

### **Health Monitoring**

#### **Health Check Configuration**
```yaml
# render.yaml
healthCheckPath: /health
```

#### **Health Endpoint Response**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0",
  "environment": "production"
}
```

---

## 📊 Monitoring & Logs

### **Access Logs**
```bash
# Render Dashboard → Your Service → Logs
# View real-time application logs
# Monitor for errors and performance issues
```

### **Performance Metrics**
- **Response Time**: Monitor API latency
- **Memory Usage**: Free tier 512MB limit
- **CPU Usage**: Free tier CPU limits
- **Database Queries**: Monitor slow queries

### **Alerts Setup**
1. **Service Settings** → **Alerts**
2. Configure:
   - **Service Down**: Email notifications
   - **High Response Time**: >5 seconds
   - **Error Rate**: >5%

---

## 🔄 CI/CD Integration

### **Automatic Deployments**
```yaml
# render.yaml ensures auto-deployment
# Push to master branch → Auto-deploy
# Pull requests → Preview deployments
```

### **GitHub Actions Alternative**
```yaml
# .github/workflows/render-deploy.yml
name: Deploy to Render
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Render
        uses: johnbeynon/render-deploy-action@v0.0.8
        with:
          service-id: ${{ secrets.RENDER_SERVICE_ID }}
          api-key: ${{ secrets.RENDER_API_KEY }}
```

---

## 🚨 Troubleshooting

### **Common Issues**

#### **1. Build Failures**
```
Error: ModuleNotFoundError: No module named 'pandas'
```
**Solution**: Check `requirements.txt` and Dockerfile

#### **2. Health Check Failures**
```
Error: Service unhealthy
```
**Solution**: Verify `/health` endpoint works locally

#### **3. CORS Errors**
```
Error: Access-Control-Allow-Origin
```
**Solution**: Update `CORS_ORIGINS` with your Render URL

#### **4. Database Issues**
```
Error: sqlite3.OperationalError
```
**Solution**: Check database file permissions

#### **5. Memory Issues**
```
Error: Container killed due to memory limit
```
**Solution**: Reduce `WORKERS` to 1 for free tier

### **Debug Commands**
```bash
# Test locally with Render environment
docker build -f Dockerfile.render -t earthquake-api .
docker run -p 10000:10000 --env-file .env earthquake-api

# Check health endpoint
curl https://your-service.onrender.com/health

# View logs in real-time
# Render Dashboard → Service → Logs
```

---

## 📈 Scaling & Performance

### **Free Tier Limits**
- **RAM**: 512MB
- **CPU**: Shared
- **Bandwidth**: 100GB/month
- **Build Time**: 15 minutes
- **Sleep**: After 15 minutes inactivity

### **Paid Plans**
- **Starter**: $7/month (1GB RAM, dedicated CPU)
- **Standard**: $25/month (2GB RAM, dedicated CPU)
- **Pro**: $100/month (4GB RAM, dedicated CPU)

### **Performance Optimization**
```python
# app/main.py optimizations
- Use connection pooling
- Implement caching
- Optimize database queries
- Use async/await properly
```

---

## 🎯 Production Checklist

### **Pre-Deployment**
- [ ] All ML models trained and committed
- [ ] Environment variables configured
- [ ] Health endpoint working locally
- [ ] Docker build successful
- [ ] CORS configured for production domain

### **Post-Deployment**
- [ ] Service responds to health checks
- [ ] API endpoints accessible
- [ ] ML predictions working
- [ ] Database connected
- [ ] Logs showing normal operation
- [ ] Monitoring configured

### **Security**
- [ ] HTTPS enabled (automatic on Render)
- [ ] Environment variables secured
- [ ] No sensitive data in repository
- [ ] CORS properly configured
- [ ] Rate limiting implemented

---

## 🌐 Live Deployment

Once deployed, your API will be available at:
```
https://your-service-name.onrender.com
```

### **API Endpoints**
- **Health**: `GET /health`
- **Live Data**: `GET /earthquakes/live`
- **History**: `GET /earthquakes/history`
- **Prediction**: `POST /predict/custom`
- **Model Info**: `GET /predict/model-info`
- **Docs**: `GET /docs` (if DEBUG=true)

---

## 📞 Support

### **Render Documentation**
- [Official Docs](https://render.com/docs)
- [Docker Guide](https://render.com/docs/docker)
- [Environment Variables](https://render.com/docs/environment-variables)

### **Community Support**
- [Render Community](https://community.render.com)
- [GitHub Issues](https://github.com/render-community)

---

## 🎉 Success!

Your earthquake prediction API is now live on Render.com with:
- ✅ **Automatic HTTPS** security
- ✅ **Zero-downtime** deployments
- ✅ **Built-in monitoring**
- ✅ **Scalable infrastructure**
- ✅ **Global CDN** distribution

**Next Steps**:
1. Test all API endpoints
2. Monitor performance metrics
3. Set up custom domain
4. Configure alerts
5. Scale as needed

---

**🚀 Your earthquake prediction system is now production-ready on Render.com!**
