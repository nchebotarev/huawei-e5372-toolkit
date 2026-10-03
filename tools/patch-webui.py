#!/usr/bin/env python3
"""Prepare a stock WebUI gzip page with the archived custom button added/removed.

The input is never overwritten. Inspect and deploy the output separately.
"""
import argparse
import gzip
from pathlib import Path
import re

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('input', type=Path, help='deviceinformation.html.gz copied from the router')
parser.add_argument('--output', required=True, type=Path)
parser.add_argument('--remove', action='store_true', help='Remove the archived button instead of adding it')
args = parser.parse_args()
if args.input.resolve() == args.output.resolve():
    parser.error('Input and output must be different files')
if args.output.exists():
    parser.error('Output already exists; choose a new filename')

data = gzip.decompress(args.input.read_bytes())
newline = b'\r\r\n' if b'\r\r\n' in data else b'\r\n' if b'\r\n' in data else b'\n'
button_pattern = re.compile(
    rb'<script\s+type="text/javascript">\s*'
    rb'create_button\("zoid LTE Diagnostics","zoid_diag"\);'
    rb'\s*\$\("#zoid_diag"\)\.click\(function\(\)\{\s*'
    rb'window\.open\("http://192\.168\.8\.1:8080/status\.html","_blank"\);'
    rb'\s*\}\);\s*</script>'
)
matches = list(button_pattern.finditer(data))
if len(matches) > 1:
    parser.error('More than one archived button found; inspect the page manually')
if args.remove:
    if len(matches) != 1:
        parser.error('Archived button not found; no output written')
    result = button_pattern.sub(b'',data,count=1)
else:
    if matches or b'zoid_diag' in data or b'zoid LTE Diagnostics' in data:
        parser.error('A custom button already exists; no output written')
    anchor = re.compile(rb'create_button\(common_refresh,"refresh"\);\s*</script>')
    anchors = list(anchor.finditer(data))
    if len(anchors) != 1:
        parser.error('Expected refresh-button anchor not found exactly once')
    fragment = (Path(__file__).resolve().parents[1]/'integration/deviceinformation-button.html').read_bytes().strip()
    fragment = fragment.replace(b'\n',newline)
    position = anchors[0].end()
    result = data[:position]+newline+fragment+data[position:]

args.output.write_bytes(gzip.compress(result,mtime=0))
print('Prepared '+str(args.output)+'; input unchanged. Review before deployment.')
