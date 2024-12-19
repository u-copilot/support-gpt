"""This file should be imported only and only if you want to run the UI locally."""
import os
import sys

import itertools
import logging
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import gradio as gr  # type: ignore
from fastapi import FastAPI
from gradio.themes.utils.colors import slate  # type: ignore
from injector import inject, singleton
from llama_index.llms import ChatMessage, ChatResponse, MessageRole
from pydantic import BaseModel

from u_copilot.constants import PROJECT_ROOT_PATH
from u_copilot.di import global_injector
from u_copilot.server.chat.chat_service import ChatService, CompletionGen
from u_copilot.server.chunks.chunks_service import Chunk, ChunksService
from u_copilot.server.ingest.ingest_service import IngestService
from u_copilot.server.psql import chat_manager
from u_copilot.settings.settings import settings
from u_copilot.ui.images import logo_svg

import json

logger = logging.getLogger(__name__)

THIS_DIRECTORY_RELATIVE = Path(__file__).parent.relative_to(PROJECT_ROOT_PATH)
# Should be "u_copilot/ui/avatar-bot.ico"
AVATAR_BOT = THIS_DIRECTORY_RELATIVE / "avatar-bot.ico"

UI_TAB_TITLE = "My Private GPT"

SOURCES_SEPARATOR = "\n\n Sources: \n"

MODES = ["Query Docs", "Search in Docs", "LLM Chat"]


class Source(BaseModel):
    file: str
    page: str
    text: str

    class Config:
        frozen = True

    @staticmethod
    def curate_sources(sources: list[Chunk]) -> set["Source"]:
        curated_sources = set()

        for chunk in sources:
            doc_metadata = chunk.document.doc_metadata

            file_name = doc_metadata.get("file_name", "-") if doc_metadata else "-"
            page_label = doc_metadata.get("page_label", "-") if doc_metadata else "-"

            source = Source(file=file_name, page=page_label, text=chunk.text)
            curated_sources.add(source)

        return curated_sources


