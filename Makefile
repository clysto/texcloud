start:
	uvicorn texcloud.main:app

docker:
	docker build -t texcloud .
