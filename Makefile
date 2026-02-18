SHELL := /bin/bash
REPO_DIR ?= $(shell git rev-parse --show-toplevel)


.PHONY: format
format:
	echo $(REPO_DIR)
	uv run ruff format $(REPO_DIR)/src  # run `black`
	uv run ruff check $(REPO_DIR)/src --select I --fix   # run `isort`


.PHONY: lint
lint:
	uv run ruff check $(REPO_DIR)/src
	uv run mypy $(REPO_DIR)/src


# MacOS only!
.PHONY: restart-docker
restart-docker:
	osascript -e 'quit app "Docker"'
	open -a Docker