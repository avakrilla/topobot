from __future__ import annotations

from dataclasses import dataclass
from typing import Awaitable, Callable, Optional

from aiogram import types


AfterFeedbackHook = Callable[[], Awaitable[None]]
CompletionCheck = Callable[[int], bool]
OnFinishHandler = Callable[[], Awaitable[None]]
NextQuestionHandler = Callable[[], Awaitable[None]]
SendFunction = Callable[..., Awaitable]


async def default_send(sender: Callable[..., Awaitable], *args, **kwargs):
    return await sender(*args, **kwargs)


@dataclass
class AnswerContext:
    callback: types.CallbackQuery
    user_id: int
    message_id: Optional[int]
    chat_id: Optional[int]
    send_func: Optional[SendFunction] = None
    remove_keyboard_func: Optional[SendFunction] = None

    async def send(self, sender: Callable[..., Awaitable], *args, **kwargs):
        sender_func = self.send_func or default_send
        return await sender_func(sender, *args, **kwargs)

    async def remove_processing_keyboard(self):
        if not self.message_id:
            return

        remover = self.remove_keyboard_func or self.callback.bot.edit_message_reply_markup
        await remover(
            chat_id=self.chat_id or self.callback.message.chat.id,
            message_id=self.message_id,
            reply_markup=None
        )


class AnswerHelper:
    def __init__(
        self,
        context: AnswerContext,
        confirm_text: str,
        feedback_text: str,
        after_feedback: Optional[AfterFeedbackHook],
        completion_check: CompletionCheck,
        on_finish: OnFinishHandler,
        on_next_question: NextQuestionHandler,
    ):
        self.context = context
        self.confirm_text = confirm_text
        self.feedback_text = feedback_text
        self.after_feedback = after_feedback
        self.completion_check = completion_check
        self.on_finish = on_finish
        self.on_next_question = on_next_question

    async def process(self):
        await self.context.send(self.context.callback.message.answer, self.confirm_text)
        await self.context.send(self.context.callback.message.answer, self.feedback_text)

        if self.after_feedback:
            await self.after_feedback()

        await self.context.remove_processing_keyboard()

        if self.completion_check(self.context.user_id):
            await self.on_finish()
        else:
            await self.on_next_question()

