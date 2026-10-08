# asl-schema

Structured data and canonical tags for asl1.com, published with GitHub Pages and loaded by one script in GHL's site header. Public on purpose: everything here is already public on the website.

- Edit `src/pages.json` or `src/business.json`, then run `python build.py` to regenerate `schema.json`.
- `loader.js` is the script the site loads. It only adds tags; it never removes anything GHL puts on the page.
- The homepage is excluded; it already has its own business schema.

Changes go live within about 10 minutes of a commit to `main`. To roll one back, revert the commit.
