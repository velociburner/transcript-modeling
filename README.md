# transcript-modeling
Final project for COSI 217b Natural Language Processing Systems

The entire application can be built and run using Docker. The image that it creates is quite large (~8GB) due to
PyTorch and its requirements, and downloading and storing the best model. It will take a few minutes to create for the
first time.
```sh
docker build -t transcript-modeling .
```

Run the container with the following command. Give it a minute to start up and download the PyTorch and BERT
requirements. Then, visit [http://127.0.0.1:8501](http://127.0.0.1:8501) on the host machine to access the webserver
running in the container.
```sh
docker run --rm -p 8501:8501 -v $PWD/instance:/app/instance --name transcript-modeling transcript-modeling
```
