# ResetDateTime

An [NZBGet](https://nzbget.com) extension that sets the modified date of
every downloaded file to **now**.

Files inside a download keep the dates they were given when they were packed,
which can be months or years ago. Media players and file browsers that sort
by "recently added" or "date modified" then bury your new downloads.
ResetDateTime fixes that by giving every file today's date once the download
finishes. Failed downloads are left alone.

## Installing (NZBGet v23+)

ResetDateTime only uses Python's standard library, so there's nothing to
`pip install`.

1. Download `resetdatetime-<version>-dist.zip` and
   `resetdatetime-<version>-dist.zip.sha256` from the
   [releases page](https://github.com/caronc/nzbget-resetdatetime/releases).

2. Check the download isn't damaged (optional, but quick):
   ```bash
   # Linux
   sha256sum -c resetdatetime-<version>-dist.zip.sha256

   # macOS
   shasum -a 256 -c resetdatetime-<version>-dist.zip.sha256
   ```
   You should see `OK`. On Windows, run this in PowerShell and compare the
   result with the number inside the `.sha256` file:
   ```powershell
   Get-FileHash resetdatetime-<version>-dist.zip
   ```

3. Unzip it into NZBGet's scripts folder. You'll find that folder under
   **Settings > Paths > ScriptDir** (in the official Docker image it's
   `/downloads/scripts`).
   ```bash
   # The zip already holds a ResetDateTime/ folder, so unzip it right into
   # the scripts folder
   unzip resetdatetime-<version>-dist.zip -d /path/to/nzbget/scripts
   ```
   You should end up with `scripts/ResetDateTime/ResetDateTime.py`. If you're
   replacing an older copy, delete the old `scripts/ResetDateTime/` folder
   first.

4. Restart NZBGet, then turn ResetDateTime on in
   **Settings > Extension Manager**. If a category has its own
   **Extensions** list (under **Settings > Categories**), add
   **ResetDateTime** there too; that list replaces the global one.

5. In **Settings > Extension Manager**, use the **Order** arrows to move
   ResetDateTime to the top, so it runs before anything that moves or
   imports the files.

There are no settings.

### Older NZBGet Versions

`ResetDateTime.py` still carries the classic `### NZBGET POST-PROCESSING SCRIPT`
header, so NZBGet versions before v23 can use it too. Put the
`ResetDateTime/` folder in your scripts folder and add it to each category's
**PostScript** list.

## Credits and License

ResetDateTime was written by Clinton Hall for [nzbToMedia](https://github.com/clinton-hall/nzbToMedia). It's free software under the GNU General Public License, version 3 or later (see [LICENSE](LICENSE)).
