# PTAC Refurb Marketing OS - Merged Streamlit Repo

This repo merges the PTAC Refurb dashboard with the 90-day content calendar system.

## Includes
- dashboard/app.py = Streamlit app
- apps_script/Code.gs = Google Apps Script bridge
- PTAC_Refurb_Marketing_OS_Workbook.xlsx = Google Sheets starter workbook
- requirements.txt = Streamlit dependencies

## Setup
1. Upload `PTAC_Refurb_Marketing_OS_Workbook.xlsx` to Google Drive.
2. Open it with Google Sheets and use File > Save as Google Sheets.
3. Copy the Google Sheet ID from the URL.
4. In Google Sheets, go to Extensions > Apps Script.
5. Paste the contents of `apps_script/Code.gs`.
6. Change `SPREADSHEET_ID` and `SHARED_SECRET`.
7. Deploy as Web App: Execute as Me, Access Anyone.
8. In Streamlit Cloud secrets add:

```toml
APPS_SCRIPT_URL = "YOUR_WEB_APP_EXEC_URL"
APPS_SCRIPT_TOKEN = "YOUR_SHARED_SECRET"
```

9. Main file path in Streamlit: `dashboard/app.py`.
