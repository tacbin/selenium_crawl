import os

from revChatGPT.revChatGPT  import Chatbot


class ChatGPT:
    @staticmethod
    def ask_and_answer(ask):
        # openai.api_key = "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"

        config = {
            "session_token": "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"
        }
        # 创建一个服务，把当前这个python文件当做一个服务
        chatbot = Chatbot(config, conversation_id=None)


        message = chatbot.get_chat_response(ask)['message']
        print(message)
        return message