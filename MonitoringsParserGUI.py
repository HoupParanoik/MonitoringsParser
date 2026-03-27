import customtkinter
import requests
from bs4 import BeautifulSoup

def parser(vers, minDrop, maxDrop, minOnline, maxOnline):
    SERVERVERSION = vers # "1.21" # NO DROP NUMBER
    MINIMUMDROP = minDrop
    MAXIMUMDROP = maxDrop
    MINIMUMONLINE = minOnline
    MAXIMUMONLINE = maxOnline

    serversDict = []

    url = "https://minecraftrating.ru/new-servers/"
    url2 = "https://minecraft-servers.ru/servera-1.21.4"
    response = requests.get(url)
    response2 = requests.get(url2)

    html_content = response.text
    html_content2 = response2.text
    soup = BeautifulSoup(html_content, "html.parser")
    soup2 = BeautifulSoup(html_content2, "html.parser")

    servers = soup.find_all("div", class_="item-control")
    servers2 = soup2.find_all("tr", class_="flex items-end gap-2 container mx-auto w-full py-4")

    serverTitles = []
    for drop in range(MINIMUMDROP, MAXIMUMDROP+1):

        link = f"https://minecraftrating.ru/new-servers/{SERVERVERSION}.{drop}/"
        responsefor = requests.get(link)
        html_contentfor = responsefor.text
        soupfor = BeautifulSoup(html_contentfor, "html.parser")
        serversfor = soupfor.find_all("div", class_="item-control")

        for idx, server in enumerate(serversfor, start=0):

            if server.find('a', class_="item-control__copy-link item-control__copy-link--2 link-2 add_event_stat"):
                continue

            title = server.find('h4', class_='left-item-control__title').text

            if title in serverTitles and (not title == "Сервер Minecraft" or not title == "A Minecraft Server"):
                continue

            serverTitles.append(title)
            online = server.find("div", class_="left-item-control__info-item left-item-control__info-item--online").span.text

            if int(online) < MINIMUMONLINE: continue
            if int(online) > MAXIMUMONLINE: continue

            version = server.find("i", class_="fas fa-check-circle").parent.text
            if not SERVERVERSION == "none":
                if not version.startswith(SERVERVERSION): continue

            slogan = server.find("p", class_="left-item-control__info").text
            ip = server.find("button", class_="item-control__copy add_event_stat").span.text

            serverDict = dict(online = online, version = version, ip = ip, title = title, slogan = slogan)
            serversDict.append(serverDict)

    for server in servers2:

        title = server.a.text

        if title in serverTitles and (not title == "Сервер Minecraft" or not title == "A Minecraft Server"):
            continue

        serverTitles.append(title)
        online = server.find("svg", class_="lucide lucide-users").parent.span.text

        if online == "Выключен": continue
        if int(online) < MINIMUMONLINE: continue
        if int(online) > MAXIMUMONLINE: continue

        version = server.find("svg", class_="lucide lucide-info").parent.span.text
        if not SERVERVERSION == "none":
            if not version.startswith(SERVERVERSION): continue

        ip = server.find("span", class_="overflow-hidden overflow-ellipsis whitespace-nowrap").text
        
        serverDict = dict(online = online, version = version, ip = ip, title = title, slogan = slogan)
        serversDict.append(serverDict)

    return serversDict


