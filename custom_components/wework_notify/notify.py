import logging
import time
import requests
import json
import os
import base64
import voluptuous as vol

from homeassistant.components.notify import (
    ATTR_MESSAGE,
    ATTR_TITLE,
    ATTR_DATA,
    ATTR_TARGET,
    PLATFORM_SCHEMA,
    BaseNotificationService,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_RESOURCE

_LOGGER = logging.getLogger(__name__)
DIVIDER = "———————————"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required("corpid"): cv.string,
    vol.Required("agentId"): cv.string,
    vol.Required("secret"): cv.string,
    vol.Required("touser"): cv.string,
    vol.Optional(CONF_RESOURCE, default = "https://qyapi.weixin.qq.com/cgi-bin"): cv.url,
    vol.Optional("resource_username", default = ""): cv.string,
    vol.Optional("resource_password", default = ""): cv.string,
    vol.Optional("https_proxies", default = ""): cv.string,

})


def get_service(hass, config, discovery_info=None):
    return WeWorkNotificationService(
        hass,
        config.get("corpid"),
        config.get("agentId"),
        config.get("secret"),
        config.get("touser"),
        config.get(CONF_RESOURCE),
        config.get("resource_username"),
        config.get("resource_password"),
        config.get("https_proxies"),
    )


class WeWorkNotificationService(BaseNotificationService):
    def __init__(self, hass, corpid, agentId, secret, touser, weworkbaseurl, resource_username, resource_password, https_proxies):
        self._corpid = corpid
        self._corpsecret = secret
        self._agentid = agentId
        self._touser = touser
        self._weworkbaseurl = weworkbaseurl
        self._httpsproxies = { "https": https_proxies } 
        self._token = ""
        self._token_expire_time = 0

        if resource_username and resource_password:
            self._header = {"Authorization": "Basic {}".format(self.getAuth(resource_username,resource_password))} 
        else:
            self._header = {}
        
        
    def getAuth(self,uername,password):
        serect = uername + ":"+password
        bs = str(base64.b64encode(serect.encode("utf-8")), "utf-8")
        return bs

    def _get_access_token(self):
        _LOGGER.debug("Getting token.")
        url = self._weworkbaseurl + "/gettoken"
        values = {
            "corpid": self._corpid,
            "corpsecret": self._corpsecret,
        }
        req = requests.post(url, params=values, headers=self._header, proxies=self._httpsproxies)
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
            self._weworkbaseurl + "/message/send?access_token="
            + self.get_access_token()
        )
        title = kwargs.get(ATTR_TITLE)

        data = kwargs.get(ATTR_DATA) or {}
        msgtype = data.get("type", "text")
        url = data.get("url")
        picurl = data.get("picurl")
        videopath = data.get("videopath")
        imagepath = data.get("imagepath")
        safe = data.get("safe") or 0
        touser = kwargs.get(ATTR_TARGET) or [self._touser]
        touser = '|'.join(touser)

        if msgtype == "text":
            content = ""
            if title is not None:
                content += f"{title}\n{DIVIDER}\n"
            content += message
            msg = {"content": content}
        elif msgtype == "textcard":
            msg = {"title": title, "description": message, "url": url}
        elif msgtype == "news":
            curl = (
                self._weworkbaseurl + "/media/uploadimg?access_token="
                + self.get_access_token()
                + "&type=image"
            )
            if imagepath and os.path.isfile(imagepath):
                files = {"image": open(imagepath, "rb")}
                try:
                    r = requests.post(curl, files=files, headers=self._header, proxies=self._httpsproxies, timeout=(20,180))
                    _LOGGER.debug("Uploading media " + imagepath + " to WeChat servicers")
                except requests.Timeout: 
                    _LOGGER.error("File upload timeout, please try again later.")
                    return                
                re = json.loads(r.text)["url"]

            elif picurl:
                re = picurl
            else:
                re = ''
            if not url:
                url = re
            msg = {
                "articles": [
                    {
                        "title": title,
                        "description": message,
                        "url": url,
                        "picurl": re,
                    }
                ]
            }
        elif msgtype == "mpnews":
            curl = (
                self._weworkbaseurl + "/media/upload?access_token="
                + self.get_access_token()
                + "&type=image"
            )
            if imagepath and os.path.isfile(imagepath):
                files = {"image": open(imagepath, "rb")}
                try:
                    r = requests.post(curl, files=files, headers=self._header, proxies=self._httpsproxies, timeout=(20,180))
                    _LOGGER.debug("Uploading media " + imagepath + " to WeChat servicers")
                except requests.Timeout: 
                    _LOGGER.error("File upload timeout, please try again later.")
                    return
                re = json.loads(r.text)
                if int(re['errcode']) != 0:
                    _LOGGER.error("Upload failed. Error Code " + str(re['errcode']) + ". " + str(re['errmsg']))
                    return
                ree = re["media_id"]
                media_id = str(ree)
                picurl = self._weworkbaseurl + "/media/get?access_token=" + self.get_access_token() + "&media_id=" + media_id  #这个地址最好不要发送，可能会泄漏代理或中转服务器信息。非可信IP也是不可使用的。
            else:
                raise TypeError("本地图片地址未填写或图片不存在，消息类型为mpnews时本地图片地址为必填！")
                return
            msg = {
                "articles": [
                    {
                        "title": title,
                        "thumb_media_id": media_id,
                        "content": message,
                        "digest": message,
                        "show_cover_pic": "1",                        
                    }
                ]
            }    
        elif msgtype == "video":
            curl = (
                self._weworkbaseurl + "/media/upload?access_token="
                + self.get_access_token()
                + "&type=video"
            )
            if not videopath:
                raise TypeError("视频地址未填写，消息类型为视频卡片时此项为必填！")
                return
            files = {"video": open(videopath, "rb")}
            try:
                r = requests.post(curl, files=files, headers=self._header, proxies=self._httpsproxies, timeout=(20,180))
                _LOGGER.debug("Uploading media " + videopath + " to WeChat servicers")
            except requests.Timeout: 
                _LOGGER.error("File upload timeout, please try again later.")
                return
            re = json.loads(r.text)
            if int(re['errcode']) != 0:
                _LOGGER.error("Upload failed. Error Code " + str(re['errcode']) + ". " + str(re['errmsg']))
                return
            ree = re["media_id"]
            media_id = str(ree)
            msg = {"media_id": media_id, "title": title, "description": message}

        else:
            raise TypeError("消息类型输入错误，请输入：text/textcard/news/mpnews/video")

        send_values = {
            "touser": touser,
            "msgtype": msgtype,
            "agentid": self._agentid,
            msgtype: msg,
            "safe": safe,
        }
        _LOGGER.debug(send_values)
        send_msges = bytes(json.dumps(send_values), "utf-8")
        response = requests.post(send_url, send_msges, headers=self._header, proxies=self._httpsproxies).json()
        if response["errcode"] != 0:
            _LOGGER.error(response)
        else:
            _LOGGER.debug(response)