@singleton
class UCopilotUi:
    @inject
    def __init__(
        self,
        ingest_service: IngestService,
        chat_service: ChatService,
        chunks_service: ChunksService,
    ) -> None:
        self._ingest_service = ingest_service
        self._chat_service = chat_service
        self._chunks_service = chunks_service

        # Cache the UI blocks
        self._ui_block = None

        # Initialize system prompt based on default mode
        self.mode = MODES[0]
        self._system_prompt = self._get_default_system_prompt(self.mode)

    def _chat(self, message: str, history: list[list[str]], mode: str, *_: Any) -> Any:
        TENANT_ID = os.getenv("PORT", 50055)

        def revert_path(formatted_path):
            # Replace all '__' with '/' in the formatted_path
            if "___" in formatted_path:
                path_marker = "___"
            else:
                path_marker = "__"
            original_path = formatted_path.replace(path_marker, "/")
            print(f"original_path_1={original_path}")
            # Check if the path ends with 'index.html' and remove it
            if original_path.endswith("index.html"):
                # Remove the last part 'index.html' by slicing
                original_path = original_path[
                    :-10
                ]  # 'index.html' is 10 characters long
            elif original_path.endswith(".html"):
                # Remove the last part 'index.html' by slicing
                original_path = original_path[:-5]  # 'index.html' is 10 characters long
            print(f"original_path_2={original_path}")
            return original_path

        def convert_to_valid_url(input_url):
            # Split the input URL into the base part and the file part
            if "@" in input_url:
                return input_url.replace("@", "?")
            else:
                # Return the original if no '@' is present
                return input_url

        def yield_deltas(completion_gen: CompletionGen) -> Iterable[str]:
            full_response: str = ""
            stream = completion_gen.response
            for delta in stream:
                if isinstance(delta, str):
                    full_response += str(delta)
                elif isinstance(delta, ChatResponse):
                    full_response += delta.delta or ""
                yield full_response

            BASE_URL = os.getenv("BASE_URL", "paly.net")
            if completion_gen.sources:
                full_response += SOURCES_SEPARATOR
                cur_sources = Source.curate_sources(completion_gen.sources)
                logger.info(f"cur_sources={cur_sources}")

                sources_text = "\n\n\n".join(
                    f"{index}. <https://{BASE_URL}/{convert_to_valid_url(revert_path(source.file))}>"
                    for index, source in enumerate(cur_sources, start=1)
                )
                print(f"sources_text={sources_text}")

                full_response += sources_text
            yield full_response

        def build_history() -> list[ChatMessage]:
            history_messages: list[ChatMessage] = list(
                itertools.chain(
                    *[
                        [
                            ChatMessage(content=interaction[0], role=MessageRole.USER),
                            ChatMessage(
                                # Remove from history content the Sources information
                                content=interaction[1].split(SOURCES_SEPARATOR)[0],
                                role=MessageRole.ASSISTANT,
                            ),
                        ]
                        for interaction in history
                    ]
                )
            )

            # max 20 messages to try to avoid context overflow
            return history_messages[:20]

        new_message = ChatMessage(content=message, role=MessageRole.USER)
        logger.info(
            f"NEW MESSAGE **** ={new_message}, type of new_message ={type(new_message)}"
        )
        all_messages = [*build_history(), new_message]
        messages_json = json.dumps(all_messages, default=str)
        logger.info(f"**** all_messsages = {messages_json}")
        # ====================================================================
        chat_manager.create_table(TENANT_ID)
        chat_manager.insert_or_update_message(TENANT_ID, message, messages_json)
        # ====================================================================
        # If a system prompt is set, add it as a system message
        if self._system_prompt:
            all_messages.insert(
                0,
                ChatMessage(
                    content=self._system_prompt,
                    role=MessageRole.SYSTEM,
                ),
            )
        match mode:
            case "Query Docs":
                query_stream = self._chat_service.stream_chat(
                    messages=all_messages,
                    use_context=True,
                )
                yield from yield_deltas(query_stream)
            case "LLM Chat":
                llm_stream = self._chat_service.stream_chat(
                    messages=all_messages,
                    use_context=False,
                )
                yield from yield_deltas(llm_stream)

            case "Search in Docs":
                response = self._chunks_service.retrieve_relevant(
                    text=message, limit=4, prev_next_chunks=0
                )

                sources = Source.curate_sources(response)
                print(f"souerces={sources}")

                BASE_URL = os.getenv("BASE_URL", "paly.net")
                yield "\n\n\n".join(
                    f"{index}. <https://{BASE_URL}/{revert_path(source.file)}>\n"
                    f"{source.text}"
                    for index, source in enumerate(sources, start=1)
                )

    # On initialization and on mode change, this function set the system prompt
    # to the default prompt based on the mode (and user settings).
    @staticmethod
    def _get_default_system_prompt(mode: str) -> str:
        p = ""
        match mode:
            # For query chat mode, obtain default system prompt from settings
            case "Query Docs":
                p = settings().ui.default_query_system_prompt
            # For chat mode, obtain default system prompt from settings
            case "LLM Chat":
                p = settings().ui.default_chat_system_prompt
            # For any other mode, clear the system prompt
            case _:
                p = ""
        return p

    def _set_system_prompt(self, system_prompt_input: str) -> None:
        logger.info(f"Setting system prompt to: {system_prompt_input}")
        self._system_prompt = system_prompt_input

    def _set_current_mode(self, mode: str) -> Any:
        self.mode = mode
        self._set_system_prompt(self._get_default_system_prompt(mode))
        # Update placeholder and allow interaction if default system prompt is set
        if self._system_prompt:
            return gr.update(placeholder=self._system_prompt, interactive=True)
        # Update placeholder and disable interaction if no default system prompt is set
        else:
            return gr.update(placeholder=self._system_prompt, interactive=False)

    def _list_ingested_files(self) -> list[list[str]]:
        TENANT_ID = os.getenv("PORT", 50055)
        try:
            # Attempt to retrieve messages from the database
            messages = chat_manager.retrieve_messages(TENANT_ID)
        except Exception as e:
            # Handle the case where the database connection fails
            print(
                f"Error: Unable to connect to the PostgreSQL database. \n Plesae make sure your psql service is started:\n\nbrew services start postgresql\n\n"
            )
            sys.exit(1)

        faq_list = []
        for message in messages:
            print(f"ID: {message[0]}, Text: {message[1]}, Timestamp: {message[2]}")
            faq_list.append([message[1]])

        return faq_list

    def _upload_file(self, files: list[str]) -> None:
        logger.debug("Loading count=%s files", len(files))
        paths = [Path(file) for file in files]
        self._ingest_service.bulk_ingest([(str(path.name), path) for path in paths])

    def _build_ui_blocks(self) -> gr.Blocks:
        logger.debug("Creating the UI blocks")
        with gr.Blocks(
            title=UI_TAB_TITLE,
            theme=gr.themes.Soft(primary_hue=slate),
            css=".logo { "
            "display:flex;"
            "background-color: #C7BAFF;"
            "height: 80px;"
            "border-radius: 8px;"
            "align-content: center;"
            "justify-content: center;"
            "align-items: center;"
            "}"
            ".logo img { height: 25% }"
            ".contain { display: flex !important; flex-direction: column !important; }"
            "#component-0, #component-3, #component-10, #component-8  { height: 100% !important; }"
            "#chatbot { flex-grow: 1 !important; overflow: auto !important;}"
            "#col { height: calc(100vh - 112px - 16px) !important; }",
        ) as blocks:
            with gr.Row():
                gr.HTML(f"<div class='logo'/><img src={logo_svg} alt=UCopilot></div")

            with gr.Row(equal_height=False):
                with gr.Column(scale=3):
                    mode = gr.Radio(
                        MODES,
                        label="Mode",
                        value="Query Docs",
                    )
                    ingested_dataset = gr.List(
                        self._list_ingested_files,
                        headers=["FAQ"],
                        label="Frequenty Asked Questions",
                        interactive=False,
                        render=False,  # Rendered under the button
                    )

                    ingested_dataset.change(
                        self._list_ingested_files,
                        outputs=ingested_dataset,
                    )
                    ingested_dataset.render()

                    system_prompt_input = gr.Textbox(
                        placeholder=self._system_prompt,
                        label="System Prompt",
                        lines=2,
                        interactive=True,
                        render=False,
                    )
                    # When mode changes, set default system prompt
                    mode.change(
                        self._set_current_mode, inputs=mode, outputs=system_prompt_input
                    )
                    # On blur, set system prompt to use in queries
                    system_prompt_input.blur(
                        self._set_system_prompt,
                        inputs=system_prompt_input,
                    )

                with gr.Column(scale=7, elem_id="col"):
                    ORGANIZATION_NAME = os.getenv("ORGANIZATION_NAME", "Palo Alto High School")
                    _ = gr.ChatInterface(
                        self._chat,
                        chatbot=gr.Chatbot(
                            label=f"{ORGANIZATION_NAME}",
                            show_copy_button=True,
                            elem_id="chatbot",
                            render=False,
                            avatar_images=(
                                None,
                                AVATAR_BOT,
                            ),
                        ),
                        # additional_inputs=[mode, upload_button, system_prompt_input],
                        additional_inputs=[mode, system_prompt_input],
                    )
        return blocks

    def get_ui_blocks(self) -> gr.Blocks:
        if self._ui_block is None:
            self._ui_block = self._build_ui_blocks()
        return self._ui_block

    def mount_in_app(self, app: FastAPI, path: str) -> None:
        blocks = self.get_ui_blocks()
        blocks.queue()
        logger.info("Mounting the gradio UI, at path=%s", path)
        gr.mount_gradio_app(app, blocks, path=path)


if __name__ == "__main__":
    ui = global_injector.get(UCopilotUi)
    _blocks = ui.get_ui_blocks()
    _blocks.queue()
    _blocks.launch(debug=False, show_api=False)
