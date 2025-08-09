.PHONY: help install setup run-backend run-frontend run test clean

help:
	@echo "Available commands:"
	@echo "  make install      - Install all dependencies"
	@echo "  make setup        - Set up the project structure"
	@echo "  make run-backend  - Run the backend server"
	@echo "  make run-frontend - Run the frontend server"
	@echo "  make run          - Run both backend and frontend"
	@echo "  make test         - Run tests"
	@echo "  make clean        - Clean up generated files"

install:
	pip install -r requirements.txt
	cd frontend && npm install

setup:
	python scripts/setup.py

run-backend:
	cd backend && uvicorn app.main:app --reload

run-frontend:
	cd frontend && npm run dev

run:
	@echo "Starting backend and frontend..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "Press Ctrl+C to stop"
	@make -j 2 run-backend run-frontend

test:
	python scripts/generate_test_data.py
	python scripts/test_full_pipeline.py test_images/simple_text.jpg

test-benchmark:
	python scripts/benchmark.py test_images/*.jpg --workers 4

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf data/uploads/*
	rm -rf data/processed/*
	rm -rf data/cache/*
	touch data/uploads/.gitkeep
	touch data/processed/.gitkeep
	touch data/cache/.gitkeep

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f