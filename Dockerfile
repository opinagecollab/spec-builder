FROM python:3.7

RUN mkdir -p /app

WORKDIR /app

COPY requirements.txt .

RUN pip install torch torchvision
RUN pip install -r requirements.txt

COPY ./ .

CMD ["python", "-m", "spec_builder"]