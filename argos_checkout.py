import asyncio
import json
import os
import traceback
from datetime import datetime

from quart import Quart, request, jsonify
import aiofiles

import discord
from curl_cffi import requests
from discord import app_commands
from discord.ext import commands, tasks
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes


bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
tree = bot.tree
app = Quart(__name__)

urls = {}
user_data = []


KEY_LENGTH = 32
SALT_LENGTH = 16
BLOCK_SIZE = 16

temporary_urls = {}
first_checkout = True

links_file = "argos-links"
data_file = "argos-data"

CHANNEL_ID = 1248232866328870984


cookies = {
    "analytics_channel": "ecomm",
    "sessionId": "Mm1w+D09+yHAzDJy+dqQmQAUfAxCpsuMKq6ChC/CBmxwLsJ6om7Wm05tv4SO9FxL",
    "CONSENTMGR": "consent:true|ts:1718443092317|id:01901b309dfb002d430c478c54d40506f004e06700bd0",
    "AMCVS_095C467352782EB30A490D45%40AdobeOrg": "1",
    "s_ecid": "MCMID|52333693957573260961282996317864418467",
    "_gcl_au": "1.1.2130043158.1718443095",
    "ArgosPopUp_customer1In20Chance": "false",
    "_scid": "0832839f-e5f4-4b9d-97f7-31d74855f09b",
    "_pin_unauth": "dWlkPVlUSTVaalZtTkRFdFkySXdaaTAwTlRObExUZzFPRGN0TnpneFltVXhZV1ExTkRNeQ",
    "umdid": "Yjc2NTZmYmQtZTliYi00MjM0LWEyNmMtYTNhMTdkZjg3YTZhfDlhNzZkMzk4LTljZTMtNDQwYS05ZDQ1LTk5OGJhYjMxNzBlOHww",
    "_tt_enable_cookie": "1",
    "_ttp": "Z09118AaqefwImztQKIvT8H9J0j",
    "_cls_v": "e8c547b9-be6e-4861-ba33-c9f464a53626",
    "_cls_s": "805ab256-4c7b-46ba-a8f7-1f162d257927:0",
    "_taggstar_vid": "33d3b641-2af8-11ef-977e-317ce98a3699",
    "multiple_tabs": "0",
    "syte_uuid": "2ff60630-2b2d-11ef-847c-7beabef0b7f3",
    "BVBRANDID": "bc531a8e-8085-47c2-85c7-3a43c58ff7e0",
    "syte_ab_tests": "{}",
    "WC_SESSION_ESTABLISHED": "true",
    "WC_ACTIVEPOINTER": "110,10151",
    "x_arg_pm_rv": "90",
    "PDP_Test_Group_1": "2",
    "Checkout_Test_Group_2": "NEW_HD|NEW_HD_SI|NEW_HD_LI",
    "WC_PERSISTENT": "UfYVbvGC9zbLHoj3RMjOEOxWe34=%0A%3B2024-07-11+13%3A15%3A17.7_1720700117227-8013168_10151_-1002,110,GBP_10151",
    "WC_AUTHENTICATION_-1002": "-1002,5Ce8ewpCVheUcD8tRlGdytomv7Q%3D",
    "WC_USERACTIVITY_-1002": "-1002,10151,null,null,null,null,null,null,null,null,PVBTboGSCF/m58oT3GPxxlHhSnhuQeucqf4ZKMXeloYHUrLbNDLb3W4n95q5znRg8jjH4qKe5580nxXrUjxaMceOepiRHb7Uo1zpjy846au2wuh+Ka8pkJpdX0SbVbdoqWDbfgsysovAQyFroERmsymIRGP/O54/tFP7YSNsSPZHg5AUCDlGKCKGJcT2ePhrdUEU/z2PErwIACfue2cOg==",
    "WC_GENERIC_ACTIVITYDATA": "[109193615569:true:false:0:7/d5dCrIjeXkl3K3tVa4jyhpAro=][com.ibm.commerce.context.audit.AuditContext|1720700117227-8013168][com.ibm.commerce.store.facade.server.context.StoreGeoCodeContext|null&null&null&null&null&null][CTXSETNAME|Store][com.ibm.commerce.context.globalization.GlobalizationContext|110&GBP&110&GBP][com.ibm.commerce.catalog.businesscontext.CatalogContext|10001&null&false&false&false][com.ibm.commerce.context.base.BaseContext|10151&-1002&-1002&-1][com.ibm.commerce.context.experiment.ExperimentContext|null][com.ibm.commerce.context.entitlement.EntitlementContext|4000000000000000002&4000000000000000002&null&-2000&null&null&null][com.ibm.commerce.giftcenter.context.GiftCenterContext|null&null&null]",
    "_taggstar_exp": "v:3|id:tvt10|group:treatment",
    "rto": "c0",
    "_sctr": "1|1720645200000",
    "Basket_Checkout_Test_Group_2": "2",
    "LastUrlCookie": "/basket?storeId=10151&langId=110",
    "_gid": "GA1.3.1299677414.1720980356",
    "AWSALB": "SxKHYjJVbvsXhr0dd/GE8GrJ9BB17SKDebN4QHlljmw5KGKM+B/TJFvoBiGC3hwWs7UYCamvhuTc+zERJ5LlT2jEAaltlNapEz+EKRB6PwadS/EEI0nQD4t6lPgO",
    "AWSALBCORS": "SxKHYjJVbvsXhr0dd/GE8GrJ9BB17SKDebN4QHlljmw5KGKM+B/TJFvoBiGC3hwWs7UYCamvhuTc+zERJ5LlT2jEAaltlNapEz+EKRB6PwadS/EEI0nQD4t6lPgO",
    "Apache": "10.102.16.175.1721028371533555",
    "JSESSIONID": "0000jz2VgqFQ0y-J7LqunVX4YGJ:1fa1n730v",
    "_ScCbts": '["96;chrome.2:2:5"]',
    "AMCV_095C467352782EB30A490D45%40AdobeOrg": "179643557|MCIDTS|19920|MCMID|52333693957573260961282996317864418467|MCAAMLH-1721670482|6|MCAAMB-1721670482|RKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y|MCOPTOUT-1721072882s|NONE|MCAID|NONE|vVersion|5.5.0",
    "akavpau_vpc_pdpcd": "1721066283~id=8cd6afe88d6eb819be5d454027647d97",
    "cisId": "51956a83dec2415c8c327ecfeffdfc97",
    "akaas_arg_uk_global": "1722275284~rv=19~id=cc5c7610fac48209c1b8f033e96a0e55",
    "prev_vals": "ar:pdp:2289489:jeanpaulgaultierlemaleeaudetoilette-125ml:*|*ar:productdetails:",
    "ufvd": "~~clp_29203-Bk!clp_29164-U!brands_hugo-boss-e!clp_30299-U!brands_lego-U!clp_29351-o!brands_jean-paul gaultier-8",
    "_abck": "5EF1B75F8EED8482BD5FA5053A6C7B81~0~YAAQvTYQYLcruaCQAQAAhD+CtwwVFeZr9fNQd1CKiJ+ayWKsfLc47iaS8ebKThrrWUjObaiR6S01QGdteTfUF+Z8RVkDiT86ibHCzNpg0MN0nuYSMS252EhvtijHbO4lNDyX4S2w3ti3PuLlDdmLlFwOUEnLxsN3Xif9XBZmcekpFj4oZDmEYWpt2JunUhAyBOb6p7dEgPmCPb3eKpnu4Qnh4o6MHG9Il99DRn+cOA6oP8BrHUURKeDO1e8ZOfJ4HwRqrnj0UHb03Abjj4H1+5GW/36dcYVhyeqEMEkJfX5f58KguVkKvBvIqJSYnMnlI5+zm2arPVD358n8D8K1yZIEKdVDv8XM2Altndd/zN0A3hmSs4/Brg+DygOswjSMk49whZbYMnSLpbGoHGHfMBYGr2grXJhR0fSPbgnNS/urFBDwdGfAym3l5ZTw5kiJ4OE0jqF+AvdqPiupuRfUB/VtF5QP~-1~-1~-1",
    "bm_s": "YAAQvTYQYMEruaCQAQAAR0CCtwG4HSdlY0paFBoAPYgFvwsXKwRvBwCsG2U2Hnbee/3GJmkYP5+/iKTQEPEzHL6/KJaq2ox01XzrXOk4go/VVCRybnQV2OhU5o1pZC1IG2eowMhiv246qaoj/eKEcedJVPrFHH5Ib7oLrwQo0Zi55Iuk7lQ2u1NZG3bt/BtQdLZHqak4QUbyqN2VvAL4llyFwHrATMdDIKwiafP5jhpHbrnWuoQw3LiRsizGjuimDJfDYwxlMmomd0rLB+zMkcTqkIGkdcAnjgsitxeguBRN1ZOsbHuouJqf",
    "_scid_r": "0832839f-e5f4-4b9d-97f7-31d74855f09b",
    "_rdt_uuid": "1718443096020.ace3c6de-e2d0-443a-8c94-9ad04189dad0",
    "_uetsid": "b71e8400420b11efb99f67c268549ef0",
    "_uetvid": "4cc3f170d70111ee96fe8f3b830bf8b2",
    "_ga": "GA1.3.174205757.1718443095",
    "_derived_epik": "dj0yJnU9Y0VhNUc2YU5WVmZvVGx5TlFoYjJYWXRuT1NHV09SbXImbj1IYWVIeGhwQVhsN0xNelVZYi0xcl9RJm09MSZ0PUFBQUFBR2FWWU5ZJnJtPTEmcnQ9QUFBQUFHYVZZTlkmc3A9NQ",
    "Bc": "d:1*1_p:0*0.005_r:null*null",
    "utag_main": "v_id:01901b309dfb002d430c478c54d40506f004e06700bd0$_sn:16$_se:11$_ss:0$_st:1721067487674$vapi_domain:argos.co.uk$dc_visit:16$ses_id:1721065681854;exp-session$_pn:2;exp-session$dc_event:10;exp-session$dc_region:eu-west-1;exp-session",
    "RT": "z=1&dm=www.argos.co.uk&si=132a8ec1-21f1-4db9-a684-9794026e0dae&ss=lymnu8j0&sl=0&tt=0&bcn=%2F%2F0217991a.akstat.io%2F&ul=syz6e&hd=sz2mn",
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Referer": "https://www.argos.co.uk/browse/technology/televisions-and-accessories/televisions/c:30106/?clickOrigin=header:productdetails:menu:televisions",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Connection": "keep-alive",
    "Cookie": """analytics_channel=ecomm; sessionId=Mm1w+D09+yHAzDJy+dqQmQAUfAxCpsuMKq6ChC/CBmxwLsJ6om7Wm05tv4SO9FxL; CONSENTMGR=consent:true%7Cts:1718443092317%7Cid:01901b309dfb002d430c478c54d40506f004e06700bd0; AMCVS_095C467352782EB30A490D45%40AdobeOrg=1; s_ecid=MCMID%7C52333693957573260961282996317864418467; _gcl_au=1.1.2130043158.1718443095; ArgosPopUp_customer1In20Chance=false; _scid=0832839f-e5f4-4b9d-97f7-31d74855f09b; _pin_unauth=dWlkPVlUSTVaalZtTkRFdFkySXdaaTAwTlRObExUZzFPRGN0TnpneFltVXhZV1ExTkRNeQ; umdid=Yjc2NTZmYmQtZTliYi00MjM0LWEyNmMtYTNhMTdkZjg3YTZhfDlhNzZkMzk4LTljZTMtNDQwYS05ZDQ1LTk5OGJhYjMxNzBlOHww; _tt_enable_cookie=1; _ttp=Z09118AaqefwImztQKIvT8H9J0j; _cls_v=e8c547b9-be6e-4861-ba33-c9f464a53626; _cls_s=805ab256-4c7b-46ba-a8f7-1f162d257927:0; _taggstar_vid=33d3b641-2af8-11ef-977e-317ce98a3699; multiple_tabs=0; syte_uuid=2ff60630-2b2d-11ef-847c-7beabef0b7f3; BVBRANDID=bc531a8e-8085-47c2-85c7-3a43c58ff7e0; syte_ab_tests={}; WC_SESSION_ESTABLISHED=true; WC_ACTIVEPOINTER=110%2C10151; x_arg_pm_rv=90; PDP_Test_Group_1=2; Checkout_Test_Group_2=NEW_HD|NEW_HD_SI|NEW_HD_LI; WC_PERSISTENT=UfYVbvGC9zbLHoj3RMjOEOxWe34%3D%0A%3B2024-07-11+13%3A15%3A17.7_1720700117227-8013168_10151_-1002%2C110%2CGBP_10151; WC_AUTHENTICATION_-1002=-1002%2C5Ce8ewpCVheUcD8tRlGdytomv7Q%3D; WC_USERACTIVITY_-1002=-1002%2C10151%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2CPVBTboGSCF%2F%2Fm58oT3GPxxlHhSnhuQeucqf4ZKMXeloYHUrLbNDLb3W4n95q5znRg8jjH4qKe5580nxXrUjxaMceOepiRHb7Uo1zpjy846au2wuh%2BKa8pkJpdX0SbVbdoqWDbfgsysovAQyFroERmsymIRGP%2FO54%2FtFP7YSNsSPZHg5AUCDlGKCKGJcT2ePhrdUEU%2Fz2PErwIACfue2cOg%3D%3D; WC_GENERIC_ACTIVITYDATA=[109193615569%3Atrue%3Afalse%3A0%3A7%2Fd5dCrIjeXkl3K3tVa4jyhpAro%3D][com.ibm.commerce.context.audit.AuditContext|1720700117227-8013168][com.ibm.commerce.store.facade.server.context.StoreGeoCodeContext|null%26null%26null%26null%26null%26null][CTXSETNAME|Store][com.ibm.commerce.context.globalization.GlobalizationContext|110%26GBP%26110%26GBP][com.ibm.commerce.catalog.businesscontext.CatalogContext|10001%26null%26false%26false%26false][com.ibm.commerce.context.base.BaseContext|10151%26-1002%26-1002%26-1][com.ibm.commerce.context.experiment.ExperimentContext|null][com.ibm.commerce.context.entitlement.EntitlementContext|4000000000000000002%264000000000000000002%26null%26-2000%26null%26null%26null][com.ibm.commerce.giftcenter.context.GiftCenterContext|null%26null%26null]; _taggstar_exp=v:3|id:tvt10|group:treatment; rto=c0; _sctr=1%7C1720645200000; Basket_Checkout_Test_Group_2=2; LastUrlCookie=/basket?storeId=10151&langId=110; _gid=GA1.3.1299677414.1720980356; AWSALB=SxKHYjJVbvsXhr0dd/GE8GrJ9BB17SKDebN4QHlljmw5KGKM+B/TJFvoBiGC3hwWs7UYCamvhuTc+zERJ5LlT2jEAaltlNapEz+EKRB6PwadS/EEI0nQD4t6lPgO; AWSALBCORS=SxKHYjJVbvsXhr0dd/GE8GrJ9BB17SKDebN4QHlljmw5KGKM+B/TJFvoBiGC3hwWs7UYCamvhuTc+zERJ5LlT2jEAaltlNapEz+EKRB6PwadS/EEI0nQD4t6lPgO; Apache=10.102.16.175.1721028371533555; JSESSIONID=0000jz2VgqFQ0y-J7LqunVX4YGJ:1fa1n730v; _ScCbts=%5B%2296%3Bchrome.2%3A2%3A5%22%5D; AMCV_095C467352782EB30A490D45%40AdobeOrg=179643557%7CMCIDTS%7C19920%7CMCMID%7C52333693957573260961282996317864418467%7CMCAAMLH-1721670482%7C6%7CMCAAMB-1721670482%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1721072882s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.5.0; akavpau_vpc_pdpcd=1721066283~id=8cd6afe88d6eb819be5d454027647d97; cisId=51956a83dec2415c8c327ecfeffdfc97; akaas_arg_uk_global=1722275284~rv=19~id=cc5c7610fac48209c1b8f033e96a0e55; prev_vals=ar%3Apdp%3A2289489%3Ajeanpaulgaultierlemaleeaudetoilette-125ml%3A*%7C*ar%3Aproductdetails%3A; ufvd=~~clp_29203-Bk!clp_29164-U!brands_hugo-boss-e!clp_30299-U!brands_lego-U!clp_29351-o!brands_jean-paul%20gaultier-8; _abck=5EF1B75F8EED8482BD5FA5053A6C7B81~0~YAAQvTYQYLcruaCQAQAAhD+CtwwVFeZr9fNQd1CKiJ+ayWKsfLc47iaS8ebKThrrWUjObaiR6S01QGdteTfUF+Z8RVkDiT86ibHCzNpg0MN0nuYSMS252EhvtijHbO4lNDyX4S2w3ti3PuLlDdmLlFwOUEnLxsN3Xif9XBZmcekpFj4oZDmEYWpt2JunUhAyBOb6p7dEgPmCPb3eKpnu4Qnh4o6MHG9Il99DRn+cOA6oP8BrHUURKeDO1e8ZOfJ4HwRqrnj0UHb03Abjj4H1+5GW/36dcYVhyeqEMEkJfX5f58KguVkKvBvIqJSYnMnlI5+zm2arPVD358n8D8K1yZIEKdVDv8XM2Altndd/zN0A3hmSs4/Brg+DygOswjSMk49whZbYMnSLpbGoHGHfMBYGr2grXJhR0fSPbgnNS/urFBDwdGfAym3l5ZTw5kiJ4OE0jqF+AvdqPiupuRfUB/VtF5QP~-1~-1~-1; bm_s=YAAQvTYQYMEruaCQAQAAR0CCtwG4HSdlY0paFBoAPYgFvwsXKwRvBwCsG2U2Hnbee/3GJmkYP5+/iKTQEPEzHL6/KJaq2ox01XzrXOk4go/VVCRybnQV2OhU5o1pZC1IG2eowMhiv246qaoj/eKEcedJVPrFHH5Ib7oLrwQo0Zi55Iuk7lQ2u1NZG3bt/BtQdLZHqak4QUbyqN2VvAL4llyFwHrATMdDIKwiafP5jhpHbrnWuoQw3LiRsizGjuimDJfDYwxlMmomd0rLB+zMkcTqkIGkdcAnjgsitxeguBRN1ZOsbHuouJqf; _scid_r=0832839f-e5f4-4b9d-97f7-31d74855f09b; _rdt_uuid=1718443096020.ace3c6de-e2d0-443a-8c94-9ad04189dad0; _uetsid=b71e8400420b11efb99f67c268549ef0; _uetvid=4cc3f170d70111ee96fe8f3b830bf8b2; _ga=GA1.3.174205757.1718443095; _derived_epik=dj0yJnU9Y0VhNUc2YU5WVmZvVGx5TlFoYjJYWXRuT1NHV09SbXImbj1IYWVIeGhwQVhsN0xNelVZYi0xcl9RJm09MSZ0PUFBQUFBR2FWWU5ZJnJtPTEmcnQ9QUFBQUFHYVZZTlkmc3A9NQ; Bc=d:1*1_p:0*0.005_r:null*null; utag_main=v_id:01901b309dfb002d430c478c54d40506f004e06700bd0$_sn:16$_se:11$_ss:0$_st:1721067487674$vapi_domain:argos.co.uk$dc_visit:16$ses_id:1721065681854%3Bexp-session$_pn:2%3Bexp-session$dc_event:10%3Bexp-session$dc_region:eu-west-1%3Bexp-session; RT="z=1&dm=www.argos.co.uk&si=132a8ec1-21f1-4db9-a684-9794026e0dae&ss=lymnu8j0&sl=0&tt=0&bcn=%2F%2F0217991a.akstat.io%2F&ul=syz6e&hd=sz2mn"; _ga_JWCPD5SJK1=GS1.1.1721077007.19.0.1721077007.60.0.0"""
}


