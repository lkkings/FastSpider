def num_to_base36(num: int) -> str:
    """数字转换成base32 (Convert number to base 36)"""

    base_str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

    if num == 0:
        return "0"

    base36 = []
    while num:
        num, i = divmod(num, 36)
        base36.append(base_str[i])

    return "".join(reversed(base36))


def _get_first_item_from_list(_list) -> list:
    # 检查是否是列表 (Check if it's a list)
    if _list and isinstance(_list, list):
        # 如果列表里第一个还是列表则提起每一个列表的第一个值
        # (If the first one in the list is still a list then bring up the first value of each list)
        if isinstance(_list[0], list):
            return [inner[0] for inner in _list if inner]
        # 如果只是普通列表，则返回这个列表包含的第一个项目作为新列表
        # (If it's just a regular list, return the first item wrapped in a list)
        else:
            return [_list[0]]
    return []


async def false_empty_afunc(*args):
    return False
