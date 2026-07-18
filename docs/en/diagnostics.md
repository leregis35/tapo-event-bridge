# Diagnostic engine

Each camera property is stored as a `DiagnosticFact` containing a value,
an evidence level, an optional source, and an optional note.

Evidence levels are `confirmed`, `observed`, `hypothesis`, and `unknown`.
Unknown is the default, so an untested capability can never silently appear as supported.
