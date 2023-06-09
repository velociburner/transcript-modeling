FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime

WORKDIR /app

ADD ./src /app/src
ADD ./data /app/data
COPY requirements.txt ./requirements.txt

RUN apt update && apt install -y gcc wget
RUN wget -O best_model "https://transcript-modeling.s3.ca-central-1.amazonaws.com/best_model"
RUN pip install -r requirements.txt

EXPOSE 8501

ENTRYPOINT [ "streamlit", "run" ]

CMD [ "src/home.py" ]
