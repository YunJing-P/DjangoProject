from django.views.generic.base import View
from .models import Feedback
from django.http import HttpResponse
from . import setting
import json
import requests
import time
from django.views.decorators.csrf import csrf_exempt

class Api(View):
    def __init__(self, **kwargs):
        self.access_token = ""
        self.update_token()

        super(Api, self).__init__(**kwargs)

    def post(self, request):
        req = json.loads(request.body)

        token = req.get("token", "")
        if token != setting.APP_VERIFICATION_TOKEN:
            print("verification token not match, token =", token)
            return HttpResponse("verification token not match, token ={}".format(token))

        req_type = req.get("type", "")
        if req_type == "":
            return HttpResponse("type is empty!")

        if req_type == "url_verification":
            return HttpResponse(self.handle_request_url_verify(req))
        
        if req_type == "event_callback":
            return HttpResponse(self.handle_event(req))
        
        return HttpResponse("type is error!")

    def update_token(self):
        token_info = self.get_tenant_access_token_info()
        if token_info != "":
            self.access_token = json.loads(token_info)['tenant_access_token']
            self.token_expire = time.time() + json.loads(token_info)['expire'] - 1800

    def get_tenant_access_token_info(self):
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
        headers = {
            "Content-Type" : "application/json"
        }
        req_body = {
            "app_id": setting.APP_ID,
            "app_secret": setting.APP_SECRET
        }

        data = bytes(json.dumps(req_body), encoding='utf8')
        rsp = requests.post(url=url, data=data, headers=headers)

        if rsp.status_code != 200 or json.loads(rsp.text)['code'] != 0:
            return ""
        return rsp.text

    def handle_request_url_verify(self, req):
        '''
            飞书验证服务器有效性接口
        '''
        challenge = req.get("challenge", "")
        rsp = {'challenge': challenge}
        return (json.dumps(rsp))
    
    def handle_event(self, req):
        event = req.get("event", {})
        event_type = event.get(("type", ""))

        if event_type == "":
            return "event_type is empty!"
        
        if event_type == "message":
            chat_type = event.get(("chat_type", ""))

            if chat_type == "private":
                text = event.get("text") + "？"
                self.send_message(event.get("open_id"), text, event.get("chat_type"))

            if chat_type == "group":
                if event.get("text_without_at_bot", "").lower().startswith("bug "):
                    new_feed_back = Feedback(
                        feedback_text=event.get("text_without_at_bot"),
                        chat_id=event.get("employee_id"),
                        user_id=event.get("open_chat_id")
                    )
                    new_feed_back.save()
                    text = "反馈已经收到！"
                    self.send_message(event.get("open_chat_id"), text, event.get("chat_type"))
                    return "send_message Done!"
            return "chat_type is empty!"

    def send_message(self, back_id, text, chat_type):
        url = "https://open.feishu.cn/open-apis/message/v4/send/"

        if self.token_expire <= time.time():
            self.update_token()

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.access_token
        }
        req_body = {
            "msg_type": "text",
            "content": {
                "text": text
            }
        }
        if "group" == chat_type:
            req_body["chat_id"] = back_id
        else :
            req_body["open_id"] = back_id

        data = bytes(json.dumps(req_body), encoding='utf8')
        rsp = requests.post(url=url, data=data, headers=headers)

        rsp_body = json.loads(rsp.text)
        if rsp.status_code != 200 or rsp_body['code'] != 0:
            print("send message error, code = ", rsp_body['code'], ", msg =", rsp_body.get("msg", ""))
            return ""
