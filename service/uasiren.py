import json
import os
from dotenv import load_dotenv

import aiohttp
from uasiren.client import Client

from utils.request import BaseRequest

load_dotenv(verbose=True)

script_dir = os.path.dirname(os.path.abspath(__file__))
ua_region_data_path = os.path.join(script_dir, "..", "dataset", "ua_regions.json")
ua_region_lang_path = os.path.join(script_dir, "..", "dataset", "ua_region_match.json")


class UASiren(BaseRequest):
    def __init__(self):
        super().__init__()
        with open(ua_region_data_path, "r") as file_raw:
            self.ua_region_data = json.loads(file_raw.read())["states"]
        with open(ua_region_lang_path, "r") as file_raw:
            self.ua_region_lang = json.loads(file_raw.read())
        self.uasiren_client: Client | None = None

    async def create_session(self) -> None:
        async with aiohttp.ClientSession() as session:
            self.uasiren_client = Client(session)

    def region_translate_ua(self, region_name: str) -> str:
        for region_en, region_ua in self.ua_region_lang.items():
            if (region_name in region_en) or (region_en in region_name):
                return region_ua

    def get_region_id(self, region_name: str) -> int:
        for region in self.ua_region_data:
            if region_name in region["regionName"]:
                return int(region["regionId"])

    async def get_alerts(self, region_id: int):
        region_alert_datasets = await self.get(
            "https://map.ukrainealarm.com/api/data/getStatesHistory",
            headers={"Authorization": "Bearer " + os.environ["UA_ALERT_TOKEN"]},
        )
        region_alert_datasets_json: list[dict] = json.loads(
            await region_alert_datasets.text()
        )
        for each_region in region_alert_datasets_json:
            if each_region["regionId"] == str(region_id):
                return each_region["alarms"]
