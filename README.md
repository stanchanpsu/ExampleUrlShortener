# Example URL Shortener server

## Install

```sh
pip install -r requirements.txt
```

## Run server

```sh
python app.py
```

## REST API

### Shorten URL

#### Auto-shorten

```sh
curl -d '{"url":"google.com"}' -H "Content-Type: application/json" \
-X POST http://localhost:5000/shorten
```

#### Vanity URL

```sh
curl -d '{"url":"google.com", "short_code":"barbie"}' -H "Content-Type: application/json" \
-X POST http://localhost:5000/shorten
```

### Redirect to shortened URL

```sh
curl http://localhost:5000/<short_code>
```
