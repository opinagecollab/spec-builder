FROM python:3.7

# Git specific directives
ARG SSH_PRIVATE_BFKEY
RUN mkdir ~/.ssh/
RUN echo "${SSH_PRIVATE_BFKEY}" > ~/.ssh/id_ed25519
RUN chmod 600 ~/.ssh/id_ed25519
RUN cat ~/.ssh/id_ed25519
RUN ssh-keyscan github.wdf.sap.corp >> ~/.ssh/known_hosts
RUN git config --global http.sslverify false

# App specific directives
RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt .

RUN pip install torch torchvision
RUN pip install -r requirements.txt

COPY ./ .

CMD ["python", "-m", "spec_builder"]