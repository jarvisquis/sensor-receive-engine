.PHONY: export_requirements
export_requirements:
	cd sensor_receive_engine && poetry export -f requirements.txt --without-hashes > requirements.txt

.PHONY: lint
lint:
	find sensor_receive_engine -type f -name "*.py" | xargs pylint

.PHONY: fmt
fmt:
	black -l 120 sensor_receive_engine/

.PHONY: sort_imports
sort_imports:
	isort --recursive sensor_receive_engine/

.PHONY: prepare_push
prepare_push: fmt sort_imports export_requirements lint