CONFIG=$(HOME)/.vropscli.yml
DOCKERIMG="ssmiller25/vropscli-dev:latest"

.PHONY: devenv
devenv:
	touch $(CONFIG)
	# TODO: Get pipenv installed as generate non-roto user, WITH bindmounts working...
	#docker run --user $(shell id -u) --rm -i -t -v=$(CONFIG):/.vropscli.yml -v=$(PWD):/vropscli vropscli-dev sh
	docker run --rm -i -t -v=$(CONFIG):/root/.vropscli.yml -v=$(PWD):/vropscli $(DOCKERIMG) sh

.PHONY: builddevenv
builddevenv:
	docker build -f Dockerfile.devenv -t $(DOCKERIMG) .


.PHONY: pushdevenv
pushdevenv:
	docker $(DOCKERIMG)


# scrach environment to experiment with buildenv
.PHONY: scratchenv
scratchenv:
	touch $(CONFIG)
	docker run --rm -i -t -v=$(CONFIG):/.vropscli.yml -v=$(PWD):/vropscli python:3.7 sh

# Python tests will record session.  Although bearer token should be temporary, still replacing it with generic uuid in
# same format as a precaution
.PHONY: cleanauth
cleanauth:
	sed -i 's#vRealizeOpsToken .*#vRealizeOpsToken 0f0f0f0f-0f0f-0f0f-0f0f-0f0f0f0f0f0f::0f0f0f0f-0f0f-0f0f-0f0f-0f0f0f0f0f0f#' fixtures/vcr_cassettes/*

.PHONY: clean
clean:
	docker rmi $(DOCKERIMG)
	docker image prune

