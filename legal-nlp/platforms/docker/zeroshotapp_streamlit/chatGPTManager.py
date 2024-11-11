from chatgpt_wrapper import ChatGPT


class chatGPTManager:
    def __init__(self):
        bot = ChatGPT()
        response = bot.ask("Hello, world!")
        print(response)


if __name__ == '__main__':
    chatGPTManager()