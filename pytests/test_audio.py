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
import json
import os

import pytest
from flaky import flaky

from telegram import Audio, TelegramError, Voice


@pytest.fixture()
def audio_file():
    f = open('tests/data/telegram.mp3', 'rb')
    yield f
    f.close()


@pytest.fixture(scope='class')
def audio(bot, chat_id):
    with open('tests/data/telegram.mp3', 'rb') as f:
        return bot.send_audio(chat_id, audio=f, timeout=10).audio


class TestAudio:
    """This object represents Tests for Telegram Audio."""

    caption = 'Test audio'
    performer = 'Leandro Toledo'
    title = 'Teste'
    # audio_file_url = 'https://python-telegram-bot.org/static/testfiles/telegram.mp3'
    # Shortened link, the above one is cached with the wrong duration.
    audio_file_url = 'https://goo.gl/3En24v'

    @staticmethod
    def test_creation(audio):
        # Make sure file has been uploaded.
        assert isinstance(audio, Audio)
        assert isinstance(audio.file_id, str)
        assert audio.file_id is not ''

    def test_expected_values(self, audio):
        assert audio.duration == 3
        assert audio.performer is None
        assert audio.title is None
        assert audio.mime_type == 'audio/mpeg'
        assert audio.file_size == 122920

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_audio_all_args(self, bot, chat_id, audio_file, audio):
        message = bot.send_audio(chat_id, audio=audio_file, caption=self.caption,
                                 duration=audio.duration, performer=self.performer,
                                 title=self.title, disable_notification=False)

        assert message.caption == self.caption

        assert isinstance(message.audio, Audio)
        assert isinstance(message.audio.file_id, str)
        assert message.audio.file_id is not None
        assert message.audio.duration == audio.duration
        assert message.audio.performer == self.performer
        assert message.audio.title == self.title
        assert message.audio.mime_type == audio.mime_type
        assert message.audio.file_size == audio.file_size

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_get_and_download_audio(self, bot, audio):
        new_file = bot.get_file(audio.file_id)

        assert new_file.file_size == audio.file_size
        assert new_file.file_id == audio.file_id
        assert new_file.file_path.startswith('https://')

        new_file.download('telegram.mp3')

        assert os.path.isfile('telegram.mp3')

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_audio_mp3_url_file(self, bot, chat_id, audio):
        message = bot.send_audio(chat_id=chat_id, audio=self.audio_file_url, caption=self.caption)

        assert message.caption == self.caption

        assert isinstance(message.audio, Audio)
        assert isinstance(message.audio.file_id, str)
        assert message.audio.file_id is not None
        assert message.audio.duration == audio.duration
        assert message.audio.mime_type == audio.mime_type
        assert message.audio.file_size == audio.file_size

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_audio_resend(self, bot, chat_id, audio):
        message = bot.send_audio(chat_id=chat_id, audio=audio.file_id)

        assert message.audio == audio

    def test_send_audio_with_audio(self, monkeypatch, bot, chat_id, audio):
        def test(_, url, data, **kwargs):
            return data['audio'] == audio.file_id

        monkeypatch.setattr("telegram.utils.request.Request.post", test)
        message = bot.send_audio(audio=audio, chat_id=chat_id)
        assert message

    def test_audio_de_json(self, bot, audio):
        json_audio = Audio.de_json({'file_id': audio.file_id, 'duration': audio.duration,
                                    'performer': TestAudio.performer, 'title': TestAudio.title,
                                    'caption': TestAudio.caption, 'mime_type': audio.mime_type,
                                    'file_size': audio.file_size},
                                   bot)

        assert json_audio.file_id == audio.file_id
        assert json_audio.duration == audio.duration
        assert json_audio.performer == self.performer
        assert json_audio.title == self.title
        assert json_audio.mime_type == audio.mime_type
        assert json_audio.file_size == audio.file_size

    def test_audio_to_json(self, audio):
        json.loads(audio.to_json())

    def test_audio_to_dict(self, audio):
        audio_dict = audio.to_dict()

        assert isinstance(audio_dict, dict)
        assert audio_dict['file_id'] == audio.file_id
        assert audio_dict['duration'] == audio.duration
        assert audio_dict['mime_type'] == audio.mime_type
        assert audio_dict['file_size'] == audio.file_size

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_error_send_audio_empty_file(self, bot, chat_id):
        audio_file = open(os.devnull, 'rb')

        with pytest.raises(TelegramError):
            bot.send_audio(chat_id=chat_id, audio=audio_file)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_error_send_audio_empty_file_id(self, bot, chat_id):
        with pytest.raises(TelegramError):
            bot.send_audio(chat_id=chat_id, audio="")

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_error_audio_without_required_args(self, bot, chat_id):
        with pytest.raises(TypeError):
            bot.send_audio(chat_id=chat_id)

    def test_equality(self, audio):
        a = Audio(audio.file_id, audio.duration)
        b = Audio(audio.file_id, audio.duration)
        c = Audio(audio.file_id, 0)
        d = Audio('', audio.duration)
        e = Voice(audio.file_id, audio.duration)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)
