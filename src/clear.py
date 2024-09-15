import json  # 添加这一行
def clear():
    with open("config.json", "r",encoding='utf-8') as json_file:
        config_data = json.load(json_file)
        config_data['MAINURL'] = ""
        config_data['COOKIES'] = ""
        config_data['XM'] = ""
        with open("config.json", "w",encoding='utf-8') as json_file:
            json.dump(config_data, json_file, indent=4,ensure_ascii=False)
if __name__ == "__main__":
    clear()