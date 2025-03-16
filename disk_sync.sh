#!/bin/bash
#
# This script backs up a source directory to a disk partition defined in a configuration file
# which in /etc/disk_sync.conf, ensuring safe unmounting even with concurrent sync operations
# using a mount counter.
#
# # Author: Osman Karagöz, Gemini
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/copyleft/gpl.txt
#
# Usage:
# /bin/bash disk_sync.sh /source/path
#
# Config file parameters:
#
# DISK_PARTITION=/dev/sdb1
# MOUNT_POINT=/mnt/backup-disk
# BACKUP_DIRECTORY=${MOUNT_POINT}/backups
# LOG_FILE=/var/log/disk_sync.log

# Default configuration file path
default_config_file="/etc/disk_sync.conf"

# Working directory
working_dir="$(pwd)"

# Search for configuration file in working directory first
config_file="${working_dir}/disk_sync.conf"

# If not found in working directory, get from default directory
if [ ! -f "$config_file" ]; then
  config_file="$default_config_file"
fi

# Check if configuration file exists
if [ ! -f "$config_file" ]; then
  echo "ERROR: Configuration file not found: $config_file"
  exit 1
fi

# Read configuration file
source "$config_file"

# Check if source directory is provided as argument
if [ $# -eq 0 ]; then
  echo "ERROR: Source directory is not provided as argument"
  exit 1
fi

# Combine all arguments into a single string
SOURCE_DIR="$*"

# Remove leading and trailing quotes if present
SOURCE_DIR=$(echo "$SOURCE_DIR" | sed -e 's/^"//' -e 's/"$//')

# Check if source directory starts with mount point
if [[ "$SOURCE_DIR" == "$MOUNT_POINT"* ]]; then
  echo "ERROR: Source directory cannot be within the mount point"
  exit 1
fi

DEST_DIR="${MOUNT_POINT}/${SOURCE_DIR#/}"

# Logging function
log_message() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Check if mount point exists, create if not
if [ ! -d "$MOUNT_POINT" ]; then
  log_message "Mount point does not exist, creating: $MOUNT_POINT"
  mkdir -p "$MOUNT_POINT"
  if [ $? -ne 0 ]; then
    log_message "ERROR: Failed to create mount point: $MOUNT_POINT"
    exit 1
  fi
fi

# Get UUID from disk partition address
disk_uuid=$(blkid -o value -s UUID "$DISK_PARTITION")

# Check if disk partition is already mounted and correct
if mountpoint -q "$MOUNT_POINT"; then
  mounted_uuid=$(blkid -o value -s UUID "$(findmnt -n -o SOURCE "$MOUNT_POINT")")
  if [ "$mounted_uuid" = "$disk_uuid" ]; then
    log_message "Correct disk partition already mounted: $DISK_PARTITION -> $MOUNT_POINT"
  else
    log_message "ERROR: Incorrect disk partition mounted on: $MOUNT_POINT"
    exit 1
  fi
else
  # Mount disk partition by UUID
  if mount UUID="$disk_uuid" "$MOUNT_POINT"; then
    log_message "Disk partition mounted by UUID: $DISK_PARTITION -> $MOUNT_POINT"
  else
    log_message "ERROR: Failed to mount disk partition by UUID: $MOUNT_POINT"
    exit 1
  fi
fi

# Create backup directory
mkdir -p "$BACKUP_DIRECTORY"

# Increment active sync counter
active_sync_counter_file="/var/run/disk_sync_${MOUNT_POINT//\//_}.counter"
if [ -f "$active_sync_counter_file" ]; then
  active_sync_counter=$(cat "$active_sync_counter_file")
  active_sync_counter=$((active_sync_counter + 1))
else
  active_sync_counter=1
fi
echo "$active_sync_counter" > "$active_sync_counter_file"

# Synchronize directories
log_message "Synchronizing: $SOURCE_DIR -> $DEST_DIR"

# Synchronize directories (with backup of deleted files)
sync_error=0
if rsync -av --delete --backup --backup-dir="$BACKUP_DIRECTORY" "$SOURCE_DIR/" "$DEST_DIR/"; then
  log_message "Directories synchronized (deleted files backed up): $SOURCE_DIR -> $DEST_DIR"
else
  log_message "ERROR: Failed to synchronize directories: $SOURCE_DIR -> $DEST_DIR"
  sync_error=1 # Sign error state
fi

# Decrement active sync counter
active_sync_counter=$(cat "$active_sync_counter_file")
active_sync_counter=$((active_sync_counter - 1))
echo "$active_sync_counter" > "$active_sync_counter_file"

# Unmount disk partition (if counter is zero)
if [ "$active_sync_counter" -eq 0 ]; then
  if umount "$MOUNT_POINT"; then
    log_message "Disk partition unmounted: $MOUNT_POINT"
    rm "$active_sync_counter_file"
  else
    log_message "ERROR: Failed to unmount disk partition: $MOUNT_POINT"
    exit 1
  fi
fi

# Exit with 1 if there is an error
if [ "$sync_error" -eq 1 ]; then
  exit 1
fi

log_message "Disk synchronization completed."

exit 0
