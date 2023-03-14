FROM node:18-alpine

WORKDIR /project
COPY package.json package-lock.json ./
ENV NPM_CONFIG_LOGLEVEL warn

RUN npm clean-install --unsafe-perm=true
RUN apk add curl

CMD [ "npm", "start"]
