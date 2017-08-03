#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2017
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
from datetime import datetime

import pytest

from telegram import Update, Message, User, MessageEntity, Chat, Audio, Document, \
    Game, PhotoSize, Sticker, Video, Voice, VideoNote, Contact, Location, Venue, Invoice, \
    SuccessfulPayment


@pytest.fixture(scope="class")
def message(bot):
    return Message(message_id=TestMessage.id,
                   from_user=TestMessage.from_user,
                   date=TestMessage.date,
                   chat=TestMessage.chat, bot=bot)


@pytest.fixture(scope="function",
                params=[
                    {'forward_from': User(99, 'forward_user'),
                     'forward_date': datetime.now()},
                    {'forward_from_chat': Chat(-23, 'channel'),
                     'forward_from_message_id': 101,
                     'forward_date': datetime.now()},
                    {'reply_to_message': Message(50, None, None, None)},
                    {'edit_date': datetime.now()},
                    {'test': 'a text message',
                     'enitites': [{'length': 4, 'offset': 10, 'type': 'bold'},
                                  {'length': 7, 'offset': 16, 'type': 'italic'}]},
                    {'audio': Audio("audio_id", 12),
                     'caption': 'audio_file'},
                    {'document': Document('document_id'),
                     'caption': 'document_file'},
                    {'game': Game('my_game', 'just my game',
                                  [PhotoSize('game_photo_id', 30, 30), ])},
                    {'photo': [PhotoSize('photo_id', 50, 50)],
                     'caption': 'photo_file'},
                    {'sticker': Sticker('sticker_id', 50, 50)},
                    {'video': Video("video_id", 12, 12, 12),
                     'caption': 'video_file'},
                    {'voice': Voice('voice_id', 5)},
                    {'video_note': VideoNote('video_note_id', 20, 12)},
                    {'new_chat_members': [User(55, 'new_user')]},
                    {'contact': Contact('phone_numner', 'contact_name')},
                    {'location': Location(-23.691288, 46.788279)},
                    {'venue': Venue(Location(-23.691288, 46.788279),
                                    'some place', 'right here')},
                    {'left_chat_member': User(33, 'kicked')},
                    {'new_chat_title': 'new title'},
                    {'new_chat_photo': [PhotoSize('photo_id', 50, 50)]},
                    {'delete_chat_photo': True},
                    {'group_chat_created': True},
                    {'supergroup_chat_created': True},
                    {'channel_chat_created': True},
                    {'migrate_to_chat_id': -12345},
                    {'migrate_from_chat_id': -54321},
                    {'pinned_message': Message(7, None, None, None)},
                    {'invoice': Invoice('my invoice', 'invoice', 'start', 'EUR', 243)},
                    {'successful_payment': SuccessfulPayment('EUR', 243, 'payload',
                                                             'charge_id', 'provider_id')}
                ],
                ids=['forwarded_user', 'forwarded_channel', 'reply', 'edited', 'text', 'audio',
                     'document', 'game', 'photo', 'sticker', 'video', 'voice', 'video_note',
                     'new_members', 'contact', 'location', 'venue', 'left_member', 'new_title',
                     'new_photo', 'delete_photo', 'group_created', 'supergroup_created',
                     'channel_created', 'migrated_to', 'migrated_from', 'pinned', 'invoice',
                     'successful_payment'])
def message_params(bot, request):
    return Message(message_id=TestMessage.id,
                   from_user=TestMessage.from_user,
                   date=TestMessage.date,
                   chat=TestMessage.chat, bot=bot, **request.param)


class TestMessage:
    """This object represents Tests for Telegram MessageTest."""
    id = 1
    from_user = User(2, 'testuser')
    date = datetime.now()
    chat = Chat(3, 'private')
    test_entities = [{'length': 4, 'offset': 10, 'type': 'bold'},
                     {'length': 7, 'offset': 16, 'type': 'italic'},
                     {'length': 4, 'offset': 25, 'type': 'code'},
                     {'length': 5, 'offset': 31, 'type': 'text_link', 'url': 'http://github.com/'},
                     {'length': 3, 'offset': 41, 'type': 'pre'}, ]
    test_text = 'Test for <bold, ita_lic, code, links and pre.'
    test_message = Message(message_id=1,
                           from_user=None,
                           date=None,
                           chat=None,
                           text=test_text,
                           entities=[MessageEntity(**e) for e in test_entities])

    def test_all_posibilities_de_json_and_to_dict(self, bot, message_params):
        new = Message.de_json(message_params.to_dict(), bot)
        new.to_dict() == message_params.to_dict()

    def test_parse_entity(self):
        text = (b'\\U0001f469\\u200d\\U0001f469\\u200d\\U0001f467'
                b'\\u200d\\U0001f467\\U0001f431http://google.com').decode('unicode-escape')
        entity = MessageEntity(type=MessageEntity.URL, offset=13, length=17)
        message = Message(
            message_id=1, from_user=None, date=None, chat=None, text=text, entities=[entity])
        assert message.parse_entity(entity) == 'http://google.com'

    def test_parse_entities(self):
        text = (b'\\U0001f469\\u200d\\U0001f469\\u200d\\U0001f467'
                b'\\u200d\\U0001f467\\U0001f431http://google.com').decode('unicode-escape')
        entity = MessageEntity(type=MessageEntity.URL, offset=13, length=17)
        entity_2 = MessageEntity(type=MessageEntity.BOLD, offset=13, length=1)
        message = Message(
            message_id=1,
            from_user=None,
            date=None,
            chat=None,
            text=text,
            entities=[entity_2, entity])
        assert message.parse_entities(MessageEntity.URL) == {entity: 'http://google.com'}
        assert message.parse_entities() == {entity: 'http://google.com', entity_2: 'h'}

    def test_text_html_simple(self):
        test_html_string = 'Test for &lt;<b>bold</b>, <i>ita_lic</i>, <code>code</code>, ' \
                           '<a href="http://github.com/">links</a> and <pre>pre</pre>.'
        text_html = self.test_message.text_html
        assert test_html_string == text_html

    def test_text_markdown_simple(self):
        test_md_string = 'Test for <*bold*, _ita\_lic_, `code`, [links](http://github.com/) and ' \
                         '```pre```.'
        text_markdown = self.test_message.text_markdown
        assert test_md_string == text_markdown

    def test_text_html_emoji(self):
        text = (b'\\U0001f469\\u200d\\U0001f469\\u200d ABC').decode('unicode-escape')
        expected = (b'\\U0001f469\\u200d\\U0001f469\\u200d <b>ABC</b>').decode('unicode-escape')
        bold_entity = MessageEntity(type=MessageEntity.BOLD, offset=7, length=3)
        message = Message(
            message_id=1, from_user=None, date=None, chat=None, text=text, entities=[bold_entity])
        assert expected == message.text_html

    def test_text_markdown_emoji(self):
        text = (b'\\U0001f469\\u200d\\U0001f469\\u200d ABC').decode('unicode-escape')
        expected = (b'\\U0001f469\\u200d\\U0001f469\\u200d *ABC*').decode('unicode-escape')
        bold_entity = MessageEntity(type=MessageEntity.BOLD, offset=7, length=3)
        message = Message(
            message_id=1, from_user=None, date=None, chat=None, text=text, entities=[bold_entity])
        assert expected == message.text_markdown

    def test_parse_entities_url_emoji(self):
        url = b'http://github.com/?unicode=\\u2713\\U0001f469'.decode('unicode-escape')
        text = 'some url'
        link_entity = MessageEntity(type=MessageEntity.URL, offset=0, length=8, url=url)
        message = Message(
            message_id=1,
            from_user=None,
            date=None,
            chat=None,
            text=text,
            entities=[link_entity])
        assert message.parse_entities() == {link_entity: text}
        assert next(iter(message.parse_entities())).url == url

    def test_chat_id(self, message):
        assert message.chat_id == message.chat.id

    def test_reply_text(self, monkeypatch, message):
        def test(*args, **kwargs):
            id = args[1] == message.chat_id
            text = args[2] == 'test'
            if kwargs.get('reply_to_message_id'):
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id and text and reply

        monkeypatch.setattr('telegram.Bot.send_message', test)
        assert message.reply_text('test')
        assert message.reply_text('test', quote=True)

    def test_reply_photo(self, monkeypatch, message):
        def test(*args, **kwargs):
            id = args[1] == message.chat_id
            photo = kwargs['photo'] == 'test_photo'
            if kwargs.get('reply_to_message_id'):
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id and photo and reply

        monkeypatch.setattr('telegram.Bot.send_photo', test)
        assert message.reply_photo(photo="test_photo")
        assert message.reply_photo(photo="test_photo", quote=True)

    def test_reply_audio(self, monkeypatch, message):
        def test(*args, **kwargs):
            id = args[1] == message.chat_id
            audio = kwargs['audio'] == 'test_audio'
            if kwargs.get('reply_to_message_id'):
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id and audio and reply

        monkeypatch.setattr('telegram.Bot.send_audio', test)
        assert message.reply_audio(audio="test_audio")
        assert message.reply_audio(audio="test_audio", quote=True)

    def test_reply_document(self, monkeypatch, message):
        def test(*args, **kwargs):
            id = args[1] == message.chat_id
            document = kwargs['document'] == 'test_document'
            if kwargs.get('reply_to_message_id'):
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id and document and reply

        monkeypatch.setattr('telegram.Bot.send_document', test)
        assert message.reply_document(document="test_document")
        assert message.reply_document(document="test_document", quote=True)

    def test_reply_sticker(self, monkeypatch, message):
        def test(*args, **kwargs):
            id = args[1] == message.chat_id
            sticker = kwargs['sticker'] == 'test_sticker'
            if kwargs.get('reply_to_message_id'):
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id and sticker and reply

        monkeypatch.setattr('telegram.Bot.send_sticker', test)
        assert message.reply_sticker(sticker="test_sticker")
        assert message.reply_sticker(sticker="test_sticker", quote=True)

    def test_reply_video(self, monkeypatch, message):
        def test(*args, **kwargs):
            id = args[1] == message.chat_id
            video = kwargs['video'] == 'test_video'
            if kwargs.get('reply_to_message_id'):
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id and video and reply

        monkeypatch.setattr('telegram.Bot.send_video', test)
        assert message.reply_video(video="test_video")
        assert message.reply_video(video="test_video", quote=True)

    def test_reply_video_note(self, monkeypatch, message):
        def test(*args, **kwargs):
            id = args[1] == message.chat_id
            video_note = kwargs['video_note'] == 'test_video_note'
            if kwargs.get('reply_to_message_id'):
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id and video_note and reply

        monkeypatch.setattr('telegram.Bot.send_video_note', test)
        assert message.reply_video_note(video_note="test_video_note")
        assert message.reply_video_note(video_note="test_video_note", quote=True)

    def test_reply_voice(self, monkeypatch, message):
        def test(*args, **kwargs):
            id = args[1] == message.chat_id
            voice = kwargs['voice'] == 'test_voice'
            if kwargs.get('reply_to_message_id'):
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id and voice and reply

        monkeypatch.setattr('telegram.Bot.send_voice', test)
        assert message.reply_voice(voice="test_voice")
        assert message.reply_voice(voice="test_voice", quote=True)

    def test_reply_location(self, monkeypatch, message):
        def test(*args, **kwargs):
            id = args[1] == message.chat_id
            location = kwargs['location'] == 'test_location'
            if kwargs.get('reply_to_message_id'):
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id and location and reply

        monkeypatch.setattr('telegram.Bot.send_location', test)
        assert message.reply_location(location="test_location")
        assert message.reply_location(location="test_location", quote=True)

    def test_reply_venue(self, monkeypatch, message):
        def test(*args, **kwargs):
            id = args[1] == message.chat_id
            venue = kwargs['venue'] == 'test_venue'
            if kwargs.get('reply_to_message_id'):
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id and venue and reply

        monkeypatch.setattr('telegram.Bot.send_venue', test)
        assert message.reply_venue(venue="test_venue")
        assert message.reply_venue(venue="test_venue", quote=True)

    def test_reply_contact(self, monkeypatch, message):
        def test(*args, **kwargs):
            id = args[1] == message.chat_id
            contact = kwargs['contact'] == 'test_contact'
            if kwargs.get('reply_to_message_id'):
                reply = kwargs['reply_to_message_id'] == message.message_id
            else:
                reply = True
            return id and contact and reply

        monkeypatch.setattr('telegram.Bot.send_contact', test)
        assert message.reply_contact(contact="test_contact")
        assert message.reply_contact(contact="test_contact", quote=True)

    def test_forward(self, monkeypatch, message):
        def test(*args, **kwargs):
            chat_id = kwargs['chat_id'] == 123456
            from_chat = kwargs['from_chat_id'] == message.chat_id
            message_id = kwargs['message_id'] == message.message_id
            if kwargs.get('disable_notification'):
                notification = kwargs['disable_notification'] is True
            else:
                notification = True
            return chat_id and from_chat and message_id and notification

        monkeypatch.setattr('telegram.Bot.forward_message', test)
        assert message.forward(123456)
        assert message.forward(123456, disable_notification=True)
        assert not message.forward(635241)

    def test_edit_text(self, monkeypatch, message):
        def test(*args, **kwargs):
            chat_id = kwargs['chat_id'] == message.chat_id
            message_id = kwargs['message_id'] == message.message_id
            text = kwargs['text'] == 'test'
            return chat_id and message_id and text

        monkeypatch.setattr('telegram.Bot.edit_message_text', test)
        assert message.edit_text(text="test")

    def test_edit_caption(self, monkeypatch, message):
        def test(*args, **kwargs):
            chat_id = kwargs['chat_id'] == message.chat_id
            message_id = kwargs['message_id'] == message.message_id
            caption = kwargs['caption'] == 'new caption'
            return chat_id and message_id and caption

        monkeypatch.setattr('telegram.Bot.edit_message_caption', test)
        assert message.edit_caption(caption='new caption')

    def test_edit_reply_markup(self, monkeypatch, message):
        def test(*args, **kwargs):
            chat_id = kwargs['chat_id'] == message.chat_id
            message_id = kwargs['message_id'] == message.message_id
            reply_markup = kwargs['reply_markup'] == [["1", "2"]]
            return chat_id and message_id and reply_markup

        monkeypatch.setattr('telegram.Bot.edit_message_reply_markup', test)
        assert message.edit_reply_markup(reply_markup=[["1", "2"]])

    def test_delete(self, monkeypatch, message):
        def test(*args, **kwargs):
            chat_id = kwargs['chat_id'] == message.chat_id
            message_id = kwargs['message_id'] == message.message_id
            return chat_id and message_id

        monkeypatch.setattr('telegram.Bot.delete_message', test)
        assert message.delete()

    # todo: add the shortcut method tests monkeypatched

    def test_equality(self):
        _id = 1
        a = Message(_id, User(1, ""), None, None)
        b = Message(_id, User(1, ""), None, None)
        c = Message(_id, User(0, ""), None, None)
        d = Message(0, User(1, ""), None, None)
        e = Update(_id)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)