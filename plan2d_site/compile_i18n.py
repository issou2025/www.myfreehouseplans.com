#!/usr/bin/env python
"""plan2d_site PO->MO compiler.

Windows often lacks GNU gettext utilities (msgfmt). This script compiles `.po`
files into `.mo` files so Django can load translations.
"""

import ast
import struct
from pathlib import Path


def _po_unquote(quoted: str) -> str:
    """Parse a PO-quoted string into a Python str.

    PO uses C-like escapes (\n, \t, \", \\). We leverage ast.literal_eval
    to safely interpret the quoted literal.
    """
    quoted = quoted.strip()
    if not (quoted.startswith('"') and quoted.endswith('"')):
        return quoted
    return ast.literal_eval(quoted)

def generate_mo_file(po_file_path, mo_file_path):
    """Convert .po file to .mo file."""
    
    messages: dict[str, str] = {}
    current_id: str | None = None
    current_str: str | None = None
    current_section: str | None = None  # 'msgid' | 'msgstr'

    def flush_pair() -> None:
        nonlocal current_id, current_str
        if current_id is None or current_str is None:
            return
        messages[current_id] = current_str

    # Parse PO file (supports multi-line msgid/msgstr, incl. header)
    with open(po_file_path, 'r', encoding='utf-8') as f:
        for raw_line in f:
            line = raw_line.strip()

            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue

            if line.startswith('msgid '):
                flush_pair()
                current_section = 'msgid'
                current_id = _po_unquote(line[len('msgid '):].strip())
                current_str = None
                continue

            if line.startswith('msgstr '):
                current_section = 'msgstr'
                current_str = _po_unquote(line[len('msgstr '):].strip())
                continue

            # Continuation line for msgid/msgstr
            if line.startswith('"') and current_section in {'msgid', 'msgstr'}:
                chunk = _po_unquote(line)
                if current_section == 'msgid' and current_id is not None:
                    current_id += chunk
                elif current_section == 'msgstr' and current_str is not None:
                    current_str += chunk
                continue

            # Ignore other PO constructs for now (msgid_plural, msgstr[n], etc.)
            # They are not currently used in our translations.

        flush_pair()

    # Ensure header exists and forces UTF-8
    header = messages.get('', '')
    if 'charset=' not in header.lower():
        if header and not header.endswith('\n'):
            header += '\n'
        header += 'Content-Type: text/plain; charset=UTF-8\n'
    messages[''] = header
    
    # Create MO file (GNU gettext format)
    # Sort keys for consistent output - put empty string (header) first
    keys = sorted(messages.keys(), key=lambda x: (x != '', x))
    
    # Encode all strings as UTF-8
    ids = [key.encode('utf-8') for key in keys]
    strs = [messages[key].encode('utf-8') for key in keys]
    
    # Calculate offsets
    # MO file structure:
    # - Header (28 bytes)
    # - Original strings table (8 bytes per entry: length + offset)
    # - Translated strings table (8 bytes per entry)
    # - Hash table (not used, so 0 entries)
    # - Original strings data
    # - Translated strings data
    
    keystart = 7 * 4 + len(keys) * 8 * 2  # After header and both tables
    
    # Calculate string data offsets
    key_offsets = []
    offset = keystart
    for id_bytes in ids:
        key_offsets.append(offset)
        offset += len(id_bytes) + 1  # +1 for null terminator
    
    str_offsets = []
    for str_bytes in strs:
        str_offsets.append(offset)
        offset += len(str_bytes) + 1
    
    # Build MO file
    output = bytearray()
    
    # Magic number (0x950412de = little-endian)
    output.extend(struct.pack('<I', 0x950412de))
    
    # File format version (0)
    output.extend(struct.pack('<I', 0))
    
    # Number of entries
    output.extend(struct.pack('<I', len(keys)))
    
    # Offset of table with original strings
    output.extend(struct.pack('<I', 7 * 4))
    
    # Offset of table with translated strings  
    output.extend(struct.pack('<I', 7 * 4 + len(keys) * 8))
    
    # Size of hashing table (0 = not used)
    output.extend(struct.pack('<I', 0))
    
    # Offset of hashing table (not used)
    output.extend(struct.pack('<I', 0))
    
    # Original strings table
    for i, id_bytes in enumerate(ids):
        output.extend(struct.pack('<I', len(id_bytes)))  # Length
        output.extend(struct.pack('<I', key_offsets[i]))  # Offset
    
    # Translated strings table
    for i, str_bytes in enumerate(strs):
        output.extend(struct.pack('<I', len(str_bytes)))  # Length
        output.extend(struct.pack('<I', str_offsets[i]))  # Offset
    
    # Original strings data
    for id_bytes in ids:
        output.extend(id_bytes)
        output.append(0)  # Null terminator
    
    # Translated strings data
    for str_bytes in strs:
        output.extend(str_bytes)
        output.append(0)  # Null terminator
    
    # Write to file
    with open(mo_file_path, 'wb') as f:
        f.write(output)
    
    return len(keys)


if __name__ == '__main__':
    # Get the locale directory
    script_dir = Path(__file__).resolve().parent
    locale_dir = script_dir / 'locale'
    
    compiled_count = 0
    
    # Find all .po files and compile them
    for po_file in locale_dir.rglob('*.po'):
        mo_file = po_file.with_suffix('.mo')
        
        try:
            count = generate_mo_file(po_file, mo_file)
            print(f"✓ Compiled {po_file.relative_to(script_dir)} -> {mo_file.relative_to(script_dir)} ({count} messages)")
            compiled_count += 1
        except Exception as e:
            print(f"✗ Error compiling {po_file.relative_to(script_dir)}: {e}")
    
    if compiled_count > 0:
        print(f"\n✓ Successfully compiled {compiled_count} translation file(s)!")
    else:
        print("\n✗ No translation files found to compile.")
