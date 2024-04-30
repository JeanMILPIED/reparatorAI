# probe-action/Dockerfile
FROM ghcr.io/puppeteer/puppeteer:22.7.1

# Install dependencies
RUN npm install puppeteer@22.7.1

COPY . /home/pptruser/src

RUN ls /home/pptruser/src

ENTRYPOINT [ "/bin/bash", "-c", "node -e \"$(</home/pptruser/src/probe.js)\"" ]