@app.post('/checkout')
async def get_message():
    request_data = await request.get_json()

    if not request_data:
        return jsonify({'error': 'channel_id and content are required'}), 400

    url = request_data["url"]
    price = request_data["price"]
    number = request_data["number"]
    tasks = request_data["tasks"]

    if not url or not price or not number or not tasks:
        return jsonify({'error': 'channel_id and content are required'}), 400

    urls[url] = {
        "price":float(price),
        "number":int(number),
        "tasks":int(tasks)
    }

    await add_url_to_file(url=url, price=float(price), count=int(number), tasks=int(tasks))
    await check_urls()

    return jsonify({'status': 'success'}), 200

async def add_url_to_file(url: str, price: float, count: int, tasks: int):
    global urls
    urls[url] = {
        "price":price,
        "number":count,
        "tasks":tasks
    }
    async with aiofiles.open(links_file, 'a') as file:
        await file.write(f"{url} || {str(price)} || {str(count)} || {str(tasks)} \n")


async def read_urls_from_file() -> dict:
    try:
        urls = {}
        async with aiofiles.open(links_file, 'r') as file:
            async for line in file:
                item = line.strip().split(" || ")

                urls[item[0]] = {
                    "price":float(item[1]),
                    "number":int(item[2]),
                    "tasks":float(item[3])
                }
        return urls
    except:
        traceback.print_exc()
        return {}


