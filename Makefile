.PHONY:image
image:
	@docker build -t pvserve:runtime -f dockerfiles/run.dockerfile ./dockerfiles/
	@docker build -t pvserve:notebook -f dockerfiles/nb.dockerfile ./dockerfiles/

.PHONY:ingest
ingest:
	@docker run -it --rm -v $(PWD)/:/src pvserve:runtime python ingest.py

.PHONY:explore
explore:
	@docker run -it --rm -v $(PWD)/:/src pvserve:runtime python explore.py

.PHONY:prepare
prepare:
	@docker run -it --rm -v $(PWD)/:/src pvserve:runtime python prepare.py

.PHONY:train
train:
	@docker run -it --rm -v $(PWD)/:/src pvserve:runtime python train.py

.PHONY:validate
validate:
	@docker run -it --rm -v $(PWD)/:/src pvserve:runtime python validate.py

.PHONY:all
all: ingest explore prepare train 

.PHONY:jupyter
jupyter:
	@docker run --rm -d --name pvservnb -p 10001:8888 -v $(PWD):/home/jovyan/work pvserve:notebook
	@printf "Wait for Notebook Server start "
	@while [[ "$$(curl -s -o /dev/null -w ''%{http_code}'' localhost:10001/login)" != "200" ]]; do printf "."; sleep 2; done
	@echo "done"
	@docker exec pvservnb jupyter notebook list | grep 'http' | sed 's/0.0.0.0:8888/localhost:10001/g'

.PHONY:stop
stop:
	@docker stop pvservnb
