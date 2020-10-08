## We Teach CS converter

Target source was https://codio.myjetbrains.com/youtrack/issue/codio-11794, project https://codio.com/edeitrick/weteach-cs
Fylesystem structure fas updated to be in the same format(all folders with source code renamed to source_code, Starters -> Starters, Solutions -> Solutions) and Topic folder naming updated to the unified format

Example script runs(required pandoc installed)

```bash
python3 weteach-cs-converter.py weteach-cs-prepared --output=weteach-cs-output
```
