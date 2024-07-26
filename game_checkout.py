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

links_file = "game-links"
data_file = "game-data"

CHANNEL_ID = 1262827372437311490


cookies = {
    "GAMESession": "AR+U4h1nggY9UJgGLbGGkGFi+Dbi148uyM7b6bD91EGuBm9lhwpy+SJhuQpBJZgbYwTXXzsxwFU6rfxBUVD1caF+rfhm1ERUUTcv9fHMC1ZMhlCNI0kLNmVlQ1E990ez/ky9s40UCKgpo9mlccogKN0",
    "JSESSIONID": "0000wSUNsBxv10lcMTQeV8Rh-Y2:18oae5lgj",
    "ORA_FPC": "id=a5fd6c23-eb70-4ed3-9166-2779654a2fe7 ",
    "WC_ACTIVEPOINTER": "44%2C10151",
    "WC_GENERIC_ACTIVITYDATA": "[23902279088%3Atrue%3Afalse%3A0%3AN97NznhAtLV2unaZ9S30WuBFEkc%3D][com.ibm.commerce.context.audit.AuditContext|1708211046048-596014][com.ibm.commerce.store.facade.server.context.StoreGeoCodeContext|null%26null%26null%26null%26null%26null][com.game.gameaccount.context.GameAccountAccessTokenContext|null][com.game.gameaccount.context.GameAccountContext|null%26null%26null%26null][CTXSETNAME|Store][com.ibm.commerce.context.globalization.GlobalizationContext|44%26GBP%2644%26GBP][com.game.gameaccount.context.GameAccountPostLogonContext|null][com.ibm.commerce.catalog.businesscontext.CatalogContext|10201%26null%26false%26false%26false][com.ibm.commerce.context.base.BaseContext|10151%26-1002%26-1002%26-1][com.ibm.commerce.context.experiment.ExperimentContext|null][com.ibm.commerce.context.entitlement.EntitlementContext|10002%2610002%26null%26-2000%26null%26null%26null]",
    "WC_PERSISTENT": "TbQdUIMXh79ggUK0yWNt4jmzSjs%3D%0A%3B2024-02-17+23%3A04%3A06.05_1708211046048-596014_10151",
    "WC_SESSION_ESTABLISHED": "true",
    "WC_USERACTIVITY_-1002": "-1002%2C10151%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2CABtLmXt%2FyjnsRlXUR6%2Bwf3mHQV%2BKIhEyRqmVnOOL8v8N8QOEkDlSwxxtdrrrNfSLqXtEFamVLHeVRGSf1fdcP7d8CphjlcQdYZZUHcQyTGhg7zj%2FQjagGlvkDrSEmOqhzXW085Gi7dSSrr7XR0Z7YTI5CW58PLIvM2aoBT4rLjF%2BqEUj0PPY1c3mX4VanFaMyejb4t5TlbdO3Z7KprBxaw%3D%3D",
    "X-Origin-Cookie": "1",
    "_cq_duid": "1.1708211046.JzxFz3cjJtU4thmc",
    "_cq_suid": "1.1708211046.6w1e2j8iQjzeu0q6",
    "_ga": "GA1.3.1136405655.1708211047",
    "_ga_BZM1F1D2W5": "GS1.1.1708630767.5.0.1708630767.60.0.0",
    "_gcl_au": "1.1.893585599.1708211047",
    "_gid": "GA1.3.1434009465.1708630768",
    "_rdt_uuid": "1708211047355.917b9704-f9b5-4af9-a989-84f394e9040d",
    "ak_bmsc": "80FF04B6649A101BFDDF6E7FFB7BC523~000000000000000000000000000000~YAAQDIR7XO9Hj8SNAQAA8XZU0haRKhRWrrW1Dw5rztbyPprxsftS66P/4ekYzihOV5GOVsJgqTqxUQqJXw/INOZe6Noq9HDkJoreDYqqfJe5Sn2nCyMXZqLIodQCToFQ4ShgVwNmefkJNbCn3SuTxiOxQDOz0QIRKNAcsXJR36Ig3rnq+BB7NACX7c19TLvS9beLI7agKjlBY5DyMcUvLeicQWPJNkZ0GGeS5X6ik4Z3uOE03iFm3pO89/EExrpxOEUdV4Y4LPZGpU4DPnIVJVv1KvZLwvIcddOIWXHH9cdIVdFNa1CHilk2iAa0BxAS5Obh4kpiEdDXKT9QJS3G+a+AfEA/if0KGHUQRUt1EeZlZ7klIlnn6g38H5+1z03Zhn/zkhgyCL0oO2S6m1J1Hh1x/O3e734+FaONzvtQVMJyS84CdmbhjWOFer9ZKTmmd4ZMC+FrPpvAW7AwBjEZgScDFcvL03YrVwbMfmNvjydmjv68OkihxBTgfHKoYA==",
    "bm_sv": "4E0E2201DA46C26D6BFCA0AAE7A430A1~YAAQDIR7XERHj8SNAQAANXJU0hbjPlQBD66gANmTWWbjvj537y9PybsPeGsPWwo8Cv/eOKVTuJ05RaZ2ihy7YclmKk84OK8Nn2rXVTjj9VpryrAaDKbsC5znJTcGrvwuK8r27H+0Cu2G1w2CUiccwOrWk7XECeX0T58sfVkhO4ZeHByuBo41Kj6jfhz5EpI519I/BMjRmKmPP5kCBtf5wPEobwGUKgEzCQ7riqGspgugqDmep4RbszClnKkcUZ/+~1",
    "complianceCookie": "true",
    "gdprPurposesCookie": "[1,2,3,4,5]",
    "hashedemail": "Guest",
    "mmapi.e.lightbox1707910661244persistData": "%221%2C1%2C1708211049%22",
    "mmapi.p.bid": "%22prodlhrcgeu06%22	",
    "mmapi.p.ids": "%7B%221%22%3A%22Guest%22%7D	",
    "mmapi.p.pd": "%227qHpjsuhLerlwyPp8Zd7iAdI_4rdLY5lsHrYlcToTjw%3D%7CGgAAAApDH4sIAAAAAAAEAGNhSPafsLBA4p07q3tpanEJc05GEaMQA6MTg2NfwkUWhleXrH7fNb7j0ajDuJ_H4I4HAxD8hwIGNpfMotTkEsYCCRaQOBjAJEE0I4NDOyODlIy62PYCCbA2oNJSif__pRgYGEGqGZmfMTNs1mGFaGVgdAUA74BZdo8AAAA%3D%22",
    "mmapi.p.srv": "%22prodlhrcgeu06%22"
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cookie': 'hashedemail=Guest; WC_PERSISTENT=TbQdUIMXh79ggUK0yWNt4jmzSjs%3D%0A%3B2024-02-17+23%3A04%3A06.05_1708211046048-596014_10151; WC_SESSION_ESTABLISHED=true; WC_ACTIVEPOINTER=44%2C10151; WC_USERACTIVITY_-1002=-1002%2C10151%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2CABtLmXt%2FyjnsRlXUR6%2Bwf3mHQV%2BKIhEyRqmVnOOL8v8N8QOEkDlSwxxtdrrrNfSLqXtEFamVLHeVRGSf1fdcP7d8CphjlcQdYZZUHcQyTGhg7zj%2FQjagGlvkDrSEmOqhzXW085Gi7dSSrr7XR0Z7YTI5CW58PLIvM2aoBT4rLjF%2BqEUj0PPY1c3mX4VanFaMyejb4t5TlbdO3Z7KprBxaw%3D%3D; WC_GENERIC_ACTIVITYDATA=[23902279088%3Atrue%3Afalse%3A0%3AN97NznhAtLV2unaZ9S30WuBFEkc%3D][com.ibm.commerce.context.audit.AuditContext|1708211046048-596014][com.ibm.commerce.store.facade.server.context.StoreGeoCodeContext|null%26null%26null%26null%26null%26null][com.game.gameaccount.context.GameAccountAccessTokenContext|null][com.game.gameaccount.context.GameAccountContext|null%26null%26null%26null][CTXSETNAME|Store][com.ibm.commerce.context.globalization.GlobalizationContext|44%26GBP%2644%26GBP][com.game.gameaccount.context.GameAccountPostLogonContext|null][com.ibm.commerce.catalog.businesscontext.CatalogContext|10201%26null%26false%26false%26false][com.ibm.commerce.context.base.BaseContext|10151%26-1002%26-1002%26-1][com.ibm.commerce.context.experiment.ExperimentContext|null][com.ibm.commerce.context.entitlement.EntitlementContext|10002%2610002%26null%26-2000%26null%26null%26null]; _cq_duid=1.1708211046.JzxFz3cjJtU4thmc; _cq_suid=1.1708211046.6w1e2j8iQjzeu0q6; _gcl_au=1.1.893585599.1708211047; mmapi.p.ids=%7B%221%22%3A%22Guest%22%7D; ORA_FPC=id=a5fd6c23-eb70-4ed3-9166-2779654a2fe7; mmapi.e.lightbox1707910661244persistData=%221%2C1%2C1708211049%22; complianceCookie=true; gdprPurposesCookie=[1,2,3,4,5]; GAMESession=AR+U4h1nggY9UJgGLbGGkGFi+Dbi148uyM7b6bD91EGuBm9lhwpy+SJhuQpBJZgbYwTXXzsxwFU6rfxBUVD1caF+rfhm1ERUUTcv9fHMC1ZMhlCNI0kLNmVlQ1E990ez/ky9s40UCKgpo9mlccogKN0; X-Origin-Cookie=1; bm_sv=4E0E2201DA46C26D6BFCA0AAE7A430A1~YAAQDIR7XERHj8SNAQAANXJU0hbjPlQBD66gANmTWWbjvj537y9PybsPeGsPWwo8Cv/eOKVTuJ05RaZ2ihy7YclmKk84OK8Nn2rXVTjj9VpryrAaDKbsC5znJTcGrvwuK8r27H+0Cu2G1w2CUiccwOrWk7XECeX0T58sfVkhO4ZeHByuBo41Kj6jfhz5EpI519I/BMjRmKmPP5kCBtf5wPEobwGUKgEzCQ7riqGspgugqDmep4RbszClnKkcUZ/+~1; JSESSIONID=0000wSUNsBxv10lcMTQeV8Rh-Y2:18oae5lgj; hashedemail=Guest; _ga_BZM1F1D2W5=GS1.1.1708630767.5.0.1708630767.60.0.0; _rdt_uuid=1708211047355.917b9704-f9b5-4af9-a989-84f394e9040d; _ga=GA1.3.1136405655.1708211047; _gid=GA1.3.1434009465.1708630768; ak_bmsc=80FF04B6649A101BFDDF6E7FFB7BC523~000000000000000000000000000000~YAAQDIR7XO9Hj8SNAQAA8XZU0haRKhRWrrW1Dw5rztbyPprxsftS66P/4ekYzihOV5GOVsJgqTqxUQqJXw/INOZe6Noq9HDkJoreDYqqfJe5Sn2nCyMXZqLIodQCToFQ4ShgVwNmefkJNbCn3SuTxiOxQDOz0QIRKNAcsXJR36Ig3rnq+BB7NACX7c19TLvS9beLI7agKjlBY5DyMcUvLeicQWPJNkZ0GGeS5X6ik4Z3uOE03iFm3pO89/EExrpxOEUdV4Y4LPZGpU4DPnIVJVv1KvZLwvIcddOIWXHH9cdIVdFNa1CHilk2iAa0BxAS5Obh4kpiEdDXKT9QJS3G+a+AfEA/if0KGHUQRUt1EeZlZ7klIlnn6g38H5+1z03Zhn/zkhgyCL0oO2S6m1J1Hh1x/O3e734+FaONzvtQVMJyS84CdmbhjWOFer9ZKTmmd4ZMC+FrPpvAW7AwBjEZgScDFcvL03YrVwbMfmNvjydmjv68OkihxBTgfHKoYA==; mmapi.p.pd=%227qHpjsuhLerlwyPp8Zd7iAdI_4rdLY5lsHrYlcToTjw%3D%7CGgAAAApDH4sIAAAAAAAEAGNhSPafsLBA4p07q3tpanEJc05GEaMQA6MTg2NfwkUWhleXrH7fNb7j0ajDuJ_H4I4HAxD8hwIGNpfMotTkEsYCCRaQOBjAJEE0I4NDOyODlIy62PYCCbA2oNJSif__pRgYGEGqGZmfMTNs1mGFaGVgdAUA74BZdo8AAAA%3D%22; mmapi.p.bid=%22prodlhrcgeu06%22; mmapi.p.srv=%22prodlhrcgeu06%22',
    'Referer': 'https://www.game.co.uk/',
    'Sec-Ch-Ua': '"Chromium";v="120", "Not(A:Brand";v="24", "Google Chrome";v="120"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': '	Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.234 Safari/537.36'
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


async def checkout_items(url, buy_count):
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


    async def buy_quantity(number, page):
        await page.wait_for_selector(".updateQuantity")
        new_url = await page.locator(".updateQuantity").get_attribute("data-url") + f"&quantity_1={number}"
        await page.goto(new_url)
        await page.wait_for_selector(".pageTitle")
        if await page.locator(".errorSummary").is_visible():
            await buy_quantity(number - 1, page)
        else:
            return buy_count


    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                proxy={
                    'server': 'http://147.78.69.129:30755',
                    'username': 'PRIM_H9MKHSODTT',
                    'password': '1ALYDO7Y7UTD9Q'
                },
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage"
                ])

            context = await browser.new_context(viewport={"width": 1920, "height": 1080},
                                                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.77 Safari/537.36")
            page = await context.new_page()
            await page.set_extra_http_headers({"sec-ch-ua": '"Chromium";v="125", "Not.A/Brand";v="24"'})

            await page.goto(url)

            await page.wait_for_selector(".addToBasket > a:nth-child(1)")
            await page.locator(".addToBasket > a:nth-child(1)").click()

            if buy_count != 1:
                buy_count = await buy_quantity(buy_count, page)

            await page.goto("https://checkout.game.co.uk/contact")

            await page.wait_for_selector(".mat-select-trigger")
            await page.locator(".mat-select-trigger").click()

            await page.wait_for_selector("#mat-option-0")
            await page.locator("#mat-option-0").click()

            await page.wait_for_selector("#mat-input-0")
            await page.locator("#mat-input-0").fill(data_dict["first_name"])

            await page.locator("#mat-input-1").fill(data_dict["last_name"])
            await page.locator("#mat-input-2").fill(data_dict["email"])
            await page.locator("#mat-input-3").fill(data_dict["phone_number"])

            await page.wait_for_selector(".mat-raised-button")
            await page.locator(".mat-raised-button").click()

            await page.wait_for_selector("a.ng-star-inserted")
            await page.locator("a.ng-star-inserted").click()

            await page.wait_for_selector(".mat-select-placeholder")
            await page.locator(".mat-select-placeholder").click()
            await page.locator(".ng-trigger-transformPanel").locator("mat-option").nth(0).click()

            form = page.locator("game-address-form")
            await form.locator("input").nth(0).fill(data_dict["delivery_address1"])
            await form.locator("input").nth(1).fill(data_dict["delivery_address2"])
            await form.locator("input").nth(3).fill(data_dict["delivery_city"])
            await form.locator("input").nth(5).fill(data_dict["delivery_zipcode"])

            await page.wait_for_selector("button.mat-raised-button:nth-child(2)")
            await page.locator("button.mat-raised-button:nth-child(2)").click()

            await page.wait_for_selector("#mat-radio-8 > label:nth-child(1)")
            await page.locator("#mat-radio-8 > label:nth-child(1)").click()

            frame = page.frame_locator("#card-number-container > iframe:nth-child(1)")
            card_num = frame.locator("#number")
            await card_num.fill(data_dict["credit_card_number"])

            await page.locator('[placeholder="Name on Card"]').fill(data_dict["first_name"])
            await page.locator('[placeholder="Expiry Date (MM/YY)"]').fill(f"{data_dict["expiry_month"]}/{data_dict["expiry_year"]}")
            await page.locator(".mat-input-element").last.fill(data_dict["cvc_code"])

            await page.locator("game-billing-same-as-delivery").nth(1).locator("mat-checkbox").click()

            await page.locator("a.ng-star-inserted").click()

            form = page.locator("game-address-form")
            await page.locator(".mat-select-placeholder").click()
            await page.locator(".ng-trigger-transformPanel").locator("mat-option").nth(0).click()

            await form.locator("input").nth(0).fill(data_dict["billing_address1"])
            await form.locator("input").nth(1).fill(data_dict["billing_address2"])
            await form.locator("input").nth(3).fill(data_dict["billing_city"])
            await form.locator("input").nth(5).fill(data_dict["billing_zipcode"])

            await page.locator(".mat-flat-button").click()

            try:
                await page.locator("#mat-checkbox-1 > label:nth-child(1)").click(timeout=1500)
            except:
                pass

            await page.locator("button.game-full-width").click()

            await asyncio.sleep(10)  # Replace time.sleep with asyncio.sleep
            return buy_count
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
                checkouts.append(checkout_items(url=url, buy_count=number))

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
    await bot.loop.create_task(app.run_task('0.0.0.0', 10002))


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
