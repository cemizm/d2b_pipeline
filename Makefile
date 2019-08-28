
.PHONY:images
images:
	docker build -t pvserve-d2b -f dockerfiles/Dockerfile ./dockerfiles

.PHONY:ingest
ingest:
	docker run -it --rm -v $(PWD)/:/src pvserve-d2b python ingest.py