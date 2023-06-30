# Filecoin Data Onboarding Report

This dashboard shows the rate of data onboarding to Filecoin for a specific client.

To run it locally (in Docker), clone this repository and build a docker image:

```
$ docker image build -t fil-onboarding-report .
```

Rename `.env.example` file to `.env` and update missing values.

Run a container from the freshly built Docker image:

```
$ docker container run --rm -it -p 8501:8501 --env-file=.env fil-onboarding-report
```

Alternatively, use Docker Compose:

```
$ docker compose up -d
```

#For Live Development
There is a special version of the docker container intended for live updates and development

```
$ docker image build -t fil-onboarding-report -f Dockerfile .

$ docker container run --rm -it -p 8501:8501 --env-file=.env -v "$(pwd):/app" fil-onboarding-report
```

Also for live development to work, a new folder called `.streamlit` needs to be added with `config.toml` inside it. In `config.toml` this code needs to be added:

```
# this is needed for local development with docker
[server]
# if you don't want to start the default browser:
headless = true
# you will need this for local development:
runOnSave = true

# If running docker on windows host:
# fileWatcherType = "poll"
```

Access http://localhost:8501/ in a web browser for interactive insights.
