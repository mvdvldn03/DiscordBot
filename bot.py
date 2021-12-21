import os
from discord.ext import commands
from dotenv import load_dotenv
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import random
import numpy as np

options = Options()
options.add_argument("--headless")
options.add_argument("--window-size=1920x1080")
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36")
driver = webdriver.Chrome(options=options, executable_path='./chromedriver 2')

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='#')
bw_list = []

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name="marta", help="Gives marta times | ![] [station1] [station2] (date) (time)")
async def marta(ctx, *args):
    station1 = args[0]
    station2 = args[1]
    url = f"https://www.google.com/search?q={station1}+marta+station+to+{station2}+marta+station+transit"
    if len(args) == 2:
        driver.get(url)
    if len(args) == 3:
        url += f"+depart+at+{args[2]}"
        driver.get(url)
    if(len(args) == 4):
        url += f"+depart+at+{args[2]}+{args[3]}"
        driver.get(url)
    departure = driver.find_element_by_xpath("//div[@class='tdu-total-time']").text[:7]
    arrival = driver.find_element_by_xpath("//div[@class='tdu-total-time']").text[10:]
    total_time = driver.find_element_by_xpath("//div[@class='tdu-time-delta']").text
    await ctx.send(f"The next train from the given date and time will leave at {departure} and arrive at {arrival}. It will take {total_time}.")

@bot.command(name='wa', help="Gives Woodward info - lunch, events, schedule | ![] [] (date)")
async def wa(ctx, *args):
    print(args)
    if args[0] == "lunch":
        if len(args) == 1:
            driver.get("https://woodward.nutrislice.com/menu/upper-school/lunch/")
            driver.find_element_by_xpath("//button[@class='primary']").click()
            driver.save_screenshot("check.png")
            sleep(2)
            food_list = driver.find_elements_by_xpath("//span[@class='food-name']")
            print(food_list)
            response = "Today's lunch includes"
            for i in range(len(food_list)):
                food_item = food_list[i].text.strip()
                if i == (len(food_list) - 1):
                    response += " and"
                    response += f" {food_item}."
                else:
                    response += f" {food_item},"
            if len(food_list) == 0:
                response = "There is no lunch being served today."
            await ctx.send(response)
        elif len(args) == 2:
            date_split = args[1].split("/")
            print(date_split)
            url = f"https://woodward.nutrislice.com/menu/upper-school/lunch/2020-{date_split[0]}-{date_split[1]}"
            driver.get(url)
            sleep(1)
            driver.find_element_by_xpath("//button[@class='primary']").click()
            driver.save_screenshot("check.png")
            sleep(1)
            food_list = driver.find_elements_by_xpath("//span[@class='food-name']")
            response = f"{args[1]}'s lunch includes"
            print(len(food_list))
            for i in range(len(food_list)):
                food_item = food_list[i].text.strip()
                print(food_item)
                if i == (len(food_list) - 1):
                    response += " and"
                    response += f" {food_item}."
                else:
                    response += f" {food_item},"
            if (len(food_list) == 0):
                response = "There is no lunch being served on that day."
            await ctx.send(response)
        else:
            raise ValueError("2")
    if args[0] == "events":
        if len(args) == 1:
            driver.get("https://wadaily.net")
            response = "The events for today are: \n"
            response += driver.find_element_by_xpath("//div[@class = 'Events']").text[6:]
        elif len(args) == 2:
            months = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September",
                      "October", "November", "December"]
            date_split = args[1].split("/")
            driver.get(f"https://wadaily.net?date={months[int(date_split[0])]}%20{date_split[1]}%202020")
            response = f"The events for {args[1]} are: \n"
            response += driver.find_element_by_xpath("//div[@class = 'Events']").text[6:]
        else:
            raise ValueError
        await ctx.send(response)
    if args[0] == "schedule":
        dates_csv = pd.read_csv("Fall_Schedule_20-21.csv")
        dates_csv = dates_csv.loc[:, ~dates_csv.columns.str.contains('^Unnamed')]
        dates_csv = dates_csv[:-1]
        dates_csv = dates_csv.replace("\r", ", ", regex=True)
        dates_csv = dates_csv.replace("             ", "", regex=True)
        length = len(dates_csv["MONDAY"])
        count = 0
        holder = []
        dates = [[], [], [], [], []]

        for x in range(length):
            holder.append(str(dates_csv["MONDAY"][x]).strip())
            holder.append(str(dates_csv["TUESDAY"][x]).strip())
            holder.append(str(dates_csv["WEDNESDAY"][x]).strip())
            holder.append(str(dates_csv["THURSDAY"][x]).strip())
            holder.append(str(dates_csv["FRIDAY"][x]).strip())

        for i in range(len(holder)-1):
            dates[count].append(holder[i])
            holder1 = int(holder[i][:holder[i].index(",")])
            holder2 = int(holder[i+1][:holder[i+1].index(",")])
            if holder1 > holder2:
                count += 1

        input_dates = args[1].split("/")
        selected_arr = dates[int(input_dates[0]) - 8]
        for b in range(len(selected_arr)):
            print(selected_arr[b][:selected_arr[b].index(",")])
            print(int(input_dates[1]))
            if(int(selected_arr[b][:selected_arr[b].index(",")]) == int(input_dates[1])):
                response = input_dates[0] + "/" + selected_arr[b]
                response = response.replace(",", ":", 1)
                await ctx.send(response)

