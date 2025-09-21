.PHONY: install run lint type test fix format

install:
	pip install -r requirements.txt

run:
	cd src && python ParkingManager.py

lint:
	ruff check .

fix:
	ruff check . --fix

type:
	mypy src

test:
	pytest
