# Reference in-memory demuxer

Drop-in implementation of `stripVideoTrackFromMp4` for pillar 4 of the mobile PWA audio skill.

```ts
/**
 * In-memory MP4/M4A video track stripper.
 * Drops the 'vide' trak box and adjusts 'stco' chunk offsets in-place.
 */
export function stripVideoTrackFromMp4(buffer: ArrayBuffer): ArrayBuffer {
  const u8 = new Uint8Array(buffer);
  const view = new DataView(buffer);

  let moovOffset = -1;
  let moovSize = 0;
  let pos = 0;

  while (pos <= buffer.byteLength - 8) {
    const size = view.getUint32(pos);
    if (size < 8 || pos + size > buffer.byteLength) break;
    const type = String.fromCharCode(u8[pos + 4], u8[pos + 5], u8[pos + 6], u8[pos + 7]);
    if (type === 'moov') {
      moovOffset = pos;
      moovSize = size;
      break;
    }
    pos += size;
  }

  if (moovOffset === -1) return buffer;

  let moovPos = moovOffset + 8;
  const moovEnd = moovOffset + moovSize;
  const retainedChildren: { offset: number; size: number }[] = [];
  let videoTrakSize = 0;

  while (moovPos <= moovEnd - 8) {
    const childSize = view.getUint32(moovPos);
    if (childSize < 8 || moovPos + childSize > moovEnd) break;
    const childType = String.fromCharCode(u8[moovPos + 4], u8[moovPos + 5], u8[moovPos + 6], u8[moovPos + 7]);

    let isVideoTrak = false;
    if (childType === 'trak') {
      for (let i = moovPos; i <= moovPos + childSize - 16; i++) {
        if (u8[i] === 0x68 && u8[i + 1] === 0x64 && u8[i + 2] === 0x6C && u8[i + 3] === 0x72) {
          if (u8[i + 12] === 0x76 && u8[i + 13] === 0x69 && u8[i + 14] === 0x64 && u8[i + 15] === 0x65) {
            isVideoTrak = true;
            break;
          }
        }
      }
    }

    if (isVideoTrak) {
      videoTrakSize += childSize;
    } else {
      retainedChildren.push({ offset: moovPos, size: childSize });
    }
    moovPos += childSize;
  }

  if (videoTrakSize === 0) return buffer; // Pure audio already

  const newSize = buffer.byteLength - videoTrakSize;
  const newBuf = new Uint8Array(newSize);
  const newView = new DataView(newBuf.buffer);

  // 1. Copy everything before moov
  newBuf.set(u8.subarray(0, moovOffset), 0);

  // 2. Write new moov box header
  const newMoovSize = moovSize - videoTrakSize;
  newView.setUint32(moovOffset, newMoovSize);
  newBuf.set(u8.subarray(moovOffset + 4, moovOffset + 8), moovOffset + 4);

  // 3. Copy retained moov children, adjusting stco chunk offsets
  let writePos = moovOffset + 8;
  for (const child of retainedChildren) {
    const childBytes = u8.slice(child.offset, child.offset + child.size);
    const childView = new DataView(childBytes.buffer);
    for (let i = 0; i <= childBytes.length - 8; i++) {
      const type = String.fromCharCode(childBytes[i + 4], childBytes[i + 5], childBytes[i + 6], childBytes[i + 7]);
      if (type === 'stco') {
        const count = childView.getUint32(i + 12);
        for (let j = 0; j < count; j++) {
          const offPos = i + 16 + j * 4;
          if (offPos + 4 <= childBytes.length) {
            const oldOff = childView.getUint32(offPos);
            if (oldOff > moovOffset) {
              childView.setUint32(offPos, oldOff - videoTrakSize);
            }
          }
        }
      }
    }
    newBuf.set(childBytes, writePos);
    writePos += child.size;
  }

  // 4. Copy trailing payload (mdat, etc.)
  newBuf.set(u8.subarray(moovEnd), writePos);

  return newBuf.buffer;
}
```
