import json  # 添加这一行
def clear():
    with open("config.json", "r") as json_file:
        config_data = json.load(json_file)
        config_data['MAINURL'] = ""
        config_data['COOKIES'] = ""
        with open("config.json", "w") as json_file:
            json.dump(config_data, json_file, indent=4)
if __name__ == "__main__":
    clear()