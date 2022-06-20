# -------------------------
# Integration testing
# -------------------------

integration-build: ## Build environment for integration tests
	cd integration_tests && docker-compose build
.PHONY: integration-build

integration-tests: ## Run integration tests
	cd integration_tests && docker-compose down && docker-compose run --rm tests
.PHONY: integration-test

# -------------------------
# Development and unit testing
# -------------------------

dev-setup: ## Install development dependencies
	docker-compose up -d && docker-compose exec graphene_federation bash
.PHONY: dev-setup

tests: ## Run unit tests
	docker-compose run graphene_federation py.test graphene_federation --cov=graphene_federation -vv
.PHONY: tests

check-style: ## Run linting
	docker-compose run graphene_federation black graphene_federation --check
.PHONY: check-style

check-types: ## Run typing check
	docker-compose run graphene_federation mypy graphene_federation
.PHONY: check-types

# -------------------------
# Help
# -------------------------

help: ## Show help
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.PHONY: help

.DEFAULT_GOAL := help

.EXPORT_ALL_VARIABLES:
DOCKER_BUILDKIT = 1
COMPOSE_DOCKER_CLI_BUILD = 1

