# Groww IR Data to Google Sheets - Setup Guide

## Step 1: Create Google Sheet

1. Go to https://sheets.google.com
2. Create a new spreadsheet named "Groww IR Data"
3. Note the Sheet ID from the URL: `https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit`

## Step 2: Set Up Google Sheets API

### 2a. Create Service Account

1. Go to https://console.cloud.google.com/
2. Create a new project: "Groww IR Data"
3. Enable Google Sheets API:
   - Search for "Google Sheets API"
   - Click "Enable"
4. Create Service Account:
   - Go to "Service Accounts"
   - Click "Create Service Account"
   - Name: `groww-ir-data`
   - Click "Create and Continue"
   - Skip optional steps, click "Done"

### 2b. Create and Download Credentials

1. Click on the service account you just created
2. Go to "Keys" tab
3. Click "Add Key" → "Create new key"
4. Choose "JSON"
5. Download the JSON file
6. **Keep this file safe** - it contains API credentials

## Step 3: Share Google Sheet with Service Account

1. In the JSON file, find the `client_email` value
2. Open your Google Sheet
3. Click "Share" (top right)
4. Paste the `client_email`
5. Give "Editor" access
6. Uncheck "Notify people"
7. Click "Share"

## Step 4: Configure for Local Development

1. Save the JSON credentials file to:
   ```
   Groww/IR_Data/google_sheets_creds.json
   ```

2. Create a `.env` file in `Groww/IR_Data/`:
   ```
   GOOGLE_SHEET_ID=your_sheet_id_here
   ```

3. Test locally:
   ```powershell
   cd Groww/IR_Data
   python fetch_groww_ir_data_with_sheets.py
   ```

## Step 5: Configure for GitHub Actions

1. Go to your GitHub repo settings
2. Click "Secrets and variables" → "Actions"
3. Create two secrets:

   **Secret 1: GOOGLE_SHEETS_ID**
   - Value: Your Google Sheet ID

   **Secret 2: GOOGLE_SHEETS_CREDENTIALS**
   - Value: Content of your JSON credentials file

4. Update `.github/workflows/fetch_groww_ir_data.yml` to use these secrets

## Sheet Structure

### Main Sheet ("All Data")
Columns:
- fetch_time
- metric_type
- epoch_timestamp
- timestamp_readable
- value

Appends all 70 records every hour

### Metric-Specific Sheets
One sheet per metric type:
- CNTU_Data
- AUM_Data
- mf_assets_Data
- mf_sip_inflows_Data
- equity_adto_Data
- stocks_adto_Data
- stocks_assets_Data

Each sheet tracks trends for that specific metric over time.

## Folder Structure After Setup

```
Groww/IR_Data/
├── fetch_groww_ir_data.py (original CSV version)
├── fetch_groww_ir_data_with_sheets.py (new Google Sheets version)
├── google_sheets_creds.json (credentials - never commit to git)
├── .env (local environment variables)
├── groww_ir_data.csv (backup)
└── groww_ir_data.jsonl (backup)
```

## Important Security Notes

⚠️ **NEVER** commit `google_sheets_creds.json` to GitHub
- Add to `.gitignore`
- Use GitHub Secrets instead for CI/CD

✅ Use `.env` file locally (add to `.gitignore`)
✅ GitHub Actions will use Secrets

## Troubleshooting

**"Authentication failed"**
- Check `client_email` is added to sheet permissions
- Verify `GOOGLE_SHEET_ID` is correct

**"Sheet not found"**
- Confirm sheet ID matches URL
- Check for typos

**Credentials invalid in GitHub**
- Paste full JSON content in GOOGLE_SHEETS_CREDENTIALS secret
- Not just the filename
