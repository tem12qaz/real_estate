from aiogram.utils.callback_data import CallbackData

language_callback = CallbackData("select_language", 'language')
main_menu_callback = CallbackData("main_menu", "_")
empty_callback = CallbackData("empty", "_")
list_objects_callback = CallbackData("list_objects", 'page')
open_object_callback = CallbackData("open_object", 'object_id')

filter_date_callback = CallbackData("filter_date", '_')
filter_district_callback = CallbackData("filter_district", 'page')
district_callback = CallbackData("district", 'district_id', 'page')
districts_drop_callback = CallbackData("drop_districts", '_')
select_price_callback = CallbackData("select_price", 'price')
price_drop_callback = CallbackData("drop_price", '_')


