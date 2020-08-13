.phony: docker-build, docker-run, docker-run-background, verify

docker-build:
	docker build -t app:build .

docker-run:
	docker container run --rm --name http3 -v `pwd`/keys:/keys -p 8000:8000/tcp -p 4433:4433/udp app:build server


docker-run-background:
	docker container run -d --rm --name http3 -v `pwd`/keys:/keys -p 8000:8000/tcp -p 4433:4433/udp app:build server

docker-stop:
	docker stop http3

bin/h3client: 
	python3.8 -m venv . 
	bin/python setup.py develop

verify: bin/h3client
	bin/h3client https://0.0.0.0:4433/other -v -k
