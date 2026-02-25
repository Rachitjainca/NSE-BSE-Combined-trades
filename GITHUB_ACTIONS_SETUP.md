# Groww IR Data Fetcher - GitHub Actions Setup

This document explains how to deploy the Groww IR Data fetcher on GitHub Actions to run automatically every hour.

## Prerequisites

1. A GitHub account
2. This project pushed to a GitHub repository
3. Git installed on your machine

## Setup Instructions

### Step 1: Initialize Git Repository (if not already done)

```powershell
cd "c:\Users\rachit.jain\Desktop\Python projects\Exisitng project\NSE BSE Combined"

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Groww IR Data Fetcher setup"
```

### Step 2: Create Repository on GitHub

1. Go to https://github.com/new
2. Create a new repository (e.g., `groww-ir-data`)
3. Follow GitHub's instructions to push your local repository

**Command** (replace YOUR_USERNAME and YOUR_REPO):
```powershell
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### Step 3: Verify Workflow is Set Up

1. Go to your GitHub repository
2. Click the **"Actions"** tab
3. You should see **"Fetch Groww IR Data Every Hour"** workflow listed
4. Click on it to see the schedule

### Step 4: Manual Trigger (Optional Test)

1. In the Actions tab, click the workflow
2. Click **"Run workflow"** button
3. Click **"Run workflow"** again to confirm
4. The script will run immediately

## How It Works

The workflow will:
- ✓ Run automatically every hour (at the 0th minute)
- ✓ Clone the repository
- ✓ Install Python and dependencies
- ✓ Run the `fetch_groww_ir_data.py` script
- ✓ Commit and push updates to `groww_ir_data.csv` and `groww_ir_data.jsonl`
- ✓ Continue running even when your laptop is off

## Viewing Results

**Method 1: On GitHub**
1. Go to your repository
2. Navigate to `Groww/IR_Data/` folder
3. Click `groww_ir_data.csv` to view the latest data
4. You'll see it updates every hour

**Method 2: Track Runs**
1. Click **"Actions"** tab
2. Click on any run to see execution logs
3. Logs show exactly when the script ran and any data fetched

## Data Files

The workflow maintains:
- `Groww/IR_Data/groww_ir_data.csv` - Main data file (appends every run)
- `Groww/IR_Data/groww_ir_data.jsonl` - JSON Lines format (appends every run)

Both files grow automatically with each hourly run.

## Time Zone Note

The cron schedule `0 * * * *` runs based on **UTC timezone**. Each run happens at the top of every hour UTC.

To adjust timing, modify the cron in `.github/workflows/fetch_groww_ir_data.yml`:
```yaml
on:
  schedule:
    - cron: '0 * * * *'  # Change this line
```

**Common cron patterns:**
- `0 * * * *` = Every hour
- `0 0 * * *` = Daily at midnight UTC
- `0 */2 * * *` = Every 2 hours
- `30 * * * *` = Every hour at 30 minutes past

## Troubleshooting

### Workflow not running?
1. Check if workflow file is in `.github/workflows/`
2. Verify you pushed the file to main branch
3. Check Actions tab for any errors

### Data not showing?
1. Click on the workflow run log
2. Check for any error messages
3. Verify Python script runs locally first

### Want to disable it?
1. Go to Actions tab
2. Click the workflow
3. Click the **"..."** menu
4. Click **"Disable workflow"**

## Future Adjustments

To stop the automation, delete or disable the workflow file in `.github/workflows/fetch_groww_ir_data.yml`

To modify the schedule, edit the `cron` value in the workflow file and push the changes.
