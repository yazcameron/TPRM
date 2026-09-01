# Drive output

Team-facing TPRM files go in this Google Drive folder, not the generic GRC analysis folder:

[TPRM reviews Drive folder](https://drive.google.com/drive/folders/1Qh9uG1tvuPq0Pruv6-aEDbyJhK1ZcaOY)  
Folder ID: `1Qh9uG1tvuPq0Pruv6-aEDbyJhK1ZcaOY`

Local HTML under `reviews/tprm/<slug>/` is a working copy only (gitignored). After every render, publish the same file into Drive.

## Folder layout

Vendor name is the first folder. Zip request number is a child folder when known.

```
TPRM reviews (root)
  Salesforce/
    #4341/
      vendor-clarification
      context-discrepancy
      vendor-materials-request
      soc2-followup
      ai-questionnaire-followup
      risk-assessment-salesforce
```

- Zip folder name is always `#` + digits (`#4341`). Strip extra text from intake (`Zip 4341` → `#4341`).
- If there is no Zip request number, put files directly in `{Vendor Name}/`.
- Reuse folders if they already exist. Do not create a second "Salesforce" folder.

Path helper (prints the expected names):

```bash
python skills/tprm-reviewer/scripts/engagement.py drive-path --vendor "Salesforce" --zip 4341
```

## How to publish

1. Ensure `{Vendor Name}` exists under folder ID `1Qh9uG1tvuPq0Pruv6-aEDbyJhK1ZcaOY`. Create it if missing.
2. If `zip_request_number` is set, ensure `#{number}` exists under the vendor folder.
3. Create or update a **Google Doc** in the leaf folder (`parentFolderId` = that folder's ID). Title = HTML filename without `.html` (e.g. `vendor-clarification`, `risk-assessment-salesforce`).
4. Prefer Google Docs MCP `createDocument` / `replaceDocumentWithMarkdown`. Else **gws** Drive/Docs CLI. Else upload the HTML file into that folder.
5. Store `drive_folder_id` (leaf) and `drive_doc_urls` on `state.json`.
6. In chat, include the Drive folder link after the pause/final line.

If Drive/Docs tools are not authenticated, still write local HTML, say Drive is unavailable, and give the intended path (`Salesforce / #4341`). Do not dump files into the shared GRC analysis folder (`1Oz_ZJxROqXYG_KM2c2pK_NSMXXup89VZ`).
