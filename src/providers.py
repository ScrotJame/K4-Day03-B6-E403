"""
🔌 MULTI-PROVIDER LLM ADAPTER (OpenAI, Gemini, Anthropic, OpenRouter & Offline Mock)
Hỗ trợ chuyển đổi linh hoạt giữa các nhà cung cấp AI chỉ bằng cách đổi biến môi trường LLM_PROVIDER.
"""

import os
import re
import sys
import json
import requests
from dotenv import load_dotenv

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

class BaseLLMProvider:
    """Interface cơ sở cho tất cả các LLM Provider"""
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError


class GeminiProvider(BaseLLMProvider):
    """Google Gemini Provider"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        # "gemini-flash-latest" là alias ổn định của Google, tự trỏ tới bản flash mới nhất
        # còn được cấp quyền cho API key hiện tại (tránh lỗi 404 khi model cụ thể bị deprecate).
        self.model_name = model or os.getenv("LLM_MODEL") or "gemini-flash-latest"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            return "[Gemini Error]: Chưa cấu hình GEMINI_API_KEY trong file .env!"
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            contents = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = client.models.generate_content(
                model=self.model_name,
                contents=contents
            )
            return response.text
        except Exception as e:
            return f"[Gemini Exception]: {str(e)}"


class OpenAIProvider(BaseLLMProvider):
    """OpenAI Provider (GPT-4o, GPT-3.5-turbo, etc.)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "gpt-4o-mini"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            return "[OpenAI Error]: Chưa cấu hình OPENAI_API_KEY trong file .env!"
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[OpenAI Exception]: {str(e)}"


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude Provider (Claude 3.5 Sonnet, Claude 3 Haiku)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "claude-3-haiku-20240307"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_anthropic_api_key_here":
            return "[Anthropic Error]: Chưa cấu hình ANTHROPIC_API_KEY trong file .env!"
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            kwargs = {
                "model": self.model_name,
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            }
            if system_prompt:
                kwargs["system"] = system_prompt
                
            response = client.messages.create(**kwargs)
            return response.content[0].text
        except Exception as e:
            return f"[Anthropic Exception]: {str(e)}"


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter Provider (Hỗ trợ gọi mọi model qua OpenRouter API)"""
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model_name = model or os.getenv("LLM_MODEL") or "google/gemini-2.5-flash"
        
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key or self.api_key == "your_openrouter_api_key_here":
            return "[OpenRouter Error]: Chưa cấu hình OPENROUTER_API_KEY trong file .env!"
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model_name,
                "messages": messages
            }
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=30)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"]
            else:
                return f"[OpenRouter API Error {res.status_code}]: {res.text}"
        except Exception as e:
            return f"[OpenRouter Exception]: {str(e)}"


class MockProvider(BaseLLMProvider):
    """Offline Mock Provider (Cho bài test không cần kết nối API, không tốn quota).

    Là một "rule-based bot" đơn giản (Cấp 1 trong 4 cấp độ AI ở README) tự mô phỏng
    luồng Thought -> Action -> Final Answer cho domain nhà trọ bằng cách đọc chính
    scratchpad đang lớn dần, để test được vòng lặp ReAct thật trong app.py mà không
    cần gọi LLM thật. Chỉ nhận diện đúng 5 test case trong config/test_cases.json,
    không phải LLM tổng quát.
    """

    KNOWN_LOCATIONS = ["Cầu Giấy", "Nam Từ Liêm", "Thanh Xuân"]

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if "ReAct Agent" in system_prompt and "Action:" in system_prompt:
            return self._react_step(prompt)
        return self._baseline_answer(prompt)

    def _baseline_answer(self, prompt: str) -> str:
        text_lower = prompt.lower()
        if any(kw in text_lower for kw in ("đặt lịch", "mã phòng", "còn trống", "tìm phòng")):
            return (
                "[Mock Baseline] Mình là trợ lý tư vấn kiến thức chung, không thể tra cứu tin "
                "đăng thực tế hay đặt lịch xem nhà thật ở chế độ này. Bạn nên hỏi kỹ chủ nhà về "
                "giá, tiền cọc, chi phí điện nước trước khi ký hợp đồng nhé."
            )
        return (
            "[Mock Baseline] Khi thuê phòng trọ, bạn nên ưu tiên vị trí gần trường, tổng chi phí "
            "phù hợp ngân sách, và đảm bảo an ninh, môi trường sống tốt. Nên đọc kỹ hợp đồng và "
            "xác minh thông tin chủ nhà trước khi đặt cọc."
        )

    def _react_step(self, scratchpad: str) -> str:
        budget_match = re.search(r"(-?\d+(?:[.,]\d+)?)\s*(?:triệu|tr\b)", scratchpad, re.IGNORECASE)
        budget = None
        if budget_match:
            budget = int(float(budget_match.group(1).replace(",", ".")) * 1_000_000)

        # Ngân sách âm -> từ chối ngay, không gọi tool (mô phỏng đúng Guardrail)
        if budget is not None and budget <= 0 and "Observation:" not in scratchpad:
            return (
                f"Thought: Ngân sách người dùng đưa ra ({budget:,} VNĐ) không hợp lệ, phải lớn hơn 0.\n"
                "Final Answer: Ngân sách bạn đưa ra không hợp lệ (phải lớn hơn 0). Bạn vui lòng "
                "cung cấp lại mức ngân sách hợp lệ để tôi hỗ trợ tìm phòng nhé!"
            )

        # Câu hỏi lý thuyết chung, không cần tool
        needs_tool = any(
            kw in scratchpad.lower()
            for kw in ("tìm phòng", "cầu giấy", "nam từ liêm", "thanh xuân", "đặt lịch")
        )
        if not needs_tool:
            return (
                "Thought: Đây là câu hỏi tư vấn kiến thức chung, không cần tra cứu dữ liệu thời "
                "gian thực nên không cần gọi tool.\n"
                "Final Answer: [Mock] Bạn nên ưu tiên vị trí gần trường, ngân sách phù hợp, và "
                "kiểm tra kỹ hợp đồng/an ninh trước khi thuê phòng."
            )

        location = next(
            (loc for loc in self.KNOWN_LOCATIONS if loc.lower() in scratchpad.lower()), "Cầu Giấy"
        )
        n_observations = scratchpad.count("Observation:")

        if n_observations == 0:
            price = budget if budget and budget > 0 else 5_000_000
            return (
                f"Thought: Cần tìm phòng trọ tại {location} với ngân sách tối đa {price:,} VNĐ.\n"
                f"Action: search_rentals[{location}, {price}, phòng trọ]"
            )

        if n_observations == 1:
            code_match = re.search(r"Mã nhà:\s*(\w+)", scratchpad)
            if not code_match:
                return (
                    "Thought: Không tìm thấy phòng phù hợp với tiêu chí đã cho.\n"
                    "Final Answer: Xin lỗi, hiện chưa có phòng trọ nào phù hợp với yêu cầu của bạn."
                )
            code = code_match.group(1)
            return (
                f"Thought: Đã tìm thấy mã nhà {code}, cần xem chi tiết và khung giờ xem phòng.\n"
                f"Action: get_rental_details[{code}]"
            )

        if n_observations == 2:
            code_match = re.search(r"nhà\s+(\w+):", scratchpad)
            code = code_match.group(1) if code_match else "NT001"
            phone_match = re.search(r"\b0\d{9,10}\b", scratchpad)
            date_match = re.search(r"\d{4}-\d{2}-\d{2}", scratchpad)
            time_match = re.search(r"lúc\s+(\d{2}:\d{2})", scratchpad, re.IGNORECASE)
            name_match = re.search(r"cho\s+([^,]+?),\s*số điện thoại", scratchpad, re.IGNORECASE)

            if phone_match and date_match and time_match and name_match:
                return (
                    f"Thought: Đã đủ thông tin ngày, giờ, tên và số điện thoại để đặt lịch cho {code}.\n"
                    f"Action: book_viewing[{code}, {date_match.group(0)}, {time_match.group(1)}, "
                    f"{name_match.group(1).strip()}, {phone_match.group(0)}]"
                )
            return (
                f"Thought: Đã có thông tin chi tiết phòng {code} nhưng chưa đủ thông tin đặt lịch.\n"
                f"Final Answer: Tôi đã tìm thấy phòng {code} phù hợp. Bạn vui lòng cung cấp ngày "
                "giờ muốn xem, họ tên và số điện thoại để tôi đặt lịch giúp bạn."
            )

        return (
            "Thought: Đã hoàn tất các bước tra cứu/đặt lịch cần thiết.\n"
            "Final Answer: [Mock] Đã xử lý xong yêu cầu của bạn, xem chi tiết ở Observation gần nhất."
        )


def get_llm_provider(provider_name: str = None) -> BaseLLMProvider:
    """Factory function tự chọn Provider từ biến môi trường LLM_PROVIDER"""
    name = (provider_name or os.getenv("LLM_PROVIDER") or "mock").lower().strip()
    
    if name == "gemini":
        return GeminiProvider()
    elif name == "openai":
        return OpenAIProvider()
    elif name == "anthropic":
        return AnthropicProvider()
    elif name == "openrouter":
        return OpenRouterProvider()
    else:
        return MockProvider()


if __name__ == "__main__":
    print("=== TEST MULTI-PROVIDER LLM ADAPTER ===")
    provider = get_llm_provider()
    print(f"✅ Provider đang dùng: {provider.__class__.__name__}")
    print(f"🤖 User Query: Hello")
    print(f"💬 Response  : {provider.generate('Hello')}")
