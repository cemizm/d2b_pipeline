DOCKERRUN	= 
PVSERVEPY	= docker run -it --rm -v $(PWD)/:/src pvserve:runtime python
#PVSERVEPY	= nvidia-docker run -it --rm -v $(PWD)/:/src pvserve:runtime python

.PHONY:image
image:
	@docker build -t pvserve:runtime -f dockerfiles/run.dockerfile ./dockerfiles/
	@docker build -t pvserve:notebook -f dockerfiles/nb.dockerfile ./dockerfiles/

.PHONY:ingest
ingest:
	@$(PVSERVEPY) ingest.py

.PHONY:clean
clean:
	@$(PVSERVEPY) clean.py

.PHONY:prepare
prepare:
	@$(PVSERVEPY) prepare.py

.PHONY:train1
train1:
	docker run -d --rm --name e1 -v $(PWD)/:/src pvserve:runtime python train.py -e 1

.PHONY:train2
train2:
	docker run -d --rm --name e2 -v $(PWD)/:/src pvserve:runtime python train.py -e 2

.PHONY:train3
train3:
	docker run -d --rm --name e3 -v $(PWD)/:/src pvserve:runtime python train.py -e 3

.PHONY:validate
validate:
	@$(PVSERVEPY) validate.py

.PHONY:all
all: ingest clean prepare train1 train2 train3 validate

.PHONY:jupyter
jupyter: jupyter-srv jupyter-token

.PHONY:jupyter-srv
jupyter-srv:
	@docker run --rm -d --name pvservnb -p 10001:8888 -v $(PWD):/home/jovyan/work pvserve:notebook
	@printf "Wait for Notebook Server start "
	@sleep 3s
	@echo "done"

.PHONY:jupyter-token
jupyter-token:
	@docker exec pvservnb jupyter notebook list | grep 'http' | sed 's/0.0.0.0:8888/localhost:10001/g'

.PHONY:stop
stop:
	@docker stop pvservnb
