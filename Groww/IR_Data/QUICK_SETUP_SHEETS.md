# Quick Google Sheets Setup for GitHub Actions

## 5-Minute Quick Start

### Step 1: Create Google Sheet
1. Go to https://sheets.google.com
2. Create "Groww IR Data"
3. Copy Sheet ID from URL: `https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid=0`

### Step 2: Get Google Credentials
1. Go to https://console.cloud.google.com/projectselector2/iam-admin/serviceaccounts
2. Create new project: "Groww Data"
3. Create Service Account: "groww-ir-data"
4. Create JSON Key
5. Download JSON file

### Step 3: Share Sheet
1. Open downloaded JSON file with text editor
2. Find `"client_email": "..."` value
3. In your Google Sheet, click "Share"
4. Paste email address, give "Editor" access, uncheck "Notify"

### Step 4: Add GitHub Secrets
1. Go to GitHub repo → Settings
2. Secrets and variables → Actions
3. Create two secrets:

**Secret 1: GOOGLE_SHEET_ID**
```
(Your sheet ID from step 1)
```

**Secret 2: GOOGLE_SHEETS_CREDENTIALS**
```
(Entire content of the JSON file, paste everything)
```

### Step 5: Update GitHub Actions
✅ Already done! Workflow is updated to:
- Use new `fetch_groww_ir_data_with_sheets.py`
- Read from GitHub Secrets
- Push to Google Sheets

### Step 6: Install Local Dependencies
```powershell
cd "Groww/IR_Data"
pip install gspread google-auth python-dotenv
```

### Step 7: Test Locally (Optional)
```powershell
cd "Groww/IR_Data"
# Create .env file with your Sheet ID
# Then run:
python fetch_groww_ir_data_with_sheets.py
```

## Now What?

✅ Your setup is complete!

**Every hour:**
- GitHub Actions runs the script
- Fetches Groww IR data
- Appends to CSV (backup)
- Appends to Google Sheets
- Commits CSV to GitHub

**In Google Sheets:**
- "All Data" sheet: All hourly data in one place
- Metric sheets: Separate sheet for each metric type (CNTU, AUM, etc.)

## Google Sheets Structure Created Automatically

| Sheet | Content |
|-------|---------|
| All Data | All metrics, append hourly |
| CNTU_Data | CNTU metric history |
| AUM_Data | AUM metric history |
| mf_assets_Data | MF Assets history |
| mf_sip_inflows_Data | MF SIP Inflows history |
| equity_adto_Data | Equity ADTO history |
| stocks_adto_Data | Stocks ADTO history |
| stocks_assets_Data | Stocks Assets history |

Each row: `[Fetch Time] [Metric] [Epoch] [Readable Time] [Value]`

## Troubleshooting

**"API not enabled"**
- Go to console.cloud.google.com
- Enable "Google Sheets API"

**"Permission denied"**
- Make sure to share sheet with the service account email
- May take 1-2 minutes for permissions to update

**"Sheet not found"**
- Verify GOOGLE_SHEET_ID secret is correct (no spaces)
- Check URL format

## Files in Groww/IR_Data/

```
✅ fetch_groww_ir_data.py             (Original CSV-only version)
✅ fetch_groww_ir_data_with_sheets.py (NEW - CSV + Google Sheets)
✅ groww_ir_data.csv                  (CSV backup)
✅ groww_ir_data.jsonl                (JSON backup)
✅ google_sheets_creds.json           (Credentials - LOCAL ONLY, never git)
✅ .env.example                       (Example config file)
✅ GOOGLE_SHEETS_SETUP.md             (Detailed setup guide)
✅ QUICK_SETUP_SHEETS.md              (This file)
```

## Security Checklist

✅ Never commit `google_sheets_creds.json` to GitHub  
✅ Use GitHub Secrets for credentials (not .env file)  
✅ Keep JSON file local only  
✅ Gitignore configured to exclude credentials  
✅ Service account has Editor access to sheet  

Done! 🎉 Your data is now syncing to Google Sheets hourly!
