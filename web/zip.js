// A minimal ZIP reader for the Overleaf drop (spec 027 item E).
//
// Overleaf's "Menu → Download → Source" gives a .zip. Unpacking it here
// keeps the promise the rest of this app makes: the manuscript never
// leaves the browser tab. That rules out a server, and — since the point
// is a page with no dependencies to audit — a library too.
//
// Only what a real Overleaf export contains is supported: stored
// (method 0) and deflated (method 8) entries, the latter through the
// browser's own `DecompressionStream("deflate-raw")` (Chrome 103+,
// Firefox 113+, Safari 16.4+). Encrypted, spanned, and Zip64 archives
// are not; Overleaf produces none of them, and guessing would be worse
// than saying so.

const EOCD_SIGNATURE = 0x06054b50;
const CENTRAL_SIGNATURE = 0x02014b50;
const LOCAL_SIGNATURE = 0x04034b50;
// End-of-central-directory record: 22 bytes, plus up to 64 KiB of
// trailing comment, so that is how far back it can hide.
const EOCD_MIN_SIZE = 22;
const MAX_COMMENT = 0xffff;

export function decompressionSupported() {
  return typeof DecompressionStream === "function";
}

/** Locate the end-of-central-directory record, scanning backwards. */
function findEocd(view) {
  const start = Math.max(0, view.byteLength - EOCD_MIN_SIZE - MAX_COMMENT);
  for (let i = view.byteLength - EOCD_MIN_SIZE; i >= start; i -= 1) {
    if (view.getUint32(i, true) === EOCD_SIGNATURE) return i;
  }
  throw new Error("not a zip file (no end-of-central-directory record)");
}

/** Every entry in the central directory: name, method, sizes, offset. */
function readCentralDirectory(view, bytes) {
  const eocd = findEocd(view);
  const count = view.getUint16(eocd + 10, true);
  let offset = view.getUint32(eocd + 16, true);

  const entries = [];
  for (let i = 0; i < count; i += 1) {
    if (view.getUint32(offset, true) !== CENTRAL_SIGNATURE) {
      throw new Error("corrupt zip (bad central-directory header)");
    }
    const method = view.getUint16(offset + 10, true);
    const compressedSize = view.getUint32(offset + 20, true);
    const nameLength = view.getUint16(offset + 28, true);
    const extraLength = view.getUint16(offset + 30, true);
    const commentLength = view.getUint16(offset + 32, true);
    const localOffset = view.getUint32(offset + 42, true);
    const name = new TextDecoder().decode(
      bytes.subarray(offset + 46, offset + 46 + nameLength)
    );
    entries.push({ name, method, compressedSize, localOffset });
    offset += 46 + nameLength + extraLength + commentLength;
  }
  return entries;
}

/** The compressed bytes of one entry, skipping its local header. */
function entryBytes(view, bytes, entry) {
  if (view.getUint32(entry.localOffset, true) !== LOCAL_SIGNATURE) {
    throw new Error(`corrupt zip (bad local header for ${entry.name})`);
  }
  // The local header repeats the name/extra lengths, and its extra
  // field routinely differs from the central one — always read both
  // from the local record.
  const nameLength = view.getUint16(entry.localOffset + 26, true);
  const extraLength = view.getUint16(entry.localOffset + 28, true);
  const start = entry.localOffset + 30 + nameLength + extraLength;
  return bytes.subarray(start, start + entry.compressedSize);
}

async function inflate(raw) {
  const stream = new Blob([raw])
    .stream()
    .pipeThrough(new DecompressionStream("deflate-raw"));
  return new Uint8Array(await new Response(stream).arrayBuffer());
}

/**
 * Read `buffer` and return `[path, text]` pairs for the entries
 * `keep(path)` accepts. Directory entries, macOS resource forks, and
 * anything `keep` rejects are skipped without being decompressed.
 */
export async function readZip(buffer, keep) {
  const bytes = new Uint8Array(buffer);
  const view = new DataView(buffer);
  const wanted = readCentralDirectory(view, bytes).filter(
    (entry) => !entry.name.endsWith("/") && keep(entry.name)
  );

  const decoder = new TextDecoder();
  const pairs = [];
  for (const entry of wanted) {
    const raw = entryBytes(view, bytes, entry);
    let contents;
    if (entry.method === 0) {
      contents = raw;
    } else if (entry.method === 8) {
      contents = await inflate(raw);
    } else {
      throw new Error(
        `unsupported compression in ${entry.name} (method ${entry.method})`
      );
    }
    pairs.push([entry.name, decoder.decode(contents)]);
  }
  return pairs;
}
