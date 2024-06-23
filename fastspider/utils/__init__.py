# -*- coding: utf-8 -*-
"""
@Description: 
@Date       : 2024/4/8 17:48
@Author     : 
@Version    : 
@License    : 
@Github     : 
@Mail       : 
-------------------------------------------------
Change Log  :
2024/4/8 17:48 -  - 
"""
import random
import secrets

# 生成一个 16 字节的随机字节串 (Generate a random byte string of 16 bytes)
seed_bytes = secrets.token_bytes(16)

# 将字节字符串转换为整数 (Convert the byte string to an integer)
seed_int = int.from_bytes(seed_bytes, "big")

# 设置随机种子 (Seed the random module)
random.seed(seed_int)
