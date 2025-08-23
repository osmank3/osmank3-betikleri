# osmank3-scripts

This repository contains a collection of scripts to automate and simplify various tasks.

## Scripts

### disk_sync.sh

This script backs up a source directory to a disk partition defined in a configuration file. It uses a mount counter to ensure safe unmounting even with concurrent sync operations.

**Usage:**

```bash
/bin/bash disk_sync.sh /source/directory
```

### exiv2retimer.py

This script increases or decreases the EXIF creation date of photos by a given time difference. It can also rename files to their creation time and archive them into a directory structure based on year, month, and day.

**Dependencies:**

*   pyexiv2

**Usage:**

```bash
python exiv2retimer.py [OPTIONS] file or directory
```

### gexiv2retimer.py

This script has the same functionality as `exiv2retimer.py`, but it uses the `GExiv2` library.

**Dependencies:**

*   Gexiv2

**Usage:**

```bash
python gexiv2retimer.py [OPTIONS] file or directory
```

### mountCasper.py

This script mounts and unmounts a `casper-rw` file, which is used for persistent storage on a live Linux distribution.

**Usage:**

```bash
# To mount
python mountCasper.py mount

# To unmount
python mountCasper.py umount
```

### prephome.py

This script prepares a user's home directory for use on a different Linux distribution. It can move or link the user's files to a new directory structure.

**Usage:**

```bash
python prephome.py [COMMAND] [OPTIONS]
```

### renamer.py

This script renames image files in a directory to their creation date.

**Dependencies:**

*   kaa.metadata

**Usage:**

```bash
python renamer.py DIRECTORY
```

### retimesrt.py

This script edits the timing of an SRT subtitle file. It can increase or decrease the time of all subtitles, or only subtitles after or before a certain time. It can also delete or add subtitles.

**Usage:**

```bash
python retimesrt.py [OPTIONS] file
```