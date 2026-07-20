"""Google Gemini (generativelanguage) API 适配器。"""
from __future__ import annotations

from ..base import Provider
from ..http import post_json
from ..types import ChatRequest, ChatResponse, ImagePart, Message, TextPart, Usage

# Gemini 的角色名：user / model（assistant 映射为 model）；system 走 systemInstruction。
_ROLE_MAP = {"user": "user", "assistant": "model"}


def _parts(msg: Message) -> list[dict]:
    out: list[dict] = []
    for p in msg.parts():
        if isinstance(p, TextPart):
            out.append({"text": p.text})
        elif isinstance(p, ImagePart):
            out.append({"inlineData": {"mimeType": p.mime, "data": p.data}})
    return out


class GeminiProvider(Provider):
    def chat(self, request: ChatRequest) -> ChatResponse:
        cfg = self.config
        model = request.model or cfg.model
        # key 作为 query 参数传递。
        url = f"{cfg.base_url}/models/{model}:generateContent?key={cfg.api_key}"
        headers = {"Content-Type": "application/json"}

        system_txt = "\n".join(
            m.text() for m in request.messages if m.role == "system"
        )
        contents = [
            {"role": _ROLE_MAP.get(m.role, "user"), "parts": _parts(m)}
            for m in request.messages
            if m.role != "system"
        ]
        gen_cfg: dict = {"temperature": request.temperature}
        if request.max_tokens is not None:
            gen_cfg["maxOutputTokens"] = request.max_tokens
        if request.stop:
            gen_cfg["stopSequences"] = request.stop
        body: dict = {"contents": contents, "generationConfig": gen_cfg}
        if system_txt:
            body["systemInstruction"] = {"parts": [{"text": system_txt}]}
        body.update(request.extra)

        data = post_json(url, headers, body)
        cands = data.get("candidates") or [{}]
        parts = (cands[0].get("content") or {}).get("parts") or []
        text = "".join(p.get("text", "") for p in parts)
        u = data.get("usageMetadata") or {}
        usage = Usage(
            prompt_tokens=u.get("promptTokenCount", 0),
            completion_tokens=u.get("candidatesTokenCount", 0),
            total_tokens=u.get("totalTokenCount", 0),
        )
        return ChatResponse(
            text=text,
            model=model,
            provider=self.name,
            usage=usage,
            raw=data,
        )
