from aiogram.utils.callback_data import CallbackData

language_callback = CallbackData("select_language", 'language')
main_menu_callback = CallbackData("main_menu", "_")
empty_callback = CallbackData("empty", "_")
delete_message_callback = CallbackData("delete_message", "_")
list_objects_callback = CallbackData("list_objects", 'page')
open_object_callback = CallbackData("open_object", 'object_id')

filter_date_callback = CallbackData("filter_date", '_')
filter_district_callback = CallbackData("filter_district", 'page')
district_callback = CallbackData("district", 'district_id', 'page')
districts_drop_callback = CallbackData("drop_districts", '_')
select_price_callback = CallbackData("select_price", 'price')
price_drop_callback = CallbackData("drop_price", '_')
date_drop_callback = CallbackData("drop_date", '_')


object_callback = CallbackData("object", 'object_id', 'action')
object_photos_callback = CallbackData("object_photos", 'photo_index', 'object_id')

form_callback = CallbackData("form", 'action')
chat_callback = CallbackData("chat", 'chat_id', 'new_msg')
call_callback = CallbackData("chat", 'companion_id', 'chat_id', 'action')
after_call_callback = CallbackData("after_call", 'chat_id', 'action')





