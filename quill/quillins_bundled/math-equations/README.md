# Math Equations

Bundled Quillin that inserts LaTeX or MathML equations at the caret.

- LaTeX equations are wrapped in `\(...\)` (inline) or `$$...$$` (display) delimiters — both are MathJax's own default math delimiters, so preview and HTML export need no extra configuration.
- MathML is inserted verbatim.

Contributed via the Insert menu and the keyboard shortcut Ctrl+Shift+E.

## Math AutoCorrect-style abbreviations

Typing a backslash code followed by a space or punctuation (matching Word's
Math AutoCorrect behavior) expands it to the corresponding symbol — e.g.
`\alpha ` becomes `α`, `\sqrt ` becomes `√`, `\ne ` becomes `≠`. Codes are
seeded from the DAISY-published Word Math AutoCorrect list (daisy.org/MSMathCodes)
and cover Greek letters, relations, set/logic notation, calculus notation, and
geometry symbols. Disable individual entries or the whole set from the Insert
Automation preferences page like any other contributed abbreviation.

## Common Formulas gallery

Ten ready-made algebra and geometry formulas (quadratic formula, Pythagorean
theorem, slope-intercept and point-slope forms, slope/distance/midpoint
formulas, difference of squares, area and circumference of a circle) are
available from **Insert > Snippet Gallery...** — pick one and it inserts
correctly formatted, with nothing to type. Each is a plain `$$...$$` block,
so it can be selected and re-edited with Ctrl+Shift+E like any other
equation.

## Explore Equation Structure

Select an equation (or type/paste one) and run **Insert > Explore Equation
Structure...**, or press **Ctrl+Shift+Grave, F**, to step through it piece
by piece — descend into a fraction's numerator and denominator, a power's
base and exponent, a square root's radicand — with a plain-English reading
available at any point via **Read this part aloud**. This is a lightweight,
dependency-free structural navigator (`quill.core.math.navigator`), not
Nemeth-quality math speech — real math braille/speech needs MathCAT,
tracked separately as a deferred, native-build-pipeline project in
`docs/planning/math.md`.
