# Run sample local embedded Dashboard

## ZF-Dashboard

1. Configure on `.env`: `SUPERSET_URL=http://host.docker.internal:8088`
2. Run zf-dashboard locally on Docker

## Superset

1. Run `make build`
2. Run `make run`
3. Log in and make sure you have a Dashboard configured to be embedded. Copy the ID of the Dashboard

## Sample

1. Edit the ID of the `embedded/sample.html` to the one you copied
2. You might have some CORS issues locally. Open Chrome running `open -n -a /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --args --user-data-dir="/tmp/chrome_dev_test" --disable-web-security` to avoid CORS problems at all
3. Open `embedded/sample.html` in your browser

# Tips

- Run `cd superset-frontend` and `npm run build-dev` to run assets locally faster
- Run `make build` and `make run` to update Superset if you change Phyton code