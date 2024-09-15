# 初始化字典
def init():
    #建立一个数据库字典，用于存储每个月份各个城市的库存情况
    #城市有上海	广州	武汉	北京	济南	苏州	常熟	泰安	深圳	珠海
    #月份month有1-12月
    #库存商品有#品牌茶饮 品牌果汁 品牌咖啡  品牌汽水 品牌饮用水  网红茶饮 网红果汁  网红咖啡 网红汽水 网红饮用水 自营茶饮 自营咖啡 自营果汁 自营汽水 自营饮用水
    #开始
    citys = ['上海','广州','武汉','北京','济南','苏州','常熟','泰安','深圳','珠海']
    months = [1,2,3,4,5,6,7,8,9,10,11,12]
    goods = ['品牌茶饮','品牌果汁','品牌咖啡','品牌汽水','品牌饮用水','网红茶饮','网红果汁','网红咖啡','网红汽水','网红饮用水','自营茶饮','自营咖啡','自营果汁','自营汽水','自营饮用水']
    #建立一个字典，用于存储每个月份各个城市的库存情况
    stock = {}
    for city in citys:
        stock[city] = {}
        for month in months:
            stock[city][month] = {}
            for good in goods:
                stock[city][month][good] = 0
    #打印字典
    print(stock)
    #保存到stock.json文件，能以中文显示,没有则在当前目录下新建一个stock.json文件    
    import json
    with open('stock.json','w',encoding='utf-8') as f:
        json.dump(stock,f,ensure_ascii=False)







 









 
 
