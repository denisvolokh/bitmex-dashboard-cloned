FROM mhart/alpine-node

RUN mkdir /code
WORKDIR /code
COPY webapp /code/

RUN yarn global add serve

EXPOSE 3000

CMD ["serve", "-s", "build", "-l", "3000"]