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

links_file = "currys-links"
data_file = "currys-data"

CHANNEL_ID = 1248593676293246976



cookies = {
    '__cf_bm':	"5cT3bEl.ytRRD2Oqmv9AaNg4Si7.OgzA.rO4pp.G9iE-1710338761-1.0.1.1-N4gDlUUoBnrhagTeebw1xqczMu5ZCUAFt1Xkvso211SA1P8B0rto9IxoLuLjpRJdG1wSMVdL0vXDy81zvnqWdw",
    '__cq_dnt':	"0",
    '_cfuvid':	"ef769qDYgYan3RQ35Yh6gEOqoZk8cJxYu4Dr4vJk9Ws-1710338761968-0.0.1.1-604800000",
    '_cs_mk_aa':	"0.07594036318843012_1710338812081",
    '_mibhv':	"anon-1710338813233-56683855_8082",
    'cf_clearance':	"eCPFqKhba0iqw_lzs3llYPNx.zZPUjVFaH.Ifa9jVCg-1710338763-1.0.1.1-dHrXarEoPHv95lJ0X0z3RSTTMBgqYEVnxx8hafkDP6v4GND0AQTDwBIc1XPkdNI6.LL5fcIwEn5SBfmmMl3unA",
    'cqcid':	"abRsoDOFYas5iqUCWknTpeHOHA",
    'cquid':	"||",
    'dw_dnt':	"0",
    'dwac_2657edce74737ed44718c8ec2e':	"5bOjgi2n6KpsmJ6jhAzN7gtN9S4BTH5LK2U=|dw-only|||GBP|false|Europe/London|true",
    'dwanonymous_c1575c7fdffeee6c1c87c9bab9ccac08':	"abRsoDOFYas5iqUCWknTpeHOHA",
    'dwOptanonConsentCookie':	"false",
    'dwsid':	"hl_Mf99HDdLBLDnzC0X-M2ihmtPzrJszhtEEbBGA1FUBv3KPevIzCVJvqITJYirVH-1Ljk_a2lf6SePYDVAoGg==",
    'gcpData':	"{}",
    'gpv_login':	"logged_out",
    'gpv_pg':	"Keyboards",
    'gpv_template':	"rendering/category/PLP",
    'gpv_url':	"https://www.currys.co.uk/gaming/gaming-accessories/keyboards",
    'OptanonAlertBoxClosed':	"2024-03-13T14:06:51.970Z",
    'OptanonConsent':	"isGpcEnabled=0&datestamp=Wed+Mar+13+2024+16:17:33+GMT+0200+(Eastern+European+Standard+Time)&version=202402.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=0e535f7d-8b94-4502-8c35-e9ec5d72b4c4&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001:1,C0008:1,C0002:1,C0003:1,C0004:1&geolocation=;&AwaitingReconsent=false",
    'sid':	"5bOjgi2n6KpsmJ6jhAzN7gtN9S4BTH5LK2U",
    'smc_group_events':	"A",
    'smc_group_test_value':	"A",
    'smc_not':	"default",
    'smc_refresh':	"32305",
    'smc_sesn':	"1",
    'smc_session_id':	"SZN2cU0lq2NrrHhiUIAhZbZQ7XD5xGR7",
    'smc_spv':	"1",
    'smc_tag':	"eyJpZCI6MTkyNCwibmFtZSI6ImN1cnJ5cy5jby51ayJ9",
    'smc_tpv':	"1",
    'smc_uid':	"1710338813572710",
    'smct_dyn_BasketCount':	"0",
    'smct_session':	'{"s":1710338814621,"l":1710340438446,"lt":1710340438446,"t":904,"p":101}'
}

