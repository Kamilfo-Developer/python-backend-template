.PHONY: lint
lint:
	ruff check . --diff
	mypy --install-types --non-interactive --config-file setup.cfg . 
	

.PHONY: style
style:
	ruff format . --check --diff
	isort . -c --diff

.PHONY: format
format:
	ruff format .
	isort .

.PHONY: test 
test:
	pytest -v -s

.PHONY: testcvg
testcvg:
	coverage run -m pytest -v -s && coverage report -m

.PHONY: testdbg
testdbg:
	pytest -v -s --pdb 

.PHONY: ftest
ftest: format test

.PHONY: flint
flint: format lint

.PHONY: dev-compose
dev-compose:
	docker compose -p app -f deployment/docker-compose.local.yml up -d --build --remove-orphans

.PHONY: dev-destroy
dev-destroy:
	docker compose -p app -f deployment/docker-compose.local.yml down -v --remove-orphans
