# Publish this separate revised Task 4 project

The separate project repository has been created. This guide is retained for future updates or a personal copy; consult `SUBMISSION_LINKS.md` for its current publication status. These instructions use your own secure browser/CLI login instead of putting a token in a document, shell history, repository or chat.

## Recommended: GitHub CLI on your computer

1. Download and extract the full project archive.
2. Open a terminal in the extracted `Task4_Online_Retail_Project` directory.
3. Install Git and GitHub CLI if required.
4. Run `gh auth login` and choose the browser-based login. Confirm you are using the intended account with `gh auth status`.
5. Configure your preferred Git author name/email locally if you have not already done so. Do not invent a contact email or paste a credential into Git configuration.
6. Create a **new** repository rather than overwriting Task 5 or the original Task 4.

```bash
git init -b main
git add .
git commit -m "Add revised evidence-based Task 4 analysis"
gh repo create online-retail-task4-evidence-based-analysis \
  --public --source=. --remote=origin --push
```

The workbook is approximately 23.7 MB, each cleaned gzip approximately 11 MB and the Word approximately 1.4 MB. No individual project file approaches GitHub's 100 MB Git-file limit. The original source workbook has its CC BY 4.0 attribution and licence notice. All credentials, caches, virtual environments and generated ZIPs are ignored.

If a repository with that name already exists, stop and inspect it. Do not force-push or replace an existing history; choose a genuinely new name or intentionally publish a reviewed update.

## Browser alternative

Create a new public repository on GitHub and use **Add file → Upload files** to upload the extracted project contents. Upload ordinary files and folders, not the ZIP as the only repository content. Keep `README.md` at the root. Large files may need a separate upload batch; use CLI if your browser rejects the upload. The scripts can re-download the verified official workbook if you intentionally choose not to include raw data; document any such omission.

## Verify after publishing

- Open the repository in a signed-out browser.
- Check that README, report, notebook, scripts, data manifests, licences and all 15 PNGs are present.
- Download the Word from the repository and verify SHA-256:
  `30c0823a72edb604492ac4d19278f0b8d0a0a502cf43cfc35bb178c828f645d8`.
- Clone it, run the documented pipeline and `python tests/validate_outputs.py`.
- Update `SUBMISSION_LINKS.md` and `PUBLICATION.json` with the real repository URL and commit ID.

Send the resulting repository URL back to the agent for unauthenticated content/link verification. No fresh token needs to be posted in the conversation. Revoke any previously exposed token.
