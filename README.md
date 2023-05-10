# transcript-modeling
Final project for COSI 217b Natural Language Processing Systems

Build Docker image:
```sh
docker build -t transcript-modeling .
```

Run the container:
```sh
docker run --rm -p 8501:8501 -v $PWD/instance:/app/instance --name transcript-modeling transcript-modeling
```

Visit [http://127.0.0.1:8501](http://127.0.0.1:8501) on the host machine to access the webserver running in the container.
