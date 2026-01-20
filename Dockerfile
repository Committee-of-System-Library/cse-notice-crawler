FROM python:latest

WORKDIR /discord_Crawler

RUN pip install requests bs4 --root-user-action=ignore requests

CMD ["/bin/sh", "-c", "tail -f /dev/null"]