async def remove_url_from_file(url: str):
    if url in urls:
        urls.pop(url)
        async with aiofiles.open(links_file, 'w') as file:
            for remaining_url, data in urls.items():
                price = data["price"]
                count = data["number"]
                tasks = data["tasks"]
                await file.write(f"{url} || {str(price)} || {str(count)} || {str(tasks)} \n")


def write_encrypted_data_to_file(encrypted_data):
    with open(data_file, "ab") as file:
        file.write(encrypted_data + b'\n')


def read_encrypted_data_from_file():
    with open(data_file, "rb") as file:
        encrypted_data = file.read().strip()
    return encrypted_data


def derive_key(password, salt):
    return scrypt(password.encode(), salt, KEY_LENGTH, N=2**14, r=8, p=1)


def encrypt_data(data, password):
    salt = get_random_bytes(SALT_LENGTH)
    key = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data.encode())
    return salt + cipher.nonce + tag + ciphertext


def decrypt_data(encrypted_data, password):
    salt = encrypted_data[:SALT_LENGTH]
    nonce = encrypted_data[SALT_LENGTH:SALT_LENGTH + BLOCK_SIZE]
    tag = encrypted_data[SALT_LENGTH + BLOCK_SIZE:SALT_LENGTH + 2 * BLOCK_SIZE]
    ciphertext = encrypted_data[SALT_LENGTH + 2 * BLOCK_SIZE:]
    key = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag).decode()


