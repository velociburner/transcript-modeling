FROM python:3.10-slim

WORKDIR /app

COPY . .

COPY requirements.txt ./requirements.txt

RUN apt update && apt install -y build-essential gcc-10
RUN pip install -r requirements.txt

EXPOSE 5000

ENTRYPOINT [ "streamlit", "run" ]

CMD [ "Home.py" ]
