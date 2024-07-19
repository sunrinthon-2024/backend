import asyncio
import json

import aiohttp
from uasiren.client import Client


async def main():
    async with aiohttp.ClientSession() as session:
        client = Client(session)

        # All response formats are available here: https://api.ukrainealarm.com/swagger/index.html
        regions = await client.get_regions()
        with open("../dataset/ua_regions.json", "w") as file:
            # Step 4: Use json.dump() to write the data
            json.dump(regions, file, indent=2, ensure_ascii=False)

        # all_alerts = await client.get_alerts()
        # print("all alerts", all_alerts)

        region_alerts = await client.get_alerts(4)
        print("alerts of region 16", region_alerts)
        #
        # last_alert_index = await client.get_last_alert_index()
        # print("last alert index", last_alert_index)


asyncio.run(main())
