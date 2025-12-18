# Slack

## Create an automatic connection list to Slack via the WEB API

## How to run this project

- 1.first build the docker image
write this command:

```bash
docker build -t  <my_image> .
```

then run this command:

```bash
docker run  <my_image>
```

Then a list of those connected to Slack will be printed
to the terminal

- 2.How insert a new client to slack:

  - run the command:

```bash
docker run  <my_image> <userId> <userName> <userEmail>
```