class App(customtkinter.CTk):
        
    def copy_ip(self, ip, button):
        self.clipboard_clear()
        self.clipboard_append(ip)
        button.configure(text="Скопировано!")
    
    def sliderMin(self, btn, onlineMin, onlineMax):
        if onlineMin.get() > onlineMax.get():
            onlineMin.set(onlineMax.get())
        btn.configure(text=f'Минимальный онлайн: {int(onlineMin.get())}')
    def sliderMax(self, btn, onlineMin, onlineMax):
        if onlineMax.get() < onlineMin.get():
            onlineMax.set(onlineMin.get())
        btn.configure(text=f'Максимальный онлайн: {int(onlineMax.get())}')

    def __init__(self):
        super().__init__()

        self.title("Парсер Мониторингов")
        self.geometry("300x450")
        self.resizable(False, False)

        versions = customtkinter.CTkOptionMenu(master=self, values=["1.16", '1.17', '1.18', '1.19', '1.20', '1.21'])
        
        minimumdrop = customtkinter.CTkEntry(self, placeholder_text="Минимальный дроп версии")
        maximumdrop = customtkinter.CTkEntry(self, placeholder_text="Максимальный дроп версии")

        minimumOnline = customtkinter.CTkSlider(self, from_=0, to=100)
        minimumOnlineLabel = customtkinter.CTkLabel(self, text="Минимальный онлайн: 50")
        maximumOnline = customtkinter.CTkSlider(self, from_=0, to=100)
        maximumOnlineLabel = customtkinter.CTkLabel(self, text="Максимальный онлайн: 50")
        minimumOnline.configure(command=lambda value: self.sliderMin(minimumOnlineLabel, minimumOnline, maximumOnline))
        maximumOnline.configure(command=lambda value: self.sliderMax(maximumOnlineLabel, minimumOnline, maximumOnline))
        
        versions.pack(padx=20, pady=10)
        minimumdrop.pack(padx=20, pady=10)
        maximumdrop.pack(padx=20, pady=10)
        minimumOnlineLabel.pack(padx=20, pady=10)
        minimumOnline.pack(padx=20, pady=10)
        maximumOnlineLabel.pack(padx=20, pady=10)
        maximumOnline.pack(padx=20, pady=10)
        versions.set("1.21")
        findButton = customtkinter.CTkButton(self, text="Найти сервера", command=lambda: self.list(versions.get(), int(minimumdrop.get()), int(maximumdrop.get()), int(minimumOnline.get()), int(maximumOnline.get())))
        findButton.pack(padx=20, pady=10)

    def list(self, version, minDrop, maxDrop, minOnline, maxOnline):
        window = customtkinter.CTkToplevel(self)
        window.title("Парсер Мониторингов")
        window.geometry("300x250")
        window.resizable(True, True)
        
        window.grid_columnconfigure((0, 1), weight=1)

        scrollFrame = customtkinter.CTkScrollableFrame(window)
        scrollFrame.pack(fill="both", expand=True)

        serversDict = parser(version, minDrop, maxDrop, minOnline, maxOnline)

        for i in range(len(serversDict)):
            window.frame = customtkinter.CTkFrame(scrollFrame)
            window.frame.grid(row=i, column=0, padx=10, pady=(10, 10), sticky="nsw")
            # Name
            window.label = customtkinter.CTkLabel(window.frame, text=serversDict[i]['title'], fg_color="transparent", font=("Avenir Next Cyr Medium", 24))
            window.label.grid(row=i, column=0, padx=20, pady=0, sticky="w")
            # Version & Players Online
            window.label = customtkinter.CTkLabel(window.frame, text=f"🖥️{serversDict[i]['version']} 🧍{serversDict[i]['online']}", fg_color="transparent", font=("Avenir Next Cyr Medium", 16))
            window.label.grid(row=i+1, column=0, padx=20, pady=1, sticky="w")
            # Slogan
            window.label = customtkinter.CTkLabel(window.frame, text=serversDict[i]['slogan'], fg_color="transparent", font=("Avenir Next Cyr Medium", 16))
            window.label.grid(row=i+2, column=0, padx=20, pady=1, sticky="w")
            # Copy IP Button
            btn = customtkinter.CTkButton(window.frame, text=serversDict[i]['ip'])
            btn.configure(command= lambda i=i, btn=btn: self.copy_ip(serversDict[i]['ip'], btn))
            btn.grid(row=i+3, column=0, padx=20, pady=(0, 10), sticky="w")

app = App()
app.mainloop()