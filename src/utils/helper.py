from datetime import datetime, date, timedelta

def blubber_instances_to_dict(list_of_instances):
    """Convert a list of blubber model instances into dictionaries for frontend."""
    dictionaried_list = []
    for _instance in list_of_instances:
        instance = _instance.to_dict()
        dictionaried_list.append(instance)
    return dictionaried_list

#eventually make this more robust, where you can specify precision of date
def json_date_to_python_date(js_date_str):
    format = "%Y-%m-%d"
    if "T" in js_date_str:
        python_date_str = js_date_str.split("T")[0]
    else:
        python_date_str = js_date_str
    python_date = datetime.strptime(python_date_str, format).date()
    return python_date

def is_item_in_itemlist(item, itemlist):
    item_id_list = [item.id for item in itemlist]
    return item.id in item_id_list
