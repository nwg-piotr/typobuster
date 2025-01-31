#!/usr/bin/env bash

PROGRAM_NAME="typobuster"
MODULE_NAME="typobuster"
SITE_PACKAGES="$(python3 -c "import sysconfig; print(sysconfig.get_paths()['purelib'])")"
PATTERN="$SITE_PACKAGES/$MODULE_NAME*"

# Remove from site_packages
for path in $PATTERN; do
    if [ -e "$path" ]; then
        echo "Removing $path"
        rm -r "$path"
    fi
done

# Remove launcher scripts
filenames=("/usr/bin/typobuster")

for filename in "${filenames[@]}"; do
  rm -f "$filename"
  echo "Removing -f $filename"
done

rm -f "/usr/share/applications $PROGRAM_NAME.desktop"
rm -f "/usr/share/pixmaps $PROGRAM_NAME.svg"
rm -f /usr/share/licenses/$PROGRAM_NAME/LICENSE
rm -f /usr/share/doc/$PROGRAM_NAME/README.md