headers = {
    'User-Agent': ' Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.234 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Connection': 'keep-alive',
    "Cookie": "sid=5bOjgi2n6KpsmJ6jhAzN7gtN9S4BTH5LK2U; dwanonymous_c1575c7fdffeee6c1c87c9bab9ccac08=abRsoDOFYas5iqUCWknTpeHOHA; __cq_dnt=0; dw_dnt=0; dwsid=hl_Mf99HDdLBLDnzC0X-M2ihmtPzrJszhtEEbBGA1FUBv3KPevIzCVJvqITJYirVH-1Ljk_a2lf6SePYDVAoGg==; __cf_bm=5H1BCFOa5yM04F7easaIEqFmCnFAf8HcgQ5LlkAAznI-1710340446-1.0.1.1-zdHyZQ8C4VesAi0zNK65FcskWjmxyTwM4NlswSzwFT60bQajS_gS0lMEHWqpZAT87yCYBgFe2dgrps9RneZ2xw; _cfuvid=ef769qDYgYan3RQ35Yh6gEOqoZk8cJxYu4Dr4vJk9Ws-1710338761968-0.0.1.1-604800000; gpv_pg=Keyboards; gpv_template=rendering/category/PLP; gpv_url=https://www.currys.co.uk/gaming/gaming-accessories/keyboards; gpv_login=logged_out; cf_clearance=eCPFqKhba0iqw_lzs3llYPNx.zZPUjVFaH.Ifa9jVCg-1710338763-1.0.1.1-dHrXarEoPHv95lJ0X0z3RSTTMBgqYEVnxx8hafkDP6v4GND0AQTDwBIc1XPkdNI6.LL5fcIwEn5SBfmmMl3unA; OptanonConsent=isGpcEnabled=0&datestamp=Wed+Mar+13+2024+16%3A17%3A33+GMT%2B0200+(Eastern+European+Standard+Time)&version=202402.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=0e535f7d-8b94-4502-8c35-e9ec5d72b4c4&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0008%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&geolocation=%3B&AwaitingReconsent=false; dwOptanonConsentCookie=false; OptanonAlertBoxClosed=2024-03-13T14:06:51.970Z; gcpData=%7B%7D; _mibhv=anon-1710338813233-56683855_8082; smc_uid=1710338813572710; smc_tag=eyJpZCI6MTkyNCwibmFtZSI6ImN1cnJ5cy5jby51ayJ9; smc_session_id=SZN2cU0lq2NrrHhiUIAhZbZQ7XD5xGR7; smc_group_events=A; smc_group_test_value=A; smc_refresh=32305; smct_session=%7B%22s%22%3A1710338814621%2C%22l%22%3A1710341626434%2C%22lt%22%3A1710340853287%2C%22t%22%3A1043%2C%22p%22%3A119%7D; smct_dyn_BasketCount=0; smc_tpv=1; smc_spv=1; smc_sesn=1; smc_not=default; dwac_2657edce74737ed44718c8ec2e=5bOjgi2n6KpsmJ6jhAzN7gtN9S4BTH5LK2U%3D|dw-only|||GBP|false|Europe%2FLondon|true; cqcid=abRsoDOFYas5iqUCWknTpeHOHA; cquid=||; _cs_mk_aa=0.34880860349061416_1710340747553"
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
        await page.wait_for_selector(".select2-selection")
        await page.locator(".select2-selection").click()
        selectors = page.locator(".select2-results__options")
        items = selectors.locator("li")
        if await items.count() > number:
            item = items.nth(number - 1)
            return_count = number
        else:
            item = items.last
            return_count = await items.count()
        await item.click()
        return return_count

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage"
            ])
            context = await browser.new_context(viewport={"width": 1920, "height": 1080})
            page = await context.new_page()

            await page.goto(
                url,
                wait_until="domcontentloaded")

            await page.wait_for_selector("#onetrust-accept-btn-handler")
            await page.locator("#onetrust-accept-btn-handler").click()

            await page.wait_for_selector(
                '.addToCartActionButton > div:nth-child(1) > div:nth-child(1) > button:nth-child(1)')
            await asyncio.sleep(0.5)
            buy_btn = page.locator('.addToCartActionButton > div:nth-child(1) > div:nth-child(1) > button:nth-child(1)')
            await buy_btn.click()
            await asyncio.sleep(0.5)

            await page.goto("https://www.currys.co.uk/cart", wait_until="domcontentloaded")

            count = await buy_quantity(page, count)

            await page.wait_for_selector('a.d-sm-none')
            continue_checkout = page.locator('a.d-sm-none')
            await continue_checkout.click()

            await page.wait_for_selector('#login-iframe')
            frame = page.frame_locator('#login-iframe')
            guest_checkout = frame.locator('#guest-id')
            await guest_checkout.click()

            guest_email = frame.locator('#j_id0\\:j_id10\\:j_id11\\:checkout-newform\\:j_id35\\:1\\:guest-email-field-id')
            await guest_email.wait_for()
            await guest_email.click()
            await guest_email.fill(data_dict["email"])

            continue_checkout = frame.locator('#guest-btn-accessid > div:nth-child(1) > a:nth-child(1)')
            await continue_checkout.click()

            await page.wait_for_selector('#stockSearch')
            postcode = page.locator('#stockSearch')
            await postcode.click()
            await postcode.type(data_dict["delivery_zipcode"], delay=0.1)

            await page.wait_for_selector('.cart-submit-user-location')
            await asyncio.sleep(1)
            submit_location = page.locator('.cart-submit-user-location')
            await submit_location.click()

            await page.wait_for_selector('.delivery-options-product-name')
            try:
                choose_delivery = page.locator('#small_box_home_delivery_standard_delivery')
                await choose_delivery.click(timeout=3000)
            except:
                traceback.print_exc()

            await page.wait_for_selector('.submit-fulfillment')
            submit_delivery = page.locator('.submit-fulfillment')
            await submit_delivery.click()

            await page.wait_for_selector(
                'div.checkout_step_options:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > form:nth-child(1) > div:nth-child(3) > fieldset:nth-child(2) > div:nth-child(5) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > span:nth-child(2) > span:nth-child(1) > span:nth-child(1)')
            select_title = page.locator(
                'div.checkout_step_options:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > form:nth-child(1) > div:nth-child(3) > fieldset:nth-child(2) > div:nth-child(5) > div:nth-child(1) > div:nth-child(1) > span:nth-child(2) > span:nth-child(1) > span:nth-child(1)')
            await select_title.click()

            await page.wait_for_selector('.select2-results')
            mr_title = page.locator('.select2-results').locator('li').nth(1)
            await mr_title.click()

            await page.wait_for_selector('#shippingFirstNamedefault')
            first_name = page.locator('#shippingFirstNamedefault').nth(0)
            await first_name.click()
            await first_name.fill(data_dict["first_name"])

            last_name = page.locator('#shippingLastNamedefault').nth(0)
            await last_name.click()
            await last_name.fill(data_dict["last_name"])

            shippingPhone = page.locator('#shippingPhoneNumberdefault').nth(0)
            await shippingPhone.click()
            await shippingPhone.fill(data_dict["phone_number"])

            shippingZip = page.locator('#shippingZipCodedefault').nth(0)
            await shippingZip.click()
            await shippingZip.fill(data_dict["delivery_zipcode"])

            shippingAddress = page.locator('#shippingAddressOnedefault').nth(0)
            await shippingAddress.click()
            await shippingAddress.fill(data_dict["delivery_address1"])

            shippingAddress2 = page.locator('#shippingAddressTwodefault').nth(0)
            await shippingAddress2.click()
            await shippingAddress2.fill(data_dict["delivery_address2"])

            shippingCity = page.locator('#shippingAddressCitydefault').nth(0)
            await shippingCity.click()
            await shippingCity.fill(data_dict["delivery_city"])

            billing_details = page.locator('.custom-control-label ').nth(0)
            await billing_details.click()

            await asyncio.sleep(0.2)

            await page.wait_for_selector(
                '#dwfrm_billing_address > fieldset:nth-child(1) > fieldset:nth-child(1) > div:nth-child(4) > div:nth-child(1) > div:nth-child(1) > span:nth-child(2) > span:nth-child(1) > span:nth-child(1)')
            select_title = page.locator(
                '#dwfrm_billing_address > fieldset:nth-child(1) > fieldset:nth-child(1) > div:nth-child(4) > div:nth-child(1) > div:nth-child(1) > span:nth-child(2) > span:nth-child(1) > span:nth-child(1)')
            await select_title.click()

            await page.wait_for_selector('.select2-results')
            mr_title = page.locator('.select2-results').locator("li").nth(1)
            await mr_title.click()

            first_name = page.locator('#billingFirstName').nth(1)
            await first_name.click()
            await first_name.fill(data_dict["first_name"])

            last_name = page.locator('#billingLastName').nth(1)
            await last_name.click()
            await last_name.fill(data_dict["last_name"])

            billingPhone = page.locator('#billingPhoneNumber').nth(1)
            await billingPhone.click()
            await billingPhone.type(data_dict["phone_number"])

            billingZip = page.locator('#billingZipCode').nth(1)
            await billingZip.click()
            await billingZip.fill(data_dict["billing_zipcode"])

            billingAddress = page.locator('#billingAddressOne').nth(1)
            await billingAddress.click()
            await billingAddress.fill(data_dict["billing_address1"])

            billingAddress2 = page.locator('#billingAddressTwo').nth(1)
            await billingAddress2.click()
            await billingAddress2.fill(data_dict["billing_address2"])

            billingCity = page.locator('#billingAddressCity').nth(1)
            await billingCity.click()
            await billingCity.fill(data_dict["billing_city"])

            switch1 = page.locator('.custom-toggle-label')
            await switch1.click()

            submit_shipping = page.locator('.submit-shipping')
            await submit_shipping.click()

            await page.wait_for_selector("#payment-method-worldpay")
            payment_method = page.locator('#payment-method-worldpay')
            await payment_method.click()

            await page.wait_for_selector("button.submit-payment:nth-child(2)")
            submit_payment_method = page.locator('button.submit-payment:nth-child(2)')
            await submit_payment_method.click()

            await page.wait_for_selector("#wp-cl-custom-html-iframe")
            frame = page.frame_locator("#wp-cl-custom-html-iframe")
            card_num = frame.locator('#cardNumber')
            await card_num.click()
            await card_num.fill(data_dict["credit_card_number"])

            expiryMonth = frame.locator('#expiryMonth')
            await expiryMonth.click()
            await expiryMonth.fill(data_dict["expiry_month"])

            expiryYear = frame.locator('#expiryYear')
            await expiryYear.click()
            await expiryYear.fill(data_dict["expiry_year"])

            securityCode = frame.locator('#securityCode')
            await securityCode.click()
            await securityCode.fill(data_dict["cvc_code"])

            submitButton = frame.locator('#submitButton')
            await submitButton.click()

            await asyncio.sleep(10)
            return count
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
    await bot.loop.create_task(app.run_task('0.0.0.0', 10004))


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