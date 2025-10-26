from __future__ import annotations

import json
import logging
from typing import Any, Tuple

from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from fastapi.routing import APIRoute
from fastapi.utils import DefaultPlaceholder
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.schemas.common import StandardResponse

logger = logging.getLogger(__name__)

DEFAULT_SUCCESS_MESSAGE = "berhasil"
DEFAULT_ERROR_MESSAGE = "Terjadi kesalahan"


def build_response_content(
    *,
    success: bool,
    message: str,
    status_code: int,
    data: Any = None,
) -> dict[str, Any]:
    return {
        "success": success,
        "message": message,
        "data": jsonable_encoder(data),
        "statusCode": status_code,
    }


def extract_error_detail(detail: Any) -> Tuple[str, Any]:
    if isinstance(detail, dict):
        message = detail.get("message") or detail.get("detail")
        data = detail.get("data")
        if data is None:
            remaining = {
                key: value
                for key, value in detail.items()
                if key not in {"message", "detail"}
            }
            data = remaining or None
        return str(message or DEFAULT_ERROR_MESSAGE), data
    if isinstance(detail, list):
        return DEFAULT_ERROR_MESSAGE, detail
    if detail:
        return str(detail), None
    return DEFAULT_ERROR_MESSAGE, None


class EnvelopeAPIRoute(APIRoute):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        response_model = kwargs.get("response_model")
        self.original_response_model = response_model

        if response_model is None or isinstance(response_model, DefaultPlaceholder):
            kwargs["response_model"] = StandardResponse[Any]
        else:
            origin = getattr(response_model, "__origin__", None)
            if origin is StandardResponse:
                kwargs["response_model"] = response_model
            else:
                kwargs["response_model"] = StandardResponse[response_model]  # type: ignore[index]

        super().__init__(*args, **kwargs)

    def get_route_handler(self):
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                response = await original_route_handler(request)
            except StarletteHTTPException as exc:
                message, data = extract_error_detail(exc.detail)
                headers = exc.headers or None
                content = build_response_content(
                    success=False,
                    message=message,
                    status_code=exc.status_code,
                    data=data,
                )
                return JSONResponse(
                    status_code=exc.status_code,
                    content=content,
                    headers=headers,
                )
            if not isinstance(response, Response):
                content = build_response_content(
                    success=True,
                    message=DEFAULT_SUCCESS_MESSAGE,
                    status_code=status.HTTP_200_OK,
                    data=response,
                )
                return JSONResponse(status_code=status.HTTP_200_OK, content=content)

            if response.status_code >= 400:
                return response

            if response.media_type != "application/json":
                return response

            try:
                body_bytes = response.body
            except (AttributeError, RuntimeError):
                return response
            if not body_bytes:
                payload: Any = None
            else:
                try:
                    payload = json.loads(body_bytes.decode(response.charset or "utf-8"))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    payload = body_bytes.decode(response.charset or "utf-8")

            if isinstance(payload, dict) and {
                "success",
                "message",
                "statusCode",
            }.issubset(payload):
                return response

            message = DEFAULT_SUCCESS_MESSAGE
            data = payload

            if isinstance(payload, dict):
                if "success" in payload and "message" in payload:
                    message = str(payload["message"])
                    data = payload.get("data")
                else:
                    pesan = payload.pop("pesan", None)
                    message = str(payload.pop("message", pesan or DEFAULT_SUCCESS_MESSAGE))
                    payload.pop("statusCode", None)
                    if "data" in payload and len(payload) == 1:
                        data = payload.get("data")
                    elif "data" in payload and len(payload) > 1:
                        data = payload
                    else:
                        data = payload or None

            wrapped_content = build_response_content(
                success=True,
                message=message,
                status_code=response.status_code,
                data=data,
            )

            headers = {
                key: value
                for key, value in response.headers.items()
                if key.lower() != "content-length"
            }

            wrapped_response = JSONResponse(
                status_code=response.status_code,
                content=wrapped_content,
                headers=headers,
                background=response.background,
            )

            return wrapped_response

        return custom_route_handler


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    message, data = extract_error_detail(exc.detail)
    content = build_response_content(
        success=False,
        message=message,
        status_code=exc.status_code,
        data=data,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=content,
        headers=exc.headers or None,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    content = build_response_content(
        success=False,
        message="Validasi gagal",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        data=exc.errors(),
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=content,
    )


async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    logger.exception("Unhandled error during request", exc_info=exc)
    content = build_response_content(
        success=False,
        message=DEFAULT_ERROR_MESSAGE,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        data=None,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=content,
    )
