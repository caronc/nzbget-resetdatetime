# Changelog

## 1.0.0

- First release as an NZBGet v23+ extension (with a `manifest.json`). It still
  works as a classic post-processing script on older NZBGet versions.
- Needs Python 3.8 or newer.
- If one file can't be changed, the rest still are (it used to stop at the
  first one), and the run is reported as failed.
- Fixed a crash on very old NZBGet versions when checking download health.
- Per-file messages now go to NZBGet's DETAIL log, with a one-line summary.
- Settings text is translated into 20 languages (shown on NZBGet v26.3 and
  newer; older versions show the English text).

Based on `ResetDateTime.py` by Clinton Hall from
[nzbToMedia](https://github.com/clinton-hall/nzbToMedia).
