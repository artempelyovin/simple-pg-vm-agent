SHELL := /bin/bash
REPO_DIR ?= $(shell git rev-parse --show-toplevel)


.PHONY: format
format:
	echo $(REPO_DIR)
	poetry run ruff format $(REPO_DIR)/src  # run `black`
	poetry run ruff check $(REPO_DIR)/src --select I --fix   # run `isort`


.PHONY: lint
lint:
	poetry run ruff check $(REPO_DIR)/src