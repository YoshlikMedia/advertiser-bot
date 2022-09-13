from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ContentType, Message

from keyboards.inline import (group_cb, groups_list, post_settings,
                              post_type_btn, post_type_cb, setting_cb)
from loader import bot, dp
from utils.database import MongoDB
from utils.states import Advertisement


@dp.callback_query_handler(group_cb.filter(), state='*')
async def group_info(call: CallbackQuery, callback_data: dict, state: FSMContext):
    async with state.proxy() as data:
        data['group_id'] = callback_data.get('group_id')
    await call.message.edit_text("🛠 Post sozlamalari: ", reply_markup=await post_settings())


@dp.callback_query_handler(setting_cb.filter(setting_name='get_post'))
async def get_post(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        group_id = data.get('group_id')

    post = await MongoDB.get_post(group_id)

    if (post is None) or (post.get('message_id') is None):
        await call.message.edit_text("❌ Post hali yaratilmagan!")
        return

    message_id, chat_id = post.get('message_id'), post.get('chat_id')
    await call.message.delete()
    await bot.forward_message(call.from_user.id, chat_id, message_id)


@dp.callback_query_handler(setting_cb.filter(setting_name='set_post'), state='*')
async def set_post(call: CallbackQuery):
    await call.message.edit_text("📝 Yangi postni yuboring:")
    await Advertisement.GetAdvertisement.set()


@dp.message_handler(state=Advertisement.GetAdvertisement, content_types=ContentType.ANY)
async def get_advertisement(message: Message, state: FSMContext):
    async with state.proxy() as data:
        group_id = data.get('group_id')
        await MongoDB.update_groups(group_id, {"message_id": message.message_id,
                                               "chat_id": message.chat.id})

        await message.answer("✅ Post yaratildi!")
    await state.finish()


@dp.callback_query_handler(setting_cb.filter(setting_name='post_type'), state='*')
async def post_type(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        group_id = data.get('group_id')
    post = await MongoDB.get_post(group_id)
    await call.message.edit_text("📝 Post turi:", reply_markup=await post_type_btn(post.get('post_type')))


@dp.callback_query_handler(post_type_cb.filter())
async def post_type(call: CallbackQuery, callback_data: dict, state: FSMContext):
    async with state.proxy() as data:
        await MongoDB.update_groups(data.get('group_id'), {"post_type": callback_data.get('post_type')})
        await call.message.edit_text(text="✅ {} post turi saqlandi!".format(callback_data.get('post_type')))


