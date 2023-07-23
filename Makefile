# Developing
install_all:
	poetry install --with dev

format_all:
	isort .
	black .