@bot.command(name='weather', help="Gives weather forecast | ![] (date)")
async def weather(ctx, *args):
    url = "https://www.google.com/search?q=weather"
    print(args)
    if len(args) > 0:
        url += f"+{args[0]}+GA"
    url += "+ten+day"
    driver.get(url)
    driver.find_element_by_xpath("//div[@class='r']").click()
    sleep(1)
    driver.find_element_by_xpath("//div[@class='_-_-components-src-molecule-DaypartDetails-DaypartDetails--Detail"
                                 "SummaryContent--1-r0i _-_-components-src-atom-Disclosure-Disclosure--SummaryDefault--"
                                 "2XBO9 _-_-components-src-atom-Disclosure-Disclosure--positionShowOpenSummary--"
                                 "2r38t']").click()
    sleep(1)
    driver.save_screenshot("check.png")
    response = ""
    days = 1
    if len(args) == 2:
        days = int(args[1])
    for i in range(days):
        day = driver.find_element_by_xpath(f"//details[@id='detailIndex{i}']").text.replace("\n", ", ")
        print(day)
        pos1 = day.index("/")
        pos2 = day.index(", ")
        day = day[:pos1-2] + day[pos1:]
        day = day[:pos2] + ": " + day[pos2+2:]
        response += day + "\n"
    await ctx.send(response)

@bot.command(name='text', help="[]")
async def text(ctx, *args):
    await ctx.send('hi')

@bot.command(name='collatz', help="Pretty explanatory m8")
async def collatz(ctx, *args):
    i = int(args[0])
    response = await ctx.send(i)
    while i > 1:
        if i % 2 == 0:
            i /= 2
        else:
            i = 3*i + 1
        i = int(i)
        sleep(1)
        await response.edit(content=str(i))

@bot.command(name='pog', help="Pretty explanatory m8")
async def pog(ctx, *args):
    m1 = args[0]
    m2 = args[1]
    i = 0
    message = m1*int(args[2])
    response = await ctx.send(message)
    while i < int(args[2]):
        sleep(0.5)
        i += 1
        message = m2*i + m1*(int(args[2])-i)
        await response.edit(content=f"{message}")

@bot.event
async def on_message(message):
    print(message.content)
    if message.author == bot.user:
        return
    if message.content.lower().startswith("im ") or message.content.lower().startswith("i'm "):
        response = "Hey " + message.content[3:] + "! I'm Bot!"
        await message.channel.send(response)
    if "bot " in message.content.lower() or message.content.lower().endswith("bot.") or message.content.lower().endswith("bot"):
        response = ["Hello! Are you talking about me?","I'm doing great! Thanks for asking.","I am all-seeing omnipotent being. Don't test me.","I always love being included in the conversation :smiling_face_with_3_hearts:"]
        await message.channel.send(response[random.randint(0,3)])
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"I registered the message: '{ctx.message.content},' but I ran into an error while processing it.")
    print(error)

bot.run(TOKEN)