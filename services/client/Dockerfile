# pull official base image
FROM node:15.1.0-alpine3.12


# set working directory
WORKDIR /usr/src/app

# add `/usr/src/app/node_modules/.bin` to $PATH
ENV PATH /usr/src/app/node_modules/.bin:$PATH

# install and cache app dependencies
COPY package.json .
COPY package-lock.json .
RUN apk add --no-cache --virtual build-dependencies \
    python2 \
    python3 \
    make \
    g++ \
    && npm install \
    && apk del build-dependencies
RUN npm ci
RUN npm install react-scripts@4.0.3 -g --silent

# start app
CMD ["npm", "start"]
