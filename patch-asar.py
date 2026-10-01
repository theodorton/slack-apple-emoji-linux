#!/usr/bin/env python3
"""Inject apple-emoji.cjs into Slack's app.asar without repacking it.

New file contents are added to the end of the archive and the header is
rewritten to point at them. Every other entry (including the "unpacked" native
modules) keeps its original offset, so app.asar.unpacked stays valid.

usage: patch-asar.py <in app.asar> <out app.asar> <apple-emoji.cjs>
"""
import hashlib
import json
import struct
import sys

ENTRY = "boot.bundle.cjs"
INJECT = "apple-emoji.cjs"
REQUIRE = b'require("./apple-emoji.cjs");\n'
BLOCK_SIZE = 4 * 1024 * 1024


def read_asar(path):
    with open(path, "rb") as f:
        data = f.read()
    _, header_size, _, json_size = struct.unpack("<4I", data[:16])
    header = json.loads(data[16 : 16 + json_size])
    return header, data[8 + header_size :]


def write_asar(path, header, body):
    raw = json.dumps(header, separators=(",", ":")).encode()
    padded = raw + b"\0" * (-len(raw) % 4)
    pickle = struct.pack("<II", len(padded) + 4, len(raw)) + padded
    with open(path, "wb") as f:
        f.write(struct.pack("<II", 4, len(pickle)))
        f.write(pickle)
        f.write(body)


def integrity(content):
    blocks = [
        hashlib.sha256(content[i : i + BLOCK_SIZE]).hexdigest()
        for i in range(0, max(len(content), 1), BLOCK_SIZE)
    ]
    return {
        "algorithm": "SHA256",
        "hash": hashlib.sha256(content).hexdigest(),
        "blockSize": BLOCK_SIZE,
        "blocks": blocks,
    }


def main(src, dst, inject_path):
    header, body = read_asar(src)
    body = bytearray(body)
    dist = header["files"]["dist"]["files"]

    def put(name, content):
        dist[name] = {
            "size": len(content),
            "offset": str(len(body)),
            "integrity": integrity(content),
        }
        body.extend(content)

    entry = dist[ENTRY]
    start = int(entry["offset"])
    boot = bytes(body[start : start + entry["size"]])
    if REQUIRE in boot:
        sys.exit(f"{ENTRY} is already patched")

    with open(inject_path, "rb") as f:
        put(INJECT, f.read())
    put(ENTRY, REQUIRE + boot)

    write_asar(dst, header, bytes(body))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
