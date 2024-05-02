# probe-action/Dockerfile
# FROM ghcr.io/puppeteer/puppeteer:17.0.0
# COPY . /home/pptruser/src
# ENTRYPOINT [ "/bin/bash", "-c", "node -e \"$(</home/pptruser/src/probe.js)\"" ]

FROM ghcr.io/puppeteer/puppeteer:17.0.0
WORKDIR /home/pptruser/src
COPY package.json package-lock.json ./
RUN npm install
COPY . .
CMD ["node", "probe.js"]
