# Profile: CLI / TUI

Activate for command-line or terminal interfaces.

<terminal_profile>
Treat terminal interfaces as first-class products. Verify:
- predictable commands/navigation;
- keyboard-first operation;
- useful help and errors;
- meaningful exit codes;
- signal handling;
- machine-readable output where appropriate;
- resize/wrap behavior;
- separation of presentation from business logic.

For rich TUIs account for Unicode grapheme clusters, terminal cell-width semantics, malformed control sequences, redraw stability, and focus stability.

Do not build a TUI when a conventional CLI is sufficient.
</terminal_profile>
