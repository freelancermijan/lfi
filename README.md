# Install

```
cd /opt/
sudo git clone https://github.com/freelancermijan/lfi.git
sudo chmod +x lfi/lfi.py
cd
sudo ln -sf /opt/lfi/lfi.py /usr/local/bin/lfi
lfi -h
```

## Options

```
lfi -h                                                                                                                           ─╯
usage: lfi [-h] (-u URL | -l LIST) -p PAYLOADS [-t {1,2,3,4,5,6,7,8,9,10}] [-v] [-o OUTPUT]

LFI Scanner

options:
  -h, --help            show this help message and exit
  -u URL, --url URL     Provide a single URL for testing
  -l LIST, --list LIST  Provide a file containing a list of URLs for testing
  -p PAYLOADS, --payloads PAYLOADS
                        Provide a list of LFI payloads for testing
  -t {1,2,3,4,5,6,7,8,9,10}, --threads {1,2,3,4,5,6,7,8,9,10}
                        Number of threads to use (1-10)
  -v, --verbose         Enable verbose mode for detailed output
  -o OUTPUT, --output OUTPUT
                        Optional output file to save found LFI URLs
```

## Usage

```
lfi -u "http://testphp.vulnweb.com/showimage.php?file=FUZZ&size=FUZZ" -p payloads/lfi.txt -v -t 4 -o test.txt
```
