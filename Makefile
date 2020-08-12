
docker-build:
	docker build -t app:build .

docker-run:
	docker container run --rm --name http3 -v `pwd`/keys:/keys -p 8000:8000/tcp -p 4433:4433/udp app:build server

