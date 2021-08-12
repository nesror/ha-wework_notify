import logging
import time
import datetime
import requests
import json
import os
import voluptuous as vol
import sys

from homeassistant.components.notify import (
    ATTR_MESSAGE,
    ATTR_TITLE,
    ATTR_DATA,
    ATTR_TARGET,
    PLATFORM_SCHEMA,
    BaseNotificationService,
)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)
DIVIDER = "——————————"

def get_service(hass, config, discovery_info=None):
    return WeWorkNotificationService(
        hass,
        config.get("corpid"),
        config.get("agentId"),
        config.get("secret"),
        config.get("touser"),
    )


class WeWorkNotificationService(BaseNotificationService):
    def __init__(self, hass, corpid, agentId, secret, touser):
        self._corpid = corpid
        self._corpsecret = secret
        self._agentid = agentId
        self._touser = touser
        self._token = ""
        self._token_expire_time = 0

    def _get_access_token(self):
        _LOGGER.debug("Getting token.")
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        values = {
            "corpid": self._corpid,
            "corpsecret": self._corpsecret,
        }
        req = requests.post(url, params=values)
        data = json.loads(req.text)
        if data["errcode"] != 0:
            _LOGGER.error("获取企业微信 Access token 失败。")
            _LOGGER.error(data)
        self._token_expire_time = time.time() + data["expires_in"]
        return data["access_token"]

    def get_access_token(self):
        if time.time() < self._token_expire_time:
            return self._token
        else:
            self._token = self._get_access_token()
            return self._token

    def send_message(self, message="", **kwargs):
        send_url = (
            "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token="
            + self.get_access_token()
        )
        title = kwargs.get("title")

        data = kwargs.get("data") or {}
        msgtype = data.get("type", "text")
        url = data.get("url")
        picurl = data.get("picurl")
        videopath = data.get("videopath")

        if msgtype == "text":
            content = ""
            if title is not None:
                content += f"{title}\n{DIVIDER}\n"
            content += message
            msg = {"content": content}
        elif msgtype == "textcard":
            msg = {"title": title, "description": message, "url": url}
        elif msgtype == "news":
            msg = {
                "articles": [
                    {
                        "title": title,
                        "description": message,
                        "url": url,
                        "picurl": picurl,
                    }
                ]
            }
        elif msgtype == "video":
            curl = (
                "https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token="
                + self.get_access_token()
                + "&type=video"
            )
            files = {"video": open(videopath, "rb")}
            r = requests.post(curl, files=files)
            re = json.loads(r.text)
            ree = re["media_id"]
            media_id = str(ree)
            msg = {"media_id": media_id, "title": title, "description": message}
        else:
            raise TypeError("消息类型输入错误，请输入：text/textcard/news/video")
        send_values = {
            "touser": self._touser,
            "msgtype": msgtype,
            "agentid": self._agentid,
            msgtype: msg,
            "safe": "0",
        }
        _LOGGER.debug(send_values)
        send_msges = bytes(json.dumps(send_values), "utf-8")
        response = requests.post(send_url, send_msges).json()
        if response["errcode"] != 0:
            _LOGGER.error(response)
        else:
            _LOGGER.debug(response)
