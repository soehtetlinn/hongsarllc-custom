# SendGrid Email Integration for Odoo 18

Send emails via SendGrid HTTP API, bypassing SMTP port blocking on Digital Ocean, AWS, and other cloud providers.

## 🎯 Features

- ✅ **Bypass SMTP blocking** - Uses HTTPS (port 443) instead of SMTP ports
- ✅ **Free tier** - 100 emails/day completely free
- ✅ **Better deliverability** - Enterprise-grade infrastructure  
- ✅ **Easy setup** - Just add your API key
- ✅ **Scalable** - Upgrade as you grow

## 📦 Installation

### 1. Install SendGrid Python Library

```bash
pip3 install sendgrid
```

### 2. Install the Module

The module is located in `/home/odoo/custom/mail_sendgrid/`

1. Restart Odoo server
2. Go to Apps → Update Apps List
3. Search for "SendGrid"
4. Click Install

### 3. Get SendGrid API Key

1. Sign up at [SendGrid.com](https://signup.sendgrid.com/) (free account)
2. Go to Settings → API Keys
3. Click "Create API Key"
4. Name it "Odoo Integration"
5. Select "Mail Send" permission (or Full Access)
6. Copy the key (starts with `SG.`)

### 4. Verify Your Sender Email

**Important:** SendGrid requires sender verification

1. Go to [Sender Authentication](https://app.sendgrid.com/settings/sender_auth/senders)
2. Click "Create New Sender"
3. Fill in your details (use your email)
4. Check your email inbox
5. Click the verification link
6. Wait for "Verified" status

### 5. Configure in Odoo

1. Go to **Settings → Technical → Email → Outgoing Mail Servers**
2. Click **Create**
3. Fill in:
   - **Name:** SendGrid
   - **SMTP Server:** (not needed for API)
   - **Authentication:** Select **"SendGrid API"**
   - **SendGrid API Key:** Paste your key
   - **From Filter:** (optional, e.g., `.*@yourdomain.com`)
4. Click **Test Connection**
5. You should see success message!

## 🧪 Testing

### Test from Command Line

```bash
python3 /home/odoo/test-sendgrid-verified.py YOUR_API_KEY your@email.com
```

### Test from Odoo

1. Go to any model with email (e.g., Contacts)
2. Try sending an email
3. Check the recipient's inbox

## 🔧 Configuration

### Option 1: Via Mail Server (Recommended)

Configure the API key in the mail server settings (as described above).

### Option 2: Via System Parameters

Go to **Settings → Technical → Parameters → System Parameters**

Add:
- Key: `sendgrid.api_key`
- Value: Your SendGrid API key

## 📊 Usage

Once configured, all emails sent from Odoo will automatically use SendGrid API instead of SMTP.

The module:
- Intercepts outgoing emails
- Sends them via SendGrid HTTP API (port 443)
- Bypasses SMTP port blocking
- Provides better deliverability

## ⚠️ Troubleshooting

### "SendGrid library not installed"
```bash
pip3 install sendgrid
# Then restart Odoo
```

### "403 Forbidden" Error
- Make sure you've verified your sender email
- Check API key has "Mail Send" permission
- Verify the "from" email matches your verified sender

### Emails not sending
1. Check Odoo logs: `/var/log/odoo/odoo.log`
2. Check mail server configuration
3. Test API key with command line script
4. Verify sender email is verified in SendGrid

### Connection test fails
- Check API key is correct (starts with `SG.`)
- Ensure `sendgrid` Python package is installed
- Check internet connectivity
- Try regenerating API key

## 📈 SendGrid Pricing

| Plan | Price | Emails/Month | Features |
|------|-------|--------------|----------|
| **Free** | $0 | 100/day | Basic features |
| **Essentials** | $19.95/mo | 50,000 | Email API, Support |
| **Pro** | $89.95/mo | 100,000 | + Dedicated IP, Advanced stats |

## 🔗 Useful Links

- [SendGrid Documentation](https://docs.sendgrid.com/)
- [SendGrid Dashboard](https://app.sendgrid.com/)
- [Sender Verification](https://app.sendgrid.com/settings/sender_auth/senders)
- [API Keys](https://app.sendgrid.com/settings/api_keys)

## 📝 License

LGPL-3

## 👨‍💻 Author

Ten Ten Tutor

## 🤝 Contributing

Issues and pull requests welcome!

## ✅ Tested On

- Odoo 18.0
- Ubuntu 22.04
- Python 3.10+
- SendGrid API v3

