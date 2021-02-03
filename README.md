# DjangoProject

## 简介

***不要上传带密钥的 setting文件***  
***不要上传带密钥的 setting文件***  
***不要上传带密钥的 setting文件***  

## 文档

1. [Django 3.1 文档](https://docs.djangoproject.com/zh-hans/3.1/)
2. [飞书开放平台](https://open.feishu.cn/document/uQjL04CN/ucDOz4yN4MjL3gzM)

## 本地配置

### mysite.setting

```python
    # mysite.setting.py 找到下列配置项

    SECRET_KEY = "anything" # 可以是任意字符串

    # 按数据库实际填写
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}
```

### feishu.setting

```python
    # feishu.setting.py 找到下列配置项

    APP_ID = "" # 飞书机器人的 APP_ID
    APP_SECRET = "" # 飞书机器人的 APP_SECRET
    APP_VERIFICATION_TOKEN = "" # 飞书机器人的 APP_VERIFICATION_TOKEN

}
```

***

## 快速上手

1. powershell 切换到 /mysite 目录下
2. python manage.py runserver
3. [本地打开](http://127.0.0.1:8000)
