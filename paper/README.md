# Paper Build

- Main LaTeX source: `main.tex`
- Compiled PDF: `main.pdf`
- Local figure assets: `figures/`

Build command:

```bash
cd /Users/hanzhenzhu/Desktop/Christian_Social_intuition/paper
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Notes:

- The paper is self-contained inside `paper/`, including copied figure files.
- The current build is a local draft and still treats human-coded explanation consistency as pending.
- References are intentionally minimal in this version and should be expanded before submission.
