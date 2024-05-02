# probe-action/Dockerfile
FROM ghcr.io/puppeteer/puppeteer:17.0.0
COPY ./probe-action/probe.js /home/pptruser/src/probe.js
ENTRYPOINT [ "/bin/bash", "-c", "node -e \"$(</home/pptruser/src/probe.js)\"" ]
