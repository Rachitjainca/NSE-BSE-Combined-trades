# Quick GitHub Actions Setup Guide

## Step-by-Step Instructions

### 1. Initialize Local Git Repository

```powershell
cd "c:\Users\rachit.jain\Desktop\Python projects\Exisitng project\NSE BSE Combined"
git init
git add .
git commit -m "Initial commit: Groww IR Data Fetcher with GitHub Actions"
```

### 2. Create Repository on GitHub.com

1. Visit https://github.com/new
2. Name it: `groww-ir-data` (or any name you prefer)
3. Choose **Public** or **Private**
4. Click **"Create repository"**

### 3. Connect Local Repository to GitHub

**Replace YOUR_USERNAME with your GitHub username:**

```powershell
git remote add origin https://github.com/YOUR_USERNAME/groww-ir-data.git
git branch -M main
git push -u origin main
```

*You'll be prompted for GitHub credentials - use your GitHub token or password*

### 4. Verify Workflow is Active

1. Go to your GitHub repository: `https://github.com/YOUR_USERNAME/groww-ir-data`
2. Click **"Actions"** tab
3. You should see **"Fetch Groww IR Data Every Hour"** listed
4. Click it to see scheduled runs

### 5. Test the Workflow (Optional)

1. In Actions tab, click the workflow name
2. Click **"Run workflow"** → **"Run workflow"**
3. It will execute immediately and you'll see the log
4. After ~1 minute, check the data files were updated

## How to Monitor

### View Execution Logs
- Go to Actions tab
- Click any workflow run
- See detailed logs of script execution

### View Updated Data Files
- Navigate to `Groww/IR_Data/` in your repository
- Click `groww_ir_data.csv`
- You'll see data updates every hour!

## What Happens Automatically

✓ **Every hour**, GitHub Actions will:
1. Clone your repository
2. Install Python dependencies
3. Run the Groww IR data fetcher script
4. Append new data to CSV and JSONL files
5. Commit and push changes back to GitHub
6. Continue even if your laptop is off

## Stopping the Automation

To stop automatic runs:
1. Go to the Actions tab
2. Click the workflow
3. Click **"..."** menu → **"Disable workflow"**

To resume:
- Click **"Enable workflow"** when you're ready

## Adjusting the Schedule

To change the run frequency, edit `.github/workflows/fetch_groww_ir_data.yml`:

Replace this line:
```yaml
- cron: '0 * * * *'  # Every hour
```

With:
```yaml
- cron: '0 */2 * * *'  # Every 2 hours
- cron: '0 0 * * *'    # Daily at midnight
- cron: '*/30 * * * *' # Every 30 minutes
```

Then push the changes:
```powershell
git add .github/workflows/fetch_groww_ir_data.yml
git commit -m "Update workflow schedule"
git push
```

## Files Created

✓ `.github/workflows/fetch_groww_ir_data.yml` - The automation workflow
✓ `.gitignore` - Excludes unnecessary files from Git
✓ `GITHUB_ACTIONS_SETUP.md` - Detailed documentation

## Troubleshooting

**Workflow not showing up?**
- Push the `.github/workflows/fetch_groww_ir_data.yml` file to main branch
- Wait a minute and refresh

**Workflow runs but fails?**
- Click the failed run in Actions tab
- Read the error log
- Common issue: missing Python packages (already fixed in workflow)

**Data not updating?**
- Check if git push is working
- Verify repository is public (or has proper permissions)
- Check workflow logs for errors

**Questions?**
- See `GITHUB_ACTIONS_SETUP.md` for full documentation
