

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

links_file = "john-links"
data_file = "john-data"

CHANNEL_ID = 1246341750143057950


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
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Connection': 'keep-alive'
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


async def checkout_items(url, number_count):
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

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage"
        ])
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1580}
        )
        page = await context.new_page()

        try:
            await page.goto(url)

            await page.wait_for_selector('button.c-button-2pep9:nth-child(1)', timeout=3000)
            cookie_button = page.locator('button.c-button-2pep9:nth-child(1)')
            await cookie_button.click()
            await asyncio.sleep(1)

            await page.wait_for_selector('#basket\\:add\\:button', timeout=1000)
            basket_button = page.locator('#basket\\:add\\:button')
            await basket_button.click()

            await page.wait_for_selector('#basket\\:confirmation\\:gtb', timeout=5000)

            if number_count != 1:
                await page.wait_for_selector(".ItemRowNew_hideOnMobile__1sUV5")
                item_number = page.locator(".ItemRowNew_hideOnMobile__1sUV5").locator("input").nth(0)
                await item_number.click()
                await asyncio.sleep(0.5)
                await item_number.type(str(number_count))
                await asyncio.sleep(5)

            await page.wait_for_selector('.button_c-button--primary__weVR3')
            confirm = page.locator('.button_c-button--primary__weVR3')
            await confirm.click()
            await asyncio.sleep(0.5)

            try:
                await page.wait_for_selector('//*[@id="main"]/section/div/div/div[2]/div/label', timeout=5000)
            except:
                try:
                    await confirm.click()
                except:
                    pass

            await page.wait_for_selector('//*[@id="main"]/section/div/div/div[2]/div/label', timeout=5000)
            guest = page.locator('//*[@id="main"]/section/div/div/div[2]/div/label')
            await guest.click()

            await page.wait_for_selector('//*[@id="email"]')
            email = page.locator('//*[@id="email"]')
            await email.click()
            await email.fill(data_dict["email"])

            await page.wait_for_selector('//*[@id="loginForm"]')
            guestsignin = page.locator('//*[@id="loginForm"]')
            await guestsignin.click()

            try:
                await page.wait_for_selector('//*[@id="delivery"]', timeout=2000)
                freedelivery = page.locator('//*[@id="delivery"]')
                await freedelivery.click()
            except:
                try:
                    await page.wait_for_selector('//*[@id="delivery"]', timeout=2000)
                    freedelivery = page.locator('//*[@id="delivery"]')
                    await freedelivery.click()
                except:
                    pass

            await page.wait_for_selector('//*[@id="title"]')
            title1 = page.locator('//*[@id="title"]')
            await title1.click()
            await title1.type('MR')

            await page.wait_for_selector('//*[@id="firstName"]')
            first_name1 = page.locator('//*[@id="firstName"]')
            await first_name1.click()
            await first_name1.fill(data_dict["first_name"])

            await page.wait_for_selector('//*[@id="lastName"]')
            last_name1 = page.locator('//*[@id="lastName"]')
            await last_name1.click()
            await last_name1.fill(data_dict["last_name"])

            await page.wait_for_selector('//*[@id="phoneNumber"]')
            phonenum1 = page.locator('//*[@id="phoneNumber"]')
            await phonenum1.click()
            await phonenum1.fill(data_dict["phone_number"])

            await page.wait_for_selector('//*[@id="main"]/section/div[1]/div/div[2]/div[2]/div[2]/form/div/div[2]/button/span')
            addmanual = page.locator('//*[@id="main"]/section/div[1]/div/div[2]/div[2]/div[2]/form/div/div[2]/button/span')
            await addmanual.click()

            await page.wait_for_selector('//*[@id="addressLine1"]')
            addressline11 = page.locator('//*[@id="addressLine1"]')
            await addressline11.click()
            await addressline11.fill(data_dict["delivery_address1"])

            await page.wait_for_selector('//*[@id="addressLine2"]')
            addressline12 = page.locator('//*[@id="addressLine2"]')
            await addressline12.click()
            await addressline12.fill(data_dict["delivery_address2"])

            await page.wait_for_selector('//*[@id="townOrCity"]')
            town1 = page.locator('//*[@id="townOrCity"]')
            await town1.click()
            await town1.fill(data_dict["delivery_city"])

            await page.wait_for_selector('//*[@id="postcode"]')
            postcode = page.locator('//*[@id="postcode"]')
            await postcode.click()
            await postcode.fill(data_dict["delivery_zipcode"])

            await page.wait_for_selector('//*[@id="deliveryAddressForm"]')
            use_this_address1 = page.locator('//*[@id="deliveryAddressForm"]')
            await use_this_address1.click()

            try:
                await page.wait_for_selector('//*[@id="main"]/section/div[1]/div/div[2]/div[4]/form/div[1]/div[1]/div/label/div/h4/span[1]', timeout=5000)
                standard_del = page.locator('//*[@id="main"]/section/div[1]/div/div[2]/div[4]/form/div[1]/div[1]/div/label/div/h4/span[1]')
                await standard_del.click()
            except:
                pass

            try:
                await page.wait_for_selector('button.button_c-button__840ed\\:nth-child(1)', timeout=5000)
                continue_to_payment1 = page.locator('button.button_c-button__840ed\\:nth-child(1)')
                await continue_to_payment1.click()
            except:
                traceback.print_exc()

            try:
                await page.wait_for_selector("//button[contains(@class,'primary__1db81')]", timeout=5000)
                continue_to_payment2 = page.locator("//button[contains(@class,'primary__1db81')]")
                await continue_to_payment2.click()
            except:
                traceback.print_exc()

            await page.keyboard.press('PageDown')

            await page.wait_for_selector('//*[@id="cardNumber"]')
            card_number2 = page.locator('//*[@id="cardNumber"]')
            await card_number2.click()
            await card_number2.fill(data_dict["credit_card_number"])

            await page.wait_for_selector('//*[@id="cardholderName"]')
            name_on_card = page.locator('//*[@id="cardholderName"]')
            await name_on_card.click()
            await name_on_card.fill(data_dict["first_name"])

            await page.wait_for_selector('//*[@id="expiryDate"]')
            expiry_date = page.locator('//*[@id="expiryDate"]')
            await expiry_date.click()
            await expiry_date.fill(f'{data_dict["expiry_month"]}/{data_dict["expiry_year"]}')

            await page.wait_for_selector('//*[@id="securityCode"]')
            security_code = page.locator('//*[@id="securityCode"]')
            await security_code.click()
            await security_code.fill(data_dict["cvc_code"])

            await page.wait_for_selector('.option_c-option__label--checkbox__0df80')
            select_billing = page.locator('.option_c-option__label--checkbox__0df80')
            await select_billing.click()

            await page.keyboard.press('PageDown')
            await asyncio.sleep(1)

            await page.wait_for_selector('//*[@id="title"]', timeout=5000)
            title2 = page.locator('//*[@id="title"]')
            await title2.click()
            await asyncio.sleep(0.2)
            await title2.fill('MR')

            await page.wait_for_selector('//*[@id="firstName"]')
            first_name2 = page.locator('//*[@id="firstName"]')
            await first_name2.click()
            await first_name2.fill(data_dict["first_name"])

            await page.wait_for_selector('//*[@id="lastName"]')
            last_name2 = page.locator('//*[@id="lastName"]')
            await last_name2.click()
            await last_name2.fill(data_dict["last_name"])

            await page.wait_for_selector('//*[@id="phoneNumber"]')
            phonenum2 = page.locator('//*[@id="phoneNumber"]')
            await phonenum2.click()
            await phonenum2.fill(data_dict["phone_number"])

            await page.wait_for_selector('//*[@id="content-creditCard"]/div/div[1]/div/div[2]/div[3]/div[2]/form/div/div[2]/button/span')
            addmanual2 = page.locator('//*[@id="content-creditCard"]/div/div[1]/div/div[2]/div[3]/div[2]/form/div/div[2]/button/span')
            await addmanual2.click()

            await page.wait_for_selector('//*[@id="addressLine1"]')
            addressline21 = page.locator('//*[@id="addressLine1"]')
            await addressline21.click()
            await addressline21.fill(data_dict["billing_address1"])

            await page.wait_for_selector('//*[@id="addressLine2"]')
            addressline22 = page.locator('//*[@id="addressLine2"]')
            await addressline22.click()
            await addressline22.fill(data_dict["billing_address2"])

            await page.wait_for_selector('//*[@id="townOrCity"]')
            town2 = page.locator('//*[@id="townOrCity"]')
            await town2.click()
            await town2.fill(data_dict["billing_city"])

            await page.wait_for_selector('//*[@id="postcode"]')
            postcode2 = page.locator('//*[@id="postcode"]')
            await postcode2.click()
            await postcode2.fill(data_dict["billing_zipcode"])

            pay = page.locator(".button_c-button--primary__1db81")
            await pay.click()
            await asyncio.sleep(20)
            return number_count

        except Exception as e:
            traceback.print_exc()
            return 0


        finally:
            await context.clear_cookies()
            await context.close()
            await browser.close()



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
                checkouts.append(checkout_items(url=url, number_count=number))

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
    await bot.loop.create_task(app.run_task('0.0.0.0', 10003))


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