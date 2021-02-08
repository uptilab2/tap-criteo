# tap-criteo

This is a [Singer](https://singer.io) tap that produces JSON-formatted data
following the [Singer
spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This tap:

- Pulls raw data from Criteo Marketing Solutions API (https://developers.criteo.com/marketing-solutions/docs)
- Extracts the following resources:
  - Analytics (https://developers.criteo.com/marketing-solutions/docs/analytics)
- Outputs the schema for each resource
- Incrementally pulls data based on the input state

### Config
```
{
  "username": string,
  "password": string,
  "start_date": string (YYYY-MM-DD),
  "advertiser_id": comma separated string, (default: all)
  "currency": string (default: EUR)
}
```

---

Copyright &copy; 2021 Stitch, Reeport
