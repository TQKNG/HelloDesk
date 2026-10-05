from app.core.logging import REDACTED, redact_value


def test_log_redaction_removes_nested_audio_transcript_and_credentials() -> None:
    logged = redact_value(
        {
            "sessionToken": "guest-token",
            "request": {
                "audio_payload": "raw-audio",
                "inputTranscript": "guest full transcript",
                "provider_reference": "provider-id",
                "api_key": "server-secret",
                "safe_status": "ok",
            },
        }
    )

    assert logged == {
        "sessionToken": REDACTED,
        "request": {
            "audio_payload": REDACTED,
            "inputTranscript": REDACTED,
            "provider_reference": REDACTED,
            "api_key": REDACTED,
            "safe_status": "ok",
        },
    }


def test_log_redaction_recurses_through_arrays() -> None:
    assert redact_value([{"authorization": "Bearer secret"}]) == [{"authorization": REDACTED}]
