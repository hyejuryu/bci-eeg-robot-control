from __future__ import annotations

import argparse
import json
import os
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Protocol

import certifi


TELEGRAM_API_BASE = "https://api.telegram.org"
DEFAULT_TIMEOUT_SEC = 10.0


class NotificationError(RuntimeError):
    pass


@dataclass(frozen=True)
class NotificationResult:
    provider: str
    message_id: int


class Notifier(Protocol):
    def send(self, message: str) -> NotificationResult:
        ...


@dataclass(frozen=True)
class TelegramConfig:
    bot_token: str
    chat_id: str

    @classmethod
    def from_env(cls) -> "TelegramConfig":
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()

        missing = []

        if not bot_token:
            missing.append("TELEGRAM_BOT_TOKEN")

        if not chat_id:
            missing.append("TELEGRAM_CHAT_ID")

        if missing:
            raise NotificationError(
                "Missing required environment variable(s): "
                + ", ".join(missing)
            )

        return cls(
            bot_token=bot_token,
            chat_id=chat_id,
        )


class TelegramNotifier:
    def __init__(
        self,
        config: TelegramConfig,
        *,
        timeout_sec: float = DEFAULT_TIMEOUT_SEC,
    ) -> None:
        self.config = config
        self.timeout_sec = timeout_sec
        self.ssl_context = ssl.create_default_context(
            cafile=certifi.where()
        )

    @classmethod
    def from_env(
        cls,
        *,
        timeout_sec: float = DEFAULT_TIMEOUT_SEC,
    ) -> "TelegramNotifier":
        return cls(
            TelegramConfig.from_env(),
            timeout_sec=timeout_sec,
        )

    def send(self, message: str) -> NotificationResult:
        text = message.strip()

        if not text:
            raise NotificationError(
                "Notification message must not be empty."
            )

        url = (
            f"{TELEGRAM_API_BASE}/"
            f"bot{self.config.bot_token}/sendMessage"
        )

        payload = json.dumps(
            {
                "chat_id": self.config.chat_id,
                "text": text,
            }
        ).encode("utf-8")

        request = urllib.request.Request(
            url=url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=self.timeout_sec,
                context=self.ssl_context,
            ) as response:
                response_body = response.read().decode("utf-8")

        except urllib.error.HTTPError as exc:
            raise NotificationError(
                f"Telegram API returned HTTP {exc.code}."
            ) from exc

        except urllib.error.URLError as exc:
            raise NotificationError(
                f"Telegram API request failed: {exc.reason}"
            ) from exc

        except ssl.SSLError as exc:
            raise NotificationError(
                f"Telegram TLS validation failed: {exc}"
            ) from exc

        try:
            data = json.loads(response_body)
        except json.JSONDecodeError as exc:
            raise NotificationError(
                "Telegram API returned invalid JSON."
            ) from exc

        if data.get("ok") is not True:
            description = data.get(
                "description",
                "Unknown Telegram API error.",
            )
            raise NotificationError(description)

        result = data.get("result")

        if not isinstance(result, dict):
            raise NotificationError(
                "Telegram API response is missing result."
            )

        message_id = result.get("message_id")

        if not isinstance(message_id, int):
            raise NotificationError(
                "Telegram API response is missing message_id."
            )

        return NotificationResult(
            provider="telegram",
            message_id=message_id,
        )


def send_notification(message: str) -> NotificationResult:
    notifier: Notifier = TelegramNotifier.from_env()
    return notifier.send(message)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Send a research-agent notification."
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "--test",
        action="store_true",
        help="Send the Telegram notifier smoke-test message.",
    )

    group.add_argument(
        "--message",
        type=str,
        help="Send a custom notification message.",
    )

    args = parser.parse_args()

    if args.test:
        message = (
            "[BCI Research Agent]\n"
            "Telegram notifier smoke test: PASS candidate"
        )
    else:
        message = args.message

    result = send_notification(message)

    print(
        "NOTIFICATION_SENT "
        f"provider={result.provider} "
        f"message_id={result.message_id}"
    )


if __name__ == "__main__":
    main()