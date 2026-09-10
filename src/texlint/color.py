"""Whether to colourise the terminal stream (spec 027 item F).

Contract: ``specs/027-first-time-user-gaps/contracts/color.md`` C-3.

The *decision* lives here, in core, because both engines must make it
identically — a user who exports ``NO_COLOR`` must get the same answer
from ``jss-lint`` and ``jsslint``. The *escape bytes* are not shared:
Python lets rich emit them, Rust writes SGR at render time, and that
divergence is documented in ``rust/README.md`` (§XIII). What both
guarantee is C-1: stripping every escape sequence yields the plain
stream byte for byte, so colour can never change layout.

The precedence is the one anstream, ripgrep, and cargo already share, so
an author's existing habits apply::

    --color always|never  >  NO_COLOR  >  CLICOLOR_FORCE  >  TOML  >  TTY
"""

from __future__ import annotations

from collections.abc import Mapping

#: Accepted values of ``--color`` and of the TOML ``color`` key.
CHOICES: tuple[str, ...] = ("auto", "always", "never")


def should_colorize(
    *,
    flag: str | None,
    toml_value: str,
    env: Mapping[str, str],
    isatty: bool,
) -> bool:
    """Resolve the colour decision.

    *flag* is ``--color``'s value or ``None`` when the user did not pass
    it; *toml_value* is ``ToolConfig.color``; *env* is the process
    environment; *isatty* is whether stdout is a terminal.
    """
    if flag == "always":
        return True
    if flag == "never":
        return False

    # `NO_COLOR` is honoured when set to anything non-empty; an empty
    # value is how a script neutralises an inherited one.
    if env.get("NO_COLOR", ""):
        return False
    # `CLICOLOR_FORCE` forces colour on, except the documented `0`.
    force = env.get("CLICOLOR_FORCE", "")
    if force and force != "0":
        return True

    if toml_value == "always":
        return True
    if toml_value == "never":
        return False

    # auto: a TTY, and a terminal that can render anything at all.
    return isatty and env.get("TERM", "") != "dumb"
