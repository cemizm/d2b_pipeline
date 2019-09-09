.PHONY:image
image:
	docker build -t pvserve:runtime -f dockerfiles/run.dockerfile ./dockerfiles/
	docker build -t pvserve:notebook -f dockerfiles/nb.dockerfile ./dockerfiles/

.PHONY:ingest
ingest:
	docker run -it --rm -v $(PWD)/:/src pvserve:runtime python ingest.py

.PHONY:prepare
prepare:
	docker run -it --rm -v $(PWD)/:/src pvserve:runtime python prepare.py

.PHONY:jupyter
jupyter:
	docker run --rm -d --name pvservnb -p 10001:8888 -v $(PWD):/home/jovyan/ pvserve:notebook