async def checkout_items(url, count):
    count = min(10, count)
    data_dict = {
        "delivery_address1": user_data[0],
        "delivery_address2": user_data[1],
        "delivery_city": user_data[2],
        "delivery_zipcode": user_data[3],
        "phone_number": user_data[4],
        "first_name": user_data[5],
        "last_name": user_data[6],
        "email": user_data[7],
        "credit_card_number": user_data[8],
        "expiry_month": user_data[9],
        "expiry_year": user_data[10],
        "cvc_code": user_data[11],
        "billing_address1": user_data[12],
        "billing_address2": user_data[13],
        "billing_city": user_data[14],
        "billing_zipcode": user_data[15],
    }

    async def buy_quantity(page, number):
        await page.wait_for_selector("#add-to-trolley-quantity")
        await page.locator("#add-to-trolley-quantity").click()
        await asyncio.sleep(0.2)
        await page.select_option('#add-to-trolley-quantity', f'{min(number, 10)}')
        await asyncio.sleep(0.1)

    async def lower_count(page):
        number = int((await page.get_by_text("Only").nth(0).text_content()).split(" ")[1])
        await page.wait_for_selector("select")
        await page.locator("select").click()
        await asyncio.sleep(0.2)
        await page.select_option('select', f'{number}')
        await asyncio.sleep(0.1)
        await page.locator(".sm-row").first.click(timeout=30000)
        return number

    async def create_account(page):
        create_acc_btn = page.get_by_text("Create an account")
        await create_acc_btn.click()

        email = page.locator("#email")
        await email.click()
        await email.fill(data_dict["email"])

        await page.locator(".Buttonstyles__Button-sc-42scm2-2").click()

        title = page.locator("#personTitle")
        await title.click()
        await asyncio.sleep(0.1)
        await page.select_option("#personTitle", "Mr")

        first_name = page.locator("#firstName")
        await first_name.click()
        await first_name.fill(data_dict["first_name"])

        last_name = page.locator("#lastName")
        await last_name.click()
        await last_name.fill(data_dict["last_name"])

        phone = page.locator("#phone")
        await phone.click()
        await phone.fill(data_dict["phone_number"])

        await page.locator("div.text-right:nth-child(2) > button:nth-child(1)").click()

        address1 = page.locator("#houseNumber")
        await address1.click()
        await address1.fill(data_dict["delivery_address1"])

        address2 = page.locator("#address1")
        await address2.click()
        await address2.fill(data_dict["delivery_address2"])

        city = page.locator("#city")
        await city.click()
        await city.fill(data_dict["delivery_city"])

        zipcode = page.locator("#zipCode")
        await zipcode.click()
        await zipcode.fill(data_dict["delivery_zipcode"])

        await page.get_by_text("Save Billing Details").click()

        confirm_email = page.locator("#emailConfirm")
        await confirm_email.click()
        await confirm_email.type(data_dict["email"])

        password = page.locator("#password")
        await password.click()
        await password.type(data_dict["email"], delay=0.3)

        await asyncio.sleep(1)

        passwordConfirm = page.locator("#passwordConfirm")
        await passwordConfirm.click()
        await asyncio.sleep(0.4)
        await passwordConfirm.type(data_dict["email"], delay=0.5)

        await asyncio.sleep(2)

        await page.get_by_text("Continue").click()
        first_checkout = False

    async def log_in(page):
        await page.wait_for_selector('#email')
        mail = page.locator('#email')
        await mail.click()
        await mail.fill(data_dict["email"])

        password = page.locator('#password')
        await password.click()
        await password.fill(data_dict["email"])

        login = page.locator("button.Buttonstyles__Button-sc-42scm2-2")
        await login.click()

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled",
                                                                    "--disable-dev-shm-usage"])
            context = await browser.new_context(viewport={"width": 1920, "height": 1080},
                                                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
            page = await context.new_page()

            await page.goto(url)

            await page.wait_for_selector("#explicit-consent-prompt-accept")
            await page.locator("#explicit-consent-prompt-accept").click()

            await page.wait_for_selector('button.iRZNRI:nth-child(1)')
            await asyncio.sleep(0.3)

            if count != 1:
                await buy_quantity(page, count)

            buy_btn = page.locator('button.iRZNRI:nth-child(1)')
            await buy_btn.click()

            try:
                await page.wait_for_selector('a.Buttonstyles__Button-sc-42scm2-2', timeout=10000)
                continue_checkout = page.locator('a.Buttonstyles__Button-sc-42scm2-2')
                await continue_checkout.click()
            except:
                await page.goto("https://www.argos.co.uk/basket")

            await page.wait_for_selector('#basket-FulfilmentSelectorForm', state="attached")
            await asyncio.sleep(0.1)
            postal_code = page.locator('#basket-FulfilmentSelectorForm').nth(1)
            await postal_code.click()
            await postal_code.fill(data_dict["delivery_zipcode"])

            await asyncio.sleep(0.2)
            await page.wait_for_selector('#basket-FulfilmentSelectorForm-deliverButton', timeout=3000, state="attached")
            postal_code = page.locator('#basket-FulfilmentSelectorForm-deliverButton').nth(1)
            await postal_code.click()
            await asyncio.sleep(0.1)

            await page.locator(".sm-row").first.click(timeout=30000)
            if await page.locator(".Alertstyles-sc-1jefrhh-0").count() != 0:
                count = await lower_count(page)

            await page.wait_for_selector("//span[text()='Continue with delivery']")
            await page.keyboard.press('PageDown')
            basket_button = page.locator("//span[text()='Continue with delivery']")
            await basket_button.click()

            if first_checkout:
                await create_account(page)
            await log_in(page)

            await page.wait_for_selector('.GridVariantstyles__GridVariantWrapper-n9v5u0-1')
            await asyncio.sleep(0.5)
            checkout = await page.query_selector('.GridVariantstyles__GridVariantWrapper-n9v5u0-1')
            dates = await checkout.query_selector_all("li")
            for date in dates:
                if "Unavailable" in await date.text_content():
                    continue
                else:
                    await date.click()
                    break

            await page.keyboard.press('PageDown')

            await page.wait_for_selector('.Buttonstyles__Button-sc-42scm2-2')
            confirm = page.locator('.Buttonstyles__Button-sc-42scm2-2')
            await confirm.click()
            await asyncio.sleep(0.5)

            await page.wait_for_selector('button.Buttonstyles__Button-sc-42scm2-2:nth-child(6)')
            await asyncio.sleep(1)
            confirm2 = page.locator('button.Buttonstyles__Button-sc-42scm2-2:nth-child(6)')
            await confirm2.click()

            await page.keyboard.press('PageDown')

            await page.wait_for_selector(".PaymentFramestyles__Iframe-sc-1qrc16h-1")
            main_frame = page.frame_locator(".PaymentFramestyles__Iframe-sc-1qrc16h-1")

            frame_card_num = main_frame.frame_locator('#cc-number > iframe:nth-child(1)')
            card_num = frame_card_num.locator("#processout-field")
            await card_num.click()
            await card_num.fill(data_dict["credit_card_number"])

            holder_name = main_frame.locator("#cardholdername")
            await holder_name.click()
            await holder_name.fill(data_dict["first_name"])

            expiry_frame = main_frame.frame_locator('#cc-exp > iframe:nth-child(1)')
            expiry = expiry_frame.locator("#processout-field")
            await expiry.click()
            await expiry.fill(f"{data_dict['expiry_month']} / {data_dict['expiry_year']}")

            cvc_frame = main_frame.frame_locator('#cc-cvc > iframe:nth-child(1)')
            cvc = cvc_frame.locator("#processout-field")
            await cvc.click()
            await cvc.fill(data_dict["cvc_code"])
            submit = main_frame.locator("#submit-button")
            await submit.click()

            await asyncio.sleep(500)

            await context.clear_cookies()
            await context.close()
            await browser.close()
    except:
        return 0


async def check_stock(url, data):
    price = data["price"]
    content = requests.get(url, headers=headers, cookies=cookies, impersonate="chrome120")
    soup = BeautifulSoup(content.content, "html.parser")

    try:
        new_price = float(soup.find("li", class_="Pricestyles__Li-sc-1oev7i-0")["content"])
        if float(price) >= new_price:
            urls[url]["price"] = new_price
            return url
        if url in temporary_urls: return False
        await send_not_relevant_message(url, new_price)
        temporary_urls[url] = datetime.now()
        return False
    except:
        return False


@tasks.loop(minutes=1)
async def check_urls():

    if len(user_data) == 0:
        return
    tasks = [check_stock(url, price) for url, price in urls.items()]
    results = await asyncio.gather(*tasks)

    for url, result in zip(urls, results):
        if result:
            checkouts = []
            number = int(urls[url]["number"])
            task_num = int(urls[url]["tasks"])
            for _ in range(task_num):
                checkouts.append(checkout_items(url=url, count=number))

            bought = await asyncio.gather(*checkouts)
            amount = sum(bought)
            if amount > 0:
                await send_message_with_buttons(url, amount)
                urls.pop(url)
            elif url not in temporary_urls:
                temporary_urls[url] = datetime.now()
                await send_fail_message(url)


async def send_fail_message(url):
    channel = bot.get_channel(CHANNEL_ID)

    data = urls[url]
    await channel.send(content=f"Failed to buy item. Trying again. Info: \n"
                               f"Link: {url} \n"
                               f"Price: {data['price']} \n"
                               f"Amount: {data['number']} \n"
                               f"Tasks: {data['tasks']} \n\n")

async def send_not_relevant_message(url, price_now):
    channel = bot.get_channel(CHANNEL_ID)

    view = URLButtons(url, price=price_now)
    data = urls[url]
    await channel.send(content=f"Item in stock, with higher price than desired: \n"
                               f"Link: {url} \n"
                               f"Price: {price_now} \n"
                               f"Desired price: {data['price']} \n"
                               f"Amount: {data['number']} \n"
                               f"Tasks: {data['tasks']} \n\n"
                               f"Buy anyway:", view=view)

async def send_message_with_buttons(url, amount):
    channel = bot.get_channel(CHANNEL_ID)

    view = URLButtons(url)
    data = urls[url]
    await channel.send(content=f"Condition met for {url}: \n"
                               f"Price bought at:{data['price']} \n"
                               f"Amount successfully bought: {amount} \n\n"
                               f"Buy more:", view=view)


class URLButtons(discord.ui.View):
    def __init__(self, url, price=0):
        super().__init__()
        self.url = url
        if price:
            self.price = price
        else:
            self.price = urls[url]["price"]
        self.row_1_choice = None

        qty = [1, 3, 5, 10, 999]
        tasks_num = [1, 3, 5, 10, 50]

        for i in qty:
            self.add_item(URLButton(label=str(i), row=0))
        for i in tasks_num:
            self.add_item(URLButton(label=str(i), row=1))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return True

    async def update_row_choice(self, interaction, choice, row):
        if row == 0:
            self.row_1_choice = choice
        elif self.row_1_choice is not None:
            tasks = []
            for _ in range(choice):
                tasks.append(checkout_items(self.url, self.row_1_choice))
            await interaction.response.send_message(f"Buying {self.row_1_choice} [item(s)]({self.url}) in {choice} task(s)")
            self.row_1_choice = None
            await add_url_to_file(self.url, self.price, urls[self.url]["number"], urls[self.url]["tasks"])
            await check_urls()


class URLButton(discord.ui.Button):
    def __init__(self, label, row):
        super().__init__(label=label, style=discord.ButtonStyle.primary, row=row)
        self.row = row

    async def callback(self, interaction: discord.Interaction):
        choice = int(self.label)
        await self.view.update_row_choice(interaction, choice, self.row)
        await interaction.response.send_message(f"Row {self.row} choice: {choice}", ephemeral=True)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    global urls
    urls = await read_urls_from_file()
    try:
        synced = await bot.tree.sync()
        print(synced)
    except:
        traceback.print_exc()
    check_urls.start()
    await bot.loop.create_task(app.run_task('0.0.0.0', 10001))


@bot.tree.command(name="register")
@app_commands.describe(delivery_address1="Delivery Address 1")
@app_commands.describe(delivery_address2="Delivery Address 2")
@app_commands.describe(delivery_city="Delivery City")
@app_commands.describe(delivery_zipcode="Delivery Zipcode")
@app_commands.describe(phone_number="Phone Number")
@app_commands.describe(first_name="First Name")
@app_commands.describe(last_name="Last Name")
@app_commands.describe(email="Email")
@app_commands.describe(credit_card_number="Credit Card Number")
@app_commands.describe(expiry_month="Expiry Month")
@app_commands.describe(expiry_year="Expiry Year")
@app_commands.describe(cvc_code="CVC Code")
@app_commands.describe(billing_address1="Billing Address 1")
@app_commands.describe(billing_address2="Billing Address 2")
@app_commands.describe(billing_city="Billing City")
@app_commands.describe(billing_zipcode="Billing Zipcode")
@app_commands.describe(bot_password="Password")
async def register(interaction: discord.Interaction, delivery_address1: str, delivery_address2: str, delivery_city: str, delivery_zipcode:str, phone_number: str, first_name: str, last_name: str, email: str, credit_card_number: str, expiry_month: str,expiry_year: str, cvc_code: str, billing_address1: str, billing_address2: str, billing_city: str, billing_zipcode: str, bot_password: str):
    try:
        password = bot_password
        data = [delivery_address1, delivery_address2, delivery_city, delivery_zipcode, phone_number, first_name, last_name, email, credit_card_number, expiry_month, expiry_year, cvc_code, billing_address1, billing_address2, billing_city, billing_zipcode]
        data_string = "||".join(data)
        encrypted_data = await asyncio.to_thread(encrypt_data, data_string, password)
        await asyncio.to_thread(write_encrypted_data_to_file, encrypted_data)
        global user_data
        user_data = data
        await interaction.response.send_message(f"Data registered, autocheckout started. /add to add links to check", ephemeral=True)
    except:
        traceback.print_exc()


@bot.tree.command(name="log_in")
@app_commands.describe(password="Password")
async def log_in(interaction: discord.Interaction, password: str):
    decrypted_data = decrypt_data(read_encrypted_data_from_file(), password)
    if len(decrypted_data.split("||")) == 16:
        global user_data
        user_data = decrypted_data.split("||")
        await interaction.response.send_message(f"Successfully logged in. Starting link checks",
                                            ephemeral=True)
    else:
        await interaction.response.send_message(f"Wrong password, try again",
                                                ephemeral=True)


@bot.tree.command(name="add")
@app_commands.describe(url="URL")
@app_commands.describe(price="Price")
@app_commands.describe(count="Count")
@app_commands.describe(tasks="Tasks")
async def add(interaction: discord.Interaction, url: str, price: float, count: int, tasks: int):
    await add_url_to_file(url, price, count, tasks)
    await interaction.response.send_message(f"[Url]({url}) was successfully added with threshold - £{price}")


@bot.tree.command(name="remove")
@app_commands.describe(url="URL")
async def remove(interaction: discord.Interaction, url: str):
    await remove_url_from_file(url)
    await interaction.response.send_message(f"[Url]({url}) was successfully removed from the list")


@bot.tree.command(name="all")
@app_commands.describe()
async def all(interaction: discord.Interaction):
    urls_dict = await read_urls_from_file()
    message = f"{len(urls_dict)} links found: \n"
    i = 1
    for url, data in urls_dict.items():
        message += f"{i}. {url} - £{data['price']}, amount: {data['number']}, tasks: {data['tasks']} \n"
        i += 1
    await interaction.response.send_message(message)



async def main():
    await bot.start("TOKEN")

asyncio.run(main())