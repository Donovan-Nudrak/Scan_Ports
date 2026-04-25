# Mini Port Scanner (Educational Tool)

A lightweight TCP port scanner written in Python with concurrency support and optional banner grabbing.

> For educational purposes only. Use only on systems you own or have explicit permission to test.

---

## Features

- TCP connect-based port scanning
- Multi-threaded execution for performance
- Optional banner grabbing for service identification
- Flexible port input (single ports, ranges, mixed)
- Export results to JSON or CSV

---

## How It Works

The scanner attempts TCP connections to a list of target ports on a given host.

- If a connection is successful → port is marked as **open**
- If enabled, the tool tries to read service banners from the open port
- All results are collected and optionally exported

---
## Usage

```bash
chmod +x scan.py

python3 scan.py <host> [options]
```

---
##  Arguments

### Required

- `host`  
    Target IP or domain to scan

---
### Optional

- `-p, --ports`  
    Ports to scan  
    Example: `22,80,443` or `1-1000`  
    Default: `22,80,443,3306,8080-8082`
    
- `-t, --timeout`  
    Connection timeout per port (seconds)  
    Default: `1.0`
    
- `-w, --workers`  
    Number of concurrent threads  
    Default: `100`
    
- `--no-banner`  
    Disable banner grabbing
    
- `-o, --output`  
    Save results to file  
    Supported formats:
    - `.json`
    - `.csv`

---

## Examples

### Basic scan
```bash
python3 scan.py 127.0.0.1
```

### Custom ports
```bash
python3 scan.py 192.168.1.1 -p 22,80,443
```

### Port range
```bash
python3 scan.py 192.168.1.1 -p 1-1000
```

### Fast scan with output
```bash
python3 scan.py 192.168.1.1 -w 200 -o result.json
```

### No banner grabbing
```bash
python3 scan.py 192.168.1.1 --no-banner
```

---

## Output Format

Each result contains:
```json
{  
  "port": 22,  
  "open": true,  
  "banner": "SSH-2.0-OpenSSH_8.2",  
  "error": null  
}
```

---

## Technical Notes

- Uses `socket` for TCP connections
- Uses `ThreadPoolExecutor` for concurrency
- Banner grabbing uses basic recv/send probing
- Results are sorted by port number

---

## Disclaimer

> This tool is intended for educational and research purposes only.  
> Unauthorized scanning of systems is illegal and not permitted.