FROM almalinux:9.4-minimal

# move files
RUN mkdir -p /usr/local/src/bot
ADD bot.py /usr/local/src/bot/bot.py
ADD requirements.txt /usr/local/src/bot/requirements.txt
ADD .env /usr/local/src/bot/.env

# install python and requirements
RUN dnf install -y python3 python3-pip && \
    pip3 install -r /usr/local/src/bot/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN playwright install

# run bot
CMD ["nohup", "python3", "/usr/local/src/bot/bot.py", "2>&1", "&"]