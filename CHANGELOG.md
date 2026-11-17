# Changelog

## 0.1.0

- Focus the project on selected Whirlpool games and state its entirely vibe-coded origin.
- Require independent backups and user verification before use.

- Split patching, UI and CLI code into separate modules.
- Validate the call argument sequence in addition to the existing input routine signature.
- Check the source hash again before replacing it; verify restored bytes before removing backups.
- Add synthetic-PE tests and x86 stub emulation without commercial game fixtures.
- Add Windows test workflow, repeatable build instructions, release checksums and third-party license collection.
- Document the distinction between runtime-confirmed and structurally compatible games.

Previous version labels were local prototype labels; 0.1.0 is the first public release. Existing prototype-patched executables are detected and must not be patched again.
