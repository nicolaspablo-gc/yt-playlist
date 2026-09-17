# yt-playlist

Personal YouTube playlist manager.

## One-time OAuth setup

### 1. Create a Google Cloud project

1. Go to https://console.cloud.google.com
2. Click the project dropdown at the top → **New Project**
3. Give it a name (e.g. `yt-playlist`) and click **Create**

### 2. Enable the YouTube Data API

1. In the left menu go to **APIs & Services** → **Library**
2. Search for `YouTube Data API v3`
3. Click it and hit **Enable**

### 3. Create OAuth credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. If prompted to configure the consent screen:
   - Choose **External**
   - Fill in the app name (anything works) and your email
   - Skip the scopes step
   - On the **Test users** step, add your own Google account email
   - Save and go back to creating credentials
4. For application type choose **Desktop app**
5. Click **Create** — you'll get a client ID and client secret

### 4. Add yourself as a test user (prevents token expiry)

Publishing the app requires Google verification (because External was chosen). You don't need to do that — instead, add your own account as a test user, which keeps tokens valid indefinitely without any verification process.

1. Go to **Google Auth Platform** → **Audience**
2. Under **Test users**, add your Google account email
3. Save

### 5. Configure credentials

```bash
cp .env.example .env
```

Open `.env` and paste your client ID and client secret from step 3.

### 6. Install dependencies

```bash
uv sync
```

### 7. Authenticate

Run the auth flow once — it will open a browser window to log in with your Google account:

```bash
python auth.py
```

This saves a `.token.json` file locally. You won't need to log in again.
