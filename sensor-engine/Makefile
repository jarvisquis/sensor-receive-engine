.PHONY: export_requirements
export_requirements:
	poetry export -f requirements.txt --without-hashes > requirements.txt

.PHONY: lint
lint:
	find . -type f -name "*.py" | xargs pylint --rcfile=sensor-engine/.pylintrc

.PHONY: fmt
fmt:
	black -l 120 ./

.PHONY: sort_imports
sort_imports:
	isort --recursive ./

.PHONY: prepare_push
prepare_push: fmt sort_imports export_requirements lint