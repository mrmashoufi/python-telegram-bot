import os
import pytest
from flaky import flaky

from telegram import Audio, TelegramError, Voice


@pytest.fixture(scope="function")
def audio_file():
    f = open('tests/data/telegram.mp3', 'rb')
    yield f
    f.close()

@pytest.fixture(scope="class")
def audio(bot, chat_id):
    return bot.send_audio(chat_id, audio=open('tests/data/telegram.mp3', 'rb'), timeout=10).audio

@pytest.fixture(scope="function")
def json_dict(audio):
    return {
        'file_id': audio.file_id,
        'duration': audio.duration,
        'performer': TestAudio.performer,
        'title': TestAudio.title,
        'caption': TestAudio.caption,
        'mime_type': audio.mime_type,
        'file_size': audio.file_size
    }

class TestAudio:
    """This object represents Tests for Telegram Audio."""

    caption = "Test audio"
    performer = 'Leandro Toledo'
    title = 'Teste'
    # audio_file_url = 'https://python-telegram-bot.org/static/testfiles/telegram.mp3'
    # Shortened link, the above one is cached with the wrong duration.
    audio_file_url = "https://goo.gl/3En24v"

    @classmethod
    def test_creation(self, audio):
        # Make sure file has been uploaded.
        assert isinstance(audio, Audio)
        assert isinstance(audio.file_id, str)
        assert audio.file_id is not ''

    def test_expected_values(self, audio):
        assert audio.duration == 3
        assert audio.performer == None
        assert audio.title is None
        assert audio.mime_type == 'audio/mpeg'
        assert audio.file_size == 122920

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_audio_all_args(self, bot, chat_id, audio_file, audio):
        message = bot.send_audio(chat_id, audio=audio_file, caption=self.caption, duration=audio.duration, performer=self.performer, title=self.title, disable_notification=False)

        assert message.caption == self.caption

        sentaudio = message.audio

        assert isinstance(sentaudio, Audio)
        assert isinstance(sentaudio.file_id, str)
        assert sentaudio.file_id is not None
        assert sentaudio.duration == audio.duration
        assert sentaudio.performer == self.performer
        assert sentaudio.title == self.title
        assert sentaudio.mime_type == audio.mime_type
        assert sentaudio.file_size == audio.file_size

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
        sentaudio = message.audio

        assert isinstance(sentaudio, Audio)
        assert isinstance(sentaudio.file_id, str)
        assert sentaudio.file_id is not None
        assert sentaudio.duration == audio.duration
        assert sentaudio.mime_type == audio.mime_type
        assert sentaudio.file_size == audio.file_size

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_audio_resend(self, bot, chat_id, audio):
        message = bot.send_audio(chat_id=chat_id, audio=audio.file_id)
        sentaudio = message.audio

        assert sentaudio == audio

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_send_audio_with_audio(self, bot, chat_id, audio):
        message = bot.send_audio(audio=audio, chat_id=chat_id)
        sentaudio = message.audio

        assert sentaudio == audio

    def test_audio_de_json(self, json_dict, bot, audio):
        newaudio = Audio.de_json(json_dict, bot)

        assert isinstance(newaudio, Audio)
        assert newaudio.file_id==audio.file_id
        assert newaudio.duration== audio.duration
        assert newaudio.performer== self.performer
        assert newaudio.title== self.title
        assert newaudio.mime_type== audio.mime_type
        assert newaudio.file_size== audio.file_size

    def test_audio_to_json(self, is_json, audio):
        assert is_json(audio.to_json())

    def test_audio_to_dict(self, is_dict, audio):
        newaudio = audio.to_dict()

        assert is_dict(newaudio)
        assert newaudio['file_id']== audio.file_id
        assert newaudio['duration'] == audio.duration
        assert newaudio['mime_type'] == audio.mime_type
        assert newaudio['file_size'] == audio.file_size

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
    def test_error_audio_without_required_args(self, bot, chat_id, json_dict):
        del(json_dict['file_id'])
        del(json_dict['duration'])

        with pytest.raises(TypeError):
            bot.send_audio(chat_id=chat_id, **json_dict)

    @flaky(3, 1)
    @pytest.mark.timeout(10)
    def test_reply_audio(self, bot, chat_id, audio_file):
        message = bot.send_message(chat_id, '.')
        audio = message.reply_audio(audio_file).audio

        assert isinstance(audio, Audio)
        assert isinstance(audio.file_id, str)
        assert audio.file_id is not None

    def test_equality(self, audio):
        a = Audio(audio.file_id, audio.duration)
        b = Audio(audio.file_id, audio.duration)
        c = Audio(audio.file_id, 0)
        d = Audio("", audio.duration)
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