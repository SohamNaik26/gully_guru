# GullyGuru Deployment Guide

## Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- PostgreSQL 13+
- Docker and Docker Compose (optional)

## Environment Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/gullyguru.git
   cd gullyguru
   ```

2. **Install dependencies**

   ```bash
   npm run install:all
   pipenv install
   ```

3. **Set up environment variables**
   - Copy `.env.example` to `.env` for backend
   - Copy `frontend/.env.production` to `frontend/.env.local` for frontend
   - Update all environment variables with production values

## Production Deployment

### Option 1: Manual Deployment

1. **Build the frontend**

   ```bash
   npm run build
   ```

2. **Start the services**
   ```bash
   npm run start
   ```

### Option 2: Docker Deployment

1. **Build and start containers**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build
   ```

## Environment Variables

### Frontend (.env.production)

- `NEXTAUTH_SECRET`: Generate using `openssl rand -base64 32`
- `NEXTAUTH_URL`: Your production domain
- `GOOGLE_CLIENT_ID`: From Google Cloud Console
- `GOOGLE_CLIENT_SECRET`: From Google Cloud Console
- `NEXT_PUBLIC_API_URL`: Backend API URL
- `NEXT_PUBLIC_USE_MOCK_DATA`: Set to false in production

### Backend (.env)

- `DATABASE_URL`: PostgreSQL connection string
- `TELEGRAM_BOT_TOKEN`: Production bot token
- `DEFAULT_TELEGRAM_CHAT_ID`: Production chat ID

## Security Checklist

- [ ] Generate new secure NEXTAUTH_SECRET
- [ ] Set up production Google OAuth credentials
- [ ] Configure SSL/TLS certificates
- [ ] Set up proper CORS policies
- [ ] Enable rate limiting
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy

## Monitoring and Maintenance

1. **Health Checks**

   - Frontend: `https://your-domain.com/api/health`
   - Backend: `https://api.your-domain.com/health`

2. **Logs**

   - Frontend: Check Next.js build logs
   - Backend: Check Python application logs

3. **Backup**
   - Regular database backups
   - Environment configuration backups

## Troubleshooting

Common issues and solutions:

1. **Database Connection Issues**

   - Check PostgreSQL connection string
   - Verify database user permissions
   - Check network connectivity

2. **Authentication Issues**

   - Verify Google OAuth configuration
   - Check NEXTAUTH_URL setting
   - Verify session configuration

3. **API Issues**
   - Check CORS configuration
   - Verify API URL configuration
   - Check server logs for errors

## Support

For deployment support:

1. Check the troubleshooting guide
2. Review server logs
3. Contact the development team
