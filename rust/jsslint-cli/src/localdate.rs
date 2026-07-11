//! `date.today().isoformat()` equivalent — shared by the `init` and
//! `report` subcommands (both stamp generated output with today's
//! date).

/// `YYYY-MM-DD`, in the process's *local* timezone (matches Python's
/// `time.localtime()`-backed `date.today()` exactly, via the same
/// libc `localtime_r` the CPython interpreter itself ultimately
/// calls). This matters, not just cosmetics: a UTC-calendar-day
/// computation would disagree with Python for a large fraction of
/// every day in any negative-UTC-offset timezone (e.g. 7 of 24 hours
/// in US Pacific), which would make a byte-exact differential test of
/// generated output flaky. No `chrono` dependency needed for one date
/// stamp; `libc` is already a near-zero-cost, ambient dependency of
/// `rusqlite`'s bundled SQLite (used by `init`).
#[cfg(unix)]
pub fn today_iso() -> String {
    unsafe {
        let t: libc::time_t = libc::time(std::ptr::null_mut());
        let mut tm: libc::tm = std::mem::zeroed();
        libc::localtime_r(&t, &mut tm);
        format!(
            "{:04}-{:02}-{:02}",
            tm.tm_year + 1900,
            tm.tm_mon + 1,
            tm.tm_mday
        )
    }
}

/// Non-Unix fallback: UTC calendar day (Howard Hinnant's
/// `civil_from_days`) rather than the true local day — `libc`'s
/// `localtime_r` isn't available on Windows and getting the local
/// timezone there needs a real timezone crate; not worth it for a
/// cosmetic date stamp, and this binary's CI/dev environment is
/// Linux-only today.
#[cfg(not(unix))]
pub fn today_iso() -> String {
    let days_since_epoch = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_secs() / 86400)
        .unwrap_or(0) as i64;
    let (y, m, d) = civil_from_days(days_since_epoch);
    format!("{y:04}-{m:02}-{d:02}")
}

/// Howard Hinnant's `civil_from_days`: days-since-1970-01-01 -> (y, m, d).
#[cfg(not(unix))]
fn civil_from_days(z: i64) -> (i64, u32, u32) {
    let z = z + 719468;
    let era = if z >= 0 { z } else { z - 146096 } / 146097;
    let doe = (z - era * 146097) as u64;
    let yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
    let y = yoe as i64 + era * 400;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let d = (doy - (153 * mp + 2) / 5 + 1) as u32;
    let m = if mp < 10 { mp + 3 } else { mp - 9 } as u32;
    (if m <= 2 { y + 1 } else { y }, m, d)
}
