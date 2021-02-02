from django.views.generic.base import View
from .models import Feedback, GroupInfo
from django.http import HttpResponse
from . import setting
import json
import requests
import time
from . import tools


class Api(View):
    def __init__(self, **kwargs):
        self.access_token = ""
        self.token_expire = 0
        self.update_tenant_access_token_info()
        super(Api, self).__init__(**kwargs)

    def post(self, request):
        req = json.loads(request.body)
        print("req", req)
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

    def update_tenant_access_token_info(self):
        if self.token_expire > time.time():
            return
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
        if rsp.text != "":
            self.access_token = json.loads(rsp.text)['tenant_access_token']
            self.token_expire = time.time() + json.loads(rsp.text)['expire'] - 1800
        return ""

    def handle_request_url_verify(self, req):
        """
            飞书验证服务器有效性接口
        """
        challenge = req.get("challenge", "")
        rsp = {'challenge': challenge}
        return json.dumps(rsp)
    
    def handle_event(self, req):
        event = req.get("event", {})
        event_type = event.get("type", "")

        if event_type == "":
            return "event_type is empty!"
        
        if event_type == "message":
            chat_type = event.get("chat_type", "")

            if chat_type == "private":
                text = event.get("text") + "？"
                self.send_message(event.get("open_id"), text, event.get("chat_type"))

            if chat_type == "group":
                chat_message = event.get("text_without_at_bot", "").lower().strip(" ")
                if tools.many_start_with(chat_message, ["bug"]):
                    new_feed_back = Feedback(
                        feedback_text=event.get("text_without_at_bot"),
                        chat_id=event.get("employee_id"),
                        user_id=event.get("open_chat_id")
                    )
                    new_feed_back.save()
                    text = "反馈已经收到！"
                    self.send_message(event.get("open_chat_id"), text, event.get("chat_type"))
                    return "send_message Done!"
                
                if tools.many_start_with(chat_message, ["update_group_info", "更新群"]):
                    self.update_group_info(event.get("open_chat_id"), event.get("chat_type"))
                    return "update_group_info Done!"
            return "chat_type is empty!"

    def send_message(self, back_id, text, chat_type):
        url = "https://open.feishu.cn/open-apis/message/v4/send/"

        self.update_tenant_access_token_info()

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

    def update_group_info(self, open_id, chat_type):
        page = ""
        self.update_tenant_access_token_info()

        def get_chat_info(page_token="0"):
            url = "https://open.feishu.cn/open-apis/chat/v4/list"
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self.access_token
            }
            req_body = {
                "page_size": "200"
            }
            if page_token != "0":
                req_body['page_token'] = page_token

            data = bytes(json.dumps(req_body), encoding='utf8')
            try:
                rsp = requests.get(url=url, data=data, headers=headers)
                rsp_body = json.loads(rsp.text)
                if rsp.status_code != 200 or rsp_body['code'] != 0:
                    print("get_chat_info error! body: ", rsp_body)
                    return {}, "0"
                page_token = rsp_body["data"].get("page_token")
            except Exception as e:
                print(e.read().decode())
                return {}, "0"

            return rsp_body["data"]["groups"], page_token

        while page != "0":
            temp_list, page = get_chat_info(page)
            GroupInfo.objects.all().delete()
            GroupInfo.objects.bulk_create([
                GroupInfo(
                    avatar=i['avatar'],
                    chat_id=i['chat_id'],
                    description=i['description'],
                    name=i['name'],
                    owner_open_id=i['owner_open_id'],
                    owner_user_id=i['owner_user_id'],
                ) for i in temp_list
            ])

        self.send_message(open_id, "更新群信息成功", chat_type)
