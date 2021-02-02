def many_start_with(check_text: str, keyword_list: list) -> bool:
    for keyword in keyword_list:
        if check_text.startswith(keyword):
            return True
    return False