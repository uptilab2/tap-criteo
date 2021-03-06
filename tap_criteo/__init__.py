#!/usr/bin/env python3
import json
import sys
import singer
from datetime import datetime, timedelta
from tap_criteo.client import CriteoClient, DATE_FORMAT
from tap_criteo.discover import discover


REQUIRED_CONFIG_KEYS = ["username", "password"]
logger = singer.get_logger()


def do_discover():

    logger.info('Starting discover')
    catalog = discover()
    json.dump(catalog.to_dict(), sys.stdout, indent=2)
    logger.info('Finished discover')


def sync(client, config, state, catalog):
    """ Sync data from tap source """
    # Loop over selected streams in catalog
    for stream in catalog.get_selected_streams(state):
        stream_id = stream.tap_stream_id
        logger.info("Syncing stream:" + stream_id)

        singer.write_schema(
            stream_name=stream_id,
            schema=stream.schema.to_dict(),
            key_properties=stream.key_properties,
        )

        yesterday = datetime.now() - timedelta(1)
        day = state.get(stream_id) or config.get('start_date')
        day = day and datetime.strptime(day, DATE_FORMAT) or yesterday

        while day <= yesterday:
            tap_data = client.request_report(stream, day)
            singer.write_records(stream_id, tap_data)
            state[stream_id] = day.strftime(DATE_FORMAT)
            singer.write_state(state)
            day += timedelta(1)

    return


@singer.utils.handle_top_exception(logger)
def main():
    # Parse command line arguments
    parsed_args = singer.utils.parse_args(REQUIRED_CONFIG_KEYS)
    config = parsed_args.config
    with CriteoClient(
        config['username'],
        config['password'],
        config.get('advertiser_id'),
        config.get('currency')
    ) as client:
        if parsed_args.discover:
            do_discover()
        elif parsed_args.catalog:
            sync(
                client=client,
                config=config,
                catalog=parsed_args.catalog,
                state=parsed_args.state or {}
            )


if __name__ == "__main__":
    main()
