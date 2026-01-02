#!/bin/bash

echo "Starting downloads from all links.txt files..."

# Find all links.txt files
find galleries -name "links.txt" -type f | while read links_file; do
	# Get directory containing the links.txt file
	dir=$(dirname "$links_file")

	echo "Processing: $dir"

	# Check if links.txt has any URLs
	if [ -s "$links_file" ]; then
		echo "  Found URLs, downloading with aria2c..."

		# Download using aria2c to the same directory
		aria2c \
			--file-allocation=none \
			--max-connection-per-server=16 \
			--split=16 \
			--min-split-size=1M \
			--continue=true \
			--check-certificate=false \
			--retry-wait=5 \
			--max-tries=10 \
			--timeout=60 \
			--connect-timeout=30 \
			--max-file-not-found=3 \
			--auto-file-renaming=true \
			--console-log-level=notice \
			--summary-interval=0 \
			--show-console-readout=true \
			--human-readable=true \
			-d "$dir" \
			-i "$links_file"

		if [ $? -eq 0 ]; then
			echo "  Download completed"
		else
			echo "  Download failed"
		fi
	else
		echo "  No URLs to download (empty file)"
	fi

	echo ""
done

echo "Download process completed!"
