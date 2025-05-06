``
This project primarily aims to demonstrate the process of transferring configuration settings from one Docker container to another. It provides a hands-on guide to help users understand and implement the transfer effectively, thereby ensuring seamless container deployment and operation.
``

```
docker build --progress plain -t shared/shared:latest . --no-cache
docker build --progress plain -t weather/api:latest . --no-cache
docker compose up
```

```
services:
  api:
    image: weather/api:latest
    container_name: api
    restart: unless-stopped
    environment:
      - ASPNETCORE_ENVIRONMENT=Development # optional
    ports:
      - 9015:80
```
