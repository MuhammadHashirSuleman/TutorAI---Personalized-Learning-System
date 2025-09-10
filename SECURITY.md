# Security Guidelines

## Environment Variables

### ⚠️ IMPORTANT: Never commit actual `.env` files!

This project uses environment variables to store sensitive configuration data like API keys, database passwords, and secret keys.

### Setup Instructions

1. **Copy the example files:**
   ```bash
   # Backend
   cp backend/.env.example backend/.env
   
   # Frontend  
   cp frontend/.env.example frontend/.env
   ```

2. **Fill in your actual values:**
   - Replace all placeholder values with your actual API keys, passwords, etc.
   - Never share these files or commit them to version control

### Files Structure

- `.env` files → **Contains real sensitive data** (NEVER commit)
- `.env.example` files → **Template files** (safe to commit)

### Protected Information

The following sensitive data is automatically ignored by git:

- **API Keys:** DeepSeek, Llama, OpenRouter
- **Database Passwords:** MySQL credentials  
- **Django Secret Keys:** Application security keys
- **Email Credentials:** SMTP passwords
- **AWS Credentials:** S3 access keys

### Verification

To verify your `.env` files are properly ignored:

```bash
git status
# Should NOT show any .env files as untracked
```

### Security Checklist

- [ ] Actual `.env` files are not tracked by git
- [ ] All sensitive values are replaced with placeholders in `.env.example`
- [ ] API keys are regenerated if accidentally exposed
- [ ] Database passwords are strong and unique
- [ ] Django SECRET_KEY is randomly generated

## Getting API Keys

### DeepSeek API
1. Visit: https://platform.deepseek.com/
2. Sign up/Login
3. Generate API key
4. Add to `backend/.env` and `frontend/.env`

### OpenRouter API  
1. Visit: https://openrouter.ai/
2. Create account
3. Get API key
4. Add to `backend/.env`

## Support

If you accidentally commit sensitive data:
1. Immediately regenerate all exposed keys
2. Update your `.env` files with new keys
3. Consider using `git filter-branch` to remove from history
