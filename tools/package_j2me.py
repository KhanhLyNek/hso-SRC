#!/usr/bin/env python3
"""Validate and package an existing Java ME MIDlet JAR (not the HSO Java SE server)."""
from pathlib import Path
import re
import shutil
import struct
import sys
import zipfile

SOURCE = Path('client/hso-client.jar')
OUT = Path('dist')
JAR = OUT / 'HSO-J2ME.jar'
JAD = OUT / 'HSO-J2ME.jad'

def u2(data, pos):
    return struct.unpack_from('>H', data, pos)[0]

def class_metadata(data):
    if data[:4] != b'\xca\xfe\xba\xbe':
        raise ValueError('Invalid class header')
    major = u2(data, 6)
    count = u2(data, 8)
    cp = [None] * count
    i, p = 1, 10
    while i < count:
        tag = data[p]
        p += 1
        if tag == 1:
            n = u2(data, p)
            p += 2
            cp[i] = data[p:p+n].decode('utf-8', 'replace')
            p += n
        elif tag in (3, 4, 9, 10, 11, 12, 17, 18):
            p += 4
        elif tag in (5, 6):
            p += 8
            i += 1
        elif tag in (7, 8, 16, 19, 20):
            cp[i] = u2(data, p)
            p += 2
        elif tag == 15:
            p += 3
        else:
            raise ValueError(f'Unsupported constant pool tag {tag}')
        i += 1
    super_idx = u2(data, p + 4)
    superclass = cp[cp[super_idx]] if super_idx else None
    return major, superclass

def attributes(raw):
    lines = raw.decode('utf-8', 'replace').replace('\r\n', '\n').split('\n')
    merged = []
    for line in lines:
        if line.startswith(' ') and merged:
            merged[-1] += line[1:]
        else:
            merged.append(line)
    result = {}
    for line in merged:
        if not line.strip():
            break
        if ': ' in line:
            k, v = line.split(': ', 1)
            result[k] = v
    return result

def manifest_bytes(attrs):
    lines = []
    for key, value in attrs.items():
        if not re.fullmatch(r'[A-Za-z0-9_-]+', key):
            raise ValueError(f'Invalid manifest key: {key}')
        b = f'{key}: {value}'.encode('utf-8')
        lines.append(b[:70])
        b = b[70:]
        while b:
            lines.append(b' ' + b[:69])
            b = b[69:]
    return b'\r\n'.join(lines) + b'\r\n\r\n'

def main():
    if not SOURCE.is_file():
        raise FileNotFoundError(f'Missing {SOURCE}')
    OUT.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(SOURCE) as source:
        bad = source.testzip()
        if bad:
            raise ValueError(f'Corrupt archive entry: {bad}')
        names = set(source.namelist())
        classes = [n for n in names if n.endswith('.class')]
        if not classes:
            raise ValueError('Client contains no Java class files')
        old_meta = source.read('META-INF/MANIFEST.MF') if 'META-INF/MANIFEST.MF' in names else b''
        attrs = attributes(old_meta) if old_meta else {}
        class_versions = {}
        midlet_candidates = []
        for name in classes:
            major, base = class_metadata(source.read(name))
            class_versions[name] = major
            if base == 'javax/microedition/midlet/MIDlet':
                midlet_candidates.append(name[:-6].replace('/', '.'))
        highest = max(class_versions.values())
        print(f'Client classes: {len(classes)}, bytecode class version: {min(class_versions.values())}..{highest}')
        print('MIDlet subclasses found:', midlet_candidates)
        print('Manifest attributes:', attrs)
        print('Newer class files:', sorted((name, v) for name, v in class_versions.items() if v > 48))
        if highest > 48:
            raise ValueError('Not a CLDC-compatible JAR: class version > 48. Requires actual J2ME source and recompilation.')
        if not attrs.get('MIDlet-1'):
            if len(midlet_candidates) != 1:
                raise ValueError('Could not uniquely identify MIDlet main class; client source or proper manifest required')
            attrs['MIDlet-1'] = f'HSO, , {midlet_candidates[0]}'
        attrs.setdefault('Manifest-Version', '1.0')
        attrs.setdefault('MIDlet-Name', 'HSO')
        attrs.setdefault('MIDlet-Version', '1.0.0')
        attrs.setdefault('MIDlet-Vendor', 'HSO')
        attrs.setdefault('MicroEdition-Configuration', 'CLDC-1.1')
        attrs.setdefault('MicroEdition-Profile', 'MIDP-2.0')
        midlet_class = attrs['MIDlet-1'].split(',')[-1].strip().replace('.', '/') + '.class'
        if midlet_class not in names:
            raise ValueError(f'MIDlet entry point is missing from JAR: {midlet_class}')
        if old_meta and attributes(old_meta) == attrs:
            shutil.copyfile(SOURCE, JAR)
            print('Manifest already valid; preserved original JAR unchanged')
        else:
            print('Writing missing MIDlet manifest fields')
            with zipfile.ZipFile(JAR, 'w') as result:
                result.writestr('META-INF/MANIFEST.MF', manifest_bytes(attrs))
                for item in source.infolist():
                    path = item.filename
                    if path.upper() == 'META-INF/MANIFEST.MF':
                        continue
                    if re.fullmatch(r'META-INF/[^/]+\.(SF|RSA|DSA|EC)', path, flags=re.I):
                        continue
                    result.writestr(item, source.read(path))
    keys = ['MIDlet-Name', 'MIDlet-Version', 'MIDlet-Vendor',
            'MIDlet-1', 'MicroEdition-Configuration', 'MicroEdition-Profile']
    jad = [f'{key}: {attrs[key]}' for key in keys]
    jad += [f'MIDlet-Jar-URL: {JAR.name}', f'MIDlet-Jar-Size: {JAR.stat().st_size}']
    JAD.write_bytes(('\r\n'.join(jad) + '\r\n').encode('utf-8'))
    print('Build OK:', JAR, JAR.stat().st_size, 'bytes;', JAD)
    print('Note: bytecode/manifest checks do not replace a runtime emulator test.')

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('J2ME package FAILED:', exc, file=sys.stderr)
        sys.exit(1)
