FROM node:16.13.2-alpine as build
COPY package.json /app/package.json
COPY yarn.lock /app/yarn.lock

COPY bomberland-library/package.json /app/bomberland-library/package.json
COPY bomberland-library/tsconfig.json /app/bomberland-library/tsconfig.json


COPY ./bomberland-engine/package.json /app/bomberland-engine/package.json

WORKDIR /app
RUN yarn install

COPY bomberland-library /app/bomberland-library

WORKDIR /app/bomberland-library
RUN yarn build
WORKDIR /app/bomberland-engine
RUN yarn install
COPY ./bomberland-engine /app/bomberland-engine
RUN yarn run test

ARG ENVIRONMENT
ENV ENVIRONMENT=${ENVIRONMENT}
ARG BUILD
ENV BUILD=${BUILD}

RUN yarn run build
RUN yarn run build:windows
RUN yarn run build:linux
RUN yarn run build:osx

# copy artifacts
FROM ubuntu:20.10
COPY --from=build /app/bomberland-engine/linux /app/bomberland-engine
WORKDIR /app
RUN chmod +x ./bomberland-engine
ENTRYPOINT ["/app/bomberland-engine"]
