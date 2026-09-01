# Prior reviews

Completed TPRM reviews live in this Google Drive folder (not the new-output folder):

[Prior TPRM reviews](https://drive.google.com/drive/folders/1_PFYmK7yZLiY0fYzKqPU_HA1NF0ml-QN)  
Folder ID: `1_PFYmK7yZLiY0fYzKqPU_HA1NF0ml-QN`

This is the **primary** source for "has this vendor been reviewed before?" Search it in Phase 1 before Safe, Glean, or local files.

## How to search

1. List or search inside folder ID `1_PFYmK7yZLiY0fYzKqPU_HA1NF0ml-QN` (Google Drive / Docs MCP, or **gws**). Match on vendor name, product name, and Zip request number if known. Include close name variants (e.g. legal entity vs product brand).
2. Open the latest matching review(s). Note date, products in scope, tier, data shared, and open conditions.
3. Compare to the current intake. Fill `prior_reviews` and `changes_since_prior` on the intake JSON.
4. If nothing matches, say so clearly — do not invent a prior review.
5. If Drive is not authenticated, set `prior_reviews_drive_available: false`, skip this folder, and try Safe / Glean / user-provided docs. Tell the user the prior-reviews folder was not reachable.

Do **not** write new intake/review files into this folder. New work goes to the output folder (`1Qh9uG1tvuPq0Pruv6-aEDbyJhK1ZcaOY`) as `{Vendor} / #{Zip}`.
