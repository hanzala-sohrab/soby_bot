import json
import typing
import requests
import datetime
import gspread
import foo

from time import time
from datetime import datetime
from gspread.exceptions import CellNotFound

gc = gspread.service_account(filename="./service_account.json")
sh = gc.open_by_url(foo.URL)
worksheet_list = sh.worksheets()
worksheet1 = worksheet_list[0]
worksheet3 = worksheet_list[1]


class WABot():
    def __init__(self, json):
        self.json = json
        self.dict_messages = json['messages']
        self.APIUrl = foo.APIUrl
        self.token = foo.token

    def send_requests(self, method, data):
        url = f"{self.APIUrl}{method}?token={self.token}"
        headers = {'Content-type': 'application/json'}
        answer = requests.post(url, data=json.dumps(data), headers=headers)
        return answer.json()

    def send_message(self, chatId, text):
        data = {"chatId" : chatId,
                "body" : text}
        answer = self.send_requests('sendMessage', data)
        return answer

    def welcome(self,chatId, noWelcome = False):
        welcome_string = ''
        if noWelcome == False:
            phone = chatId[0:-5]
            r = c = -1
            try:
                prospect = worksheet3.find(phone)
            except CellNotFound:
                r = len(worksheet3.col_values(1)) + 1
                c = 1
                worksheet3.update_cell(r, c, phone)
            i = 2
            welcome_string = "صوبی ایگڑو، ڈسکا میں خوشآمدید\nWelcome to Soby Agro, Daska\n\n"
            while True:
                cell = f"A{i}"
                item = worksheet1.acell(cell).value
                if item == None:
                    break
                welcome_string += f"{i-1}. {item}\n"
                i += 1
            welcome_string += "\n\nاوپر دییۓ گئ لسٹ میں سے اپنی دلچسپی کے پروڈکٹ کا نمبر درج کریں، مسال کے تور پر: اوٹومیٹک ریپڑ کے لئے 1 لکھ کر مسج کریں\nPlease choose your product from the list and send a message with its number\nEg: for Automatic Self Propelled Reaper send 1 in message"
        else:
            welcome_string = """Incorrect command
                                Commands:
                                1. chatid - show ID of the current chat
                                2. time - show server time
                                3. me - show your nickname
                                4. file [format] - get a file. Available formats: doc/gif/jpg/png/pdf/mp3/mp4
                                5. ptt - get a voice message
                                6. geo - get a location
                                7. group - create a group with the bot"""
        return self.send_message(chatId, welcome_string)

    def time(self, chatId):
        t = datetime.datetime.now()
        time = t.strftime('%d:%m:%Y')
        return self.send_message(chatId, time)

    def file(self, chatId, format, fileName, url, caption=''):
        availableFiles = ['doc', 'gif', 'jpg', 'png', 'pdf', 'mp4', 'mp3', 'mkv']
        if format in availableFiles:
            data = {
                'chatId' : chatId,
                'body': url,
                'filename' : fileName,
                'caption' : caption
            }
            return self.send_requests('sendFile', data)
        return self.send_requests("sendMessage", {})

    def product_of_interest(self, chatId, prod):
        # _time = int(time())
        botMessage = ""
        try:
            total = len(worksheet1.col_values(1))
            if prod > total:
                raise CellNotFound
            # url = worksheet1.acell(f"C{prod + 1}", value_render_option="FORMULA").value[8:-2]
            # imageName = url.split(".")[0]
            # imageExtension = url.split(".")[-1]
            message = worksheet1.acell(f"F{prod + 1}").value + "\n\n" + worksheet1.acell(f"E{prod + 1}").value
            phone = chatId[0:-5]
            prospect = worksheet3.find(phone)
            r = prospect.row
            poi = worksheet1.acell(f"A{prod + 1}").value
            initialPOI = worksheet3.acell(f"C{r}").value
            if initialPOI is None:
                initialPOI = poi
            else:
                initialPOI += "," + poi
            # if poi not in initialPOI:
            #     initialPOI += "," + poi
            worksheet3.update_cell(r, 3, initialPOI)
            now = datetime.now()
            year = now.strftime("%Y")
            month = now.strftime("%m")
            day = now.strftime("%d")
            dateOfEnquiry = f"{day}.{month}.{year}"
            initiaDOE = worksheet3.acell(f"D{r}").value
            if initiaDOE is None:
                initiaDOE = dateOfEnquiry
            else:
                initiaDOE += "," + dateOfEnquiry
            # if dateOfEnquiry not in initiaDOE:
            #     initiaDOE += "," + dateOfEnquiry
            worksheet3.update_cell(r, 4, initiaDOE)
            # self.file(chatId, imageExtension, imageName, url, message)
            # while int(time()) < _time + 10:
            #     pass
            url = worksheet1.acell(f"D{prod + 1}").value
            video = url.split("/")[-1]
            format = video.split(".")[-1]
            return self.file(chatId, format, video, url, message)
        except CellNotFound:
            botMessage = "No such product found!"
            return self.send_message(chatId, botMessage)

    def location(self, chatId, place):
        phone = chatId[0:-5]
        prospect = worksheet3.find(phone)
        r = prospect.row
        initialPlace = worksheet3.acell(f"B{r}").value
        if initialPlace is None:
            initialPlace = place
        else:
            initialPlace += "," + place
        # if place not in initialPlace:
        #     initialPlace += "," + place
        worksheet3.update_cell(r, 2, initialPlace)
        return self.send_message(chatId, "Thanks. \n\nIf you would like to know more, type in *hi* or *hello*")

    def produc_of_interest_flow(self, chatId, keyword):
        # _time = int(time())
        phone = chatId[0:-5]
        product = worksheet1.find(keyword)
        prod = product.row
        r = 0
        try:
            prospect = worksheet3.find(phone)
            r = prospect.row
        except CellNotFound:
            r = len(worksheet3.col_values(1)) + 1
            worksheet3.update_cell(f"A{r}", phone)

        poi = worksheet1.acell(f"A{prod}").value
        initialPOI = worksheet3.acell(f"C{r}").value
        if initialPOI is None:
            initialPOI = poi
        else:
            initialPOI += "," + poi
        # if poi not in initialPOI:
        #     initialPOI += "," + poi
        worksheet3.update_cell(r, 3, initialPOI)
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")
        dateOfEnquiry = f"{day}.{month}.{year}"
        initiaDOE = worksheet3.acell(f"D{r}").value
        if initiaDOE is None:
            initiaDOE = dateOfEnquiry
        else:
            initiaDOE += "," + dateOfEnquiry
        # if dateOfEnquiry not in initiaDOE:
        #     initiaDOE += "," + dateOfEnquiry
        worksheet3.update_cell(r, 4, initiaDOE)
        # url = worksheet1.acell(f"C{prod}", value_render_option="FORMULA").value[8:-2]
        # imageName = url.split(".")[0]
        # imageExtension = url.split(".")[-1]
        message = worksheet1.acell(f"F{prod}").value + "\n\n" + worksheet1.acell(f"E{prod}").value
        # self.file(chatId, imageExtension, imageName, url, message)
        # while int(time()) < _time + 10:
        #     pass
        url = worksheet1.acell(f"D{prod}").value
        video = url.split("/")[-1]
        format = video.split(".")[-1]
        return self.file(chatId, format, video, url, message)

    def typing(self, chatId):
        phone = chatId[0:-5]
        data = {
            "phone": phone,
            "chatId": chatId,
            "on": "true",
            "duration": 30
        }
        return self.send_requests("typing", data)

    def processing(self):
        if self.dict_messages != []:
            print(self.dict_messages)
            for message in self.dict_messages:
                text = message['body'].split()
                if not message['fromMe']:
                    id  = message['chatId']
                    if "-" not in id:
                        url = f"{self.APIUrl}messagesHistory?page=0&count=10&chatId={id}&token={self.token}"
                        foo = requests.get(url).json()["messages"]
                        prevMessage = foo[1]["body"]
                        if text[0].lower() in ['dfhdfhgfh535']:
                            self.typing(id)
                            return self.welcome(id)
                        elif "abc.com" in message['body']:
                            self.typing(id)
                            m = message['body']
                            i = m.index("www.abc.com/")
                            keyword = ""
                            while i < len(m) and m[i] != ' ':
                                keyword += m[i]
                                i += 1
                            _time = message['time']
                            self.produc_of_interest_flow(id, keyword)
                            while int(time()) < _time + 60:
                                pass
                            self.typing(id)
                            return self.send_message(
                                id, "آپ کا ضلعی کونسا ہے سڑجی؟\nWhat is your District Area Sir?")
                        elif "https://fb.me" in message["body"]:
                            self.typing(id)
                            m = message['body']
                            i = m.index("https://fb.me")
                            keyword = ""
                            while i < len(m) and m[i] != ' ':
                                keyword += m[i]
                                i += 1
                            _time = message['time']
                            self.produc_of_interest_flow(id, keyword)
                            while int(time()) < _time + 60:
                                pass
                            self.typing(id)
                            return self.send_message(
                                id, "آپ کا ضلعی کونسا ہے سڑجی؟\nWhat is your District Area Sir?")
                        elif "fb.me" in message["body"]:
                            self.typing(id)
                            m = message['body']
                            i = m.index("fb.me")
                            keyword = ""
                            while i < len(m) and m[i] != ' ':
                                keyword += m[i]
                                i += 1
                            _time = message['time']
                            self.produc_of_interest_flow(id, keyword)
                            while int(time()) < _time + 60:
                                pass
                            self.typing(id)
                            return self.send_message(
                                id, "آپ کا ضلعی کونسا ہے سڑجی؟\nWhat is your District Area Sir?")
                        elif "choose your product" in prevMessage:
                            try:
                                poi = int(message['body'])
                                _time = message['time']
                                self.typing(id)
                                self.product_of_interest(id, poi)
                                while int(time()) < _time + 60:
                                    pass
                                self.typing(id)
                                return self.send_message(id, "آپ کا ضلعی کونسا ہے سڑجی؟\nWhat is your District Area Sir?")
                            except ValueError:
                                return self.send_message(id, f"Wrong input format. Enter an integer between 1 and {len(worksheet1.col_values(1)) - 1}")
                        elif "District" in prevMessage:
                            return self.location(id, message["body"])
                    return 'NoCommand'
                return 'NoCommand'
