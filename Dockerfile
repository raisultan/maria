FROM python:3-slim

RUN apt update && apt -y upgrade && apt-get install -y --no-install-recommends git
RUN apt install -y curl jq build-essential

ADD requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

ADD entrypoint.sh /entrypoint.sh
RUN chmod +x entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
