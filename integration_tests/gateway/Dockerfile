FROM node:18-alpine

WORKDIR /project
COPY package.json package-lock.json ./
ENV NPM_CONFIG_LOGLEVEL warn

RUN npm install -g npm@9.6.1
RUN npm clean-install
RUN apk add curl

CMD [ "npm", "start"]
