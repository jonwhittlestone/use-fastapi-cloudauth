# use-fastapi-cloudauth

Demonstration of how to use `fastapi-cloudauth` with cognito, without a login form.

To appear authenticated using the `fastapi-cloudauth`'s dependencies, you need a valid bearer token first.

🙏Thanks to [fastapi-cloudauth](https://github.com/tokusumi/fastapi-cloudauth) for all the hard work.

## Pre requisite

- You already have a Cognito user pool created. [[use this template](https://github.com/jonwhittlestone/learn-fastapi-with-cognito/blob/main/infrastructure/cloudformation/cognito.yaml)]

## Example usage

1. Create your virtual env and add dependencies

```bash
$ python3.12 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
```

2. Create & populate your `.env` file using the example.

```bash
$ cp .env.example .env
```

3. Run the server

```bash
$ python main.py
```

4. Hit the `/get-token` endpoint

```bash
curl --request POST \
  --url http://localhost:8888/get-token \
  --header 'Content-Type: application/json' \
  --data '{
  "username": "{{USERNAME}}",
  "password": "{{PASSWORD}}",
  "email": "{{EMAIL}}"
}'
```

5. In the Swagger UI, use the `Authorize 🔒` button & enter the token

6. Hit a protected endpoint
