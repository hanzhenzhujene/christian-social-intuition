PYTHON ?= python
PIP ?= $(PYTHON) -m pip
PKG ?= christian_social_intuition

.PHONY: help setup test ci-smoke refresh-analysis refresh-figures paper paper-smoke release-check rerun-selected-v2 clean

help:
	@echo "Available targets:"
	@echo "  make setup               Install pinned dependencies and the package in editable mode"
	@echo "  make test                Run the test suite"
	@echo "  make ci-smoke            Run the same lightweight checks as GitHub Actions"
	@echo "  make refresh-analysis    Rebuild analysis bundles from the committed selected-v2 raw runs"
	@echo "  make refresh-figures     Rebuild README and paper figure assets"
	@echo "  make paper               Recompile the LaTeX paper"
	@echo "  make paper-smoke         Smoke-check the LaTeX paper build"
	@echo "  make release-check       Run tests, rebuild paper-facing artifacts, and recompile the PDF"
	@echo "  make rerun-selected-v2   Re-run both Qwen selected-v2 experiments (requires local Ollama models)"
	@echo "  make clean               Remove local LaTeX and pytest cache artifacts"

setup:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements/runtime.lock.txt -r requirements/dev.lock.txt
	$(PIP) install -e . --no-deps

test:
	pytest -q

ci-smoke: test paper-smoke

refresh-analysis:
	PYTHONPATH=src $(PYTHON) -m $(PKG).cli analyze-results \
		--results outputs/runs/qwen2.5_7b_instruct_eval_v2.jsonl \
		--frames-path configs/frames.yaml \
		--output-dir outputs/analysis/qwen2.5_7b_instruct_eval_v2
	PYTHONPATH=src $(PYTHON) -m $(PKG).cli analyze-results \
		--results outputs/runs/qwen2.5_0.5b_instruct_eval_v2.jsonl \
		--frames-path configs/frames.yaml \
		--output-dir outputs/analysis/qwen2.5_0.5b_instruct_eval_v2
	PYTHONPATH=src $(PYTHON) -m $(PKG).cli analyze-results \
		--results outputs/runs/qwen2.5_7b_instruct_eval_v2.jsonl outputs/runs/qwen2.5_0.5b_instruct_eval_v2.jsonl \
		--frames-path configs/frames.yaml \
		--output-dir outputs/analysis/final_combined_v2

refresh-figures:
	PYTHONPATH=src $(PYTHON) -m $(PKG).cli build-paper-figures \
		--analysis-dirs outputs/analysis/qwen2.5_7b_instruct_eval_v2 outputs/analysis/qwen2.5_0.5b_instruct_eval_v2 \
		--output-dir paper/figures
	PYTHONPATH=src $(PYTHON) -m $(PKG).study_overview_figure
	PYTHONPATH=src $(PYTHON) -m $(PKG).readme_summary_figure

paper:
	cd paper && pdflatex -interaction=nonstopmode -halt-on-error main.tex >/tmp/csi_paper_build.log
	cd paper && pdflatex -interaction=nonstopmode -halt-on-error main.tex >/tmp/csi_paper_build.log
	@tail -n 5 /tmp/csi_paper_build.log

paper-smoke: paper

release-check: test refresh-analysis refresh-figures paper

rerun-selected-v2:
	PYTHONPATH=src $(PYTHON) -m $(PKG).cli run-experiment \
		--model qwen2.5:7b-instruct \
		--split eval \
		--frame-mode selected \
		--run-id selected_v2 \
		--output outputs/runs/qwen2.5_7b_instruct_eval_v2.jsonl
	PYTHONPATH=src $(PYTHON) -m $(PKG).cli run-experiment \
		--model qwen2.5:0.5b-instruct \
		--split eval \
		--frame-mode selected \
		--run-id selected_v2 \
		--output outputs/runs/qwen2.5_0.5b_instruct_eval_v2.jsonl

clean:
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	find . -name '.DS_Store' -delete
	rm -rf .pytest_cache
	rm -f paper/*.aux paper/*.log paper/*.out
	rm -rf paper/figures_smoke_v2
