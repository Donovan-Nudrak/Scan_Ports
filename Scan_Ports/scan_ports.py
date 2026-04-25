#!/usr/bin/env python3
"""
Mini port scanner + banner grabbing (educational).
Use only on systems/environments with permission.
"""

import socket
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json
import csv


def scan_port(host, port, timeout=1.0, grab_banner=True):
    result = {"port": port, "open": False, "banner": None, "error": None}
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            res = s.connect_ex((host, port))

            if res == 0:
                result["open"] = True

                if grab_banner:
                    try:
                        s.settimeout(0.8)
                        banner = s.recv(1024)

                        if banner:
                            result["banner"] = banner.decode(errors="replace").strip()
                        else:
                            try:
                                s.sendall(b"\r\n")
                                banner = s.recv(1024)
                                if banner:
                                    result["banner"] = banner.decode(errors="replace").strip()
                            except Exception:
                                pass
                    except Exception:
                        pass

    except Exception as e:
        result["error"] = str(e)

    return result


def scan_ports(host, ports, timeout=1.0, workers=100, grab_banner=True):
    out = []

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(scan_port, host, p, timeout, grab_banner): p for p in ports}

        for fut in as_completed(futures):
            res = fut.result()
            out.append(res)

    return sorted(out, key=lambda x: x["port"])


def parse_ports(ports_str):
    # accepts "22,80,8000-8010"
    s = set()

    for part in ports_str.split(","):
        part = part.strip()

        if "-" in part:
            a, b = part.split("-", 1)
            s.update(range(int(a), int(b) + 1))
        elif part:
            s.add(int(part))

    return sorted(p for p in s if 0 < p < 65536)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_csv(path, data):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["port", "open", "banner", "error"])
        writer.writeheader()

        for row in data:
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description="Mini port scanner + banner grabbing (educational).")

    parser.add_argument("host", help="Host or IP to scan")

    parser.add_argument(
        "-p", "--ports",
        default="22,80,443,3306,8080-8082",
        help="Ports (e.g. 22,80,8000-8010)"
    )

    parser.add_argument(
        "-t", "--timeout",
        type=float,
        default=1.0,
        help="Connection timeout (seconds)"
    )

    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=100,
        help="Number of threads"
    )

    parser.add_argument(
        "-o", "--output",
        help="Save results to file (.json or .csv)"
    )

    parser.add_argument(
        "--no-banner",
        action="store_true",
        help="Disable banner grabbing"
    )

    args = parser.parse_args()

    try:
        target_ip = socket.gethostbyname(args.host)
    except Exception as e:
        print(f"[!] Error resolving host: {e}")
        return

    ports = parse_ports(args.ports)

    print(
        f"Scanning {args.host} ({target_ip}) ports: "
        f"{min(ports)}-{max(ports)} — {len(ports)} ports"
    )

    start = datetime.now()

    results = scan_ports(
        target_ip,
        ports,
        timeout=args.timeout,
        workers=args.workers,
        grab_banner=not args.no_banner
    )

    dur = (datetime.now() - start).total_seconds()
    open_ports = [r for r in results if r["open"]]

    print(f"\nResults (open: {len(open_ports)}) — time: {dur:.2f}s\n")

    for r in open_ports:
        print(f"Port {r['port']:5d}  open  banner: {r['banner'] or '-'}")

    if args.output:
        if args.output.lower().endswith(".json"):
            save_json(args.output, results)
        elif args.output.lower().endswith(".csv"):
            save_csv(args.output, results)
        else:
            print("[!] Unknown output format, use .json or .csv")

        print(f"[+] Saved to {args.output}")


if __name__ == "__main__":
    main()
