# Deploy

This repo deploys two instances of superset, each one with a different `.terra` configuration:

## Superset internal (aka Superset Big)

Used for internal ZeroFox employees only as it has more internal data.

Links:

- QA: https://build.zerofox.com/job/superset-qa-deploy/
- Stag: https://build.zerofox.com/job/superset-stag-deploy/
- Prod: https://build.zerofox.com/job/superset-prod-deploy/

## Insights (aka Superset external or Superset Small)

Used for external users. It has less data and it is accesible from cloud.zerofox.com through ZF-Dashboard. Only ZeroFox employees can access the UI through the VPN.

Links:

- QA: https://build.zerofox.com/job/insights-qa-deploy/
- Stag: https://build.zerofox.com/job/insights-stag-deploy/
- Prod: https://build.zerofox.com/job/insights-prod-deploy/