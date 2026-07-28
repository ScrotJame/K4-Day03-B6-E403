"""
🚀 CORE AGENT APP (Dành cho Role 4: Core Agent Developer)
File chính ghép nối tất cả các thành phần: Tools + Prompts + Test Cases + Multi-Provider.
Đề tài 10: Trợ lý tìm nhà trọ/căn hộ và đặt lịch xem nhà.
"""

import json
import os
import re
import sys
import time
from dotenv import load_dotenv

# Đảm bảo import các module cùng thư mục src/ hoạt động mượt mà
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Import các thành phần từ file của Role 2, Role 3 & Multi-Provider Adapter
from tools import AVAILABLE_TOOLS
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider

load_dotenv()

# Nhận diện dòng "Action: tool_name[arg1, arg2, ...]" và "Final Answer: ..." trong output LLM
ACTION_RE = re.compile(r"Action:\s*(\w+)\s*\[([^\]]*)\]", re.IGNORECASE)
FINAL_ANSWER_RE = re.compile(r"Final Answer:\s*(.+)", re.IGNORECASE | re.DOTALL)

# Gói Free Tier của một số Provider (vd Gemini) giới hạn ~5 request/phút/model.
# Giãn cách + retry nhẹ để không bị 429 khi chạy hết bộ Test Cases liên tiếp.
LLM_CALL_DELAY_SECONDS = 13
RATE_LIMIT_MARKERS = ("RESOURCE_EXHAUSTED", "429")


def _safe_generate(provider, prompt: str, system_prompt: str) -> str:
    """Gọi provider.generate() có giãn cách và retry khi bị rate limit (429).
    Bỏ qua giãn cách với MockProvider vì chạy offline, không có rate limit thật.
    """
    if provider.__class__.__name__ != "MockProvider":
        time.sleep(LLM_CALL_DELAY_SECONDS)
    response = provider.generate(prompt, system_prompt=system_prompt)
    if any(marker in response for marker in RATE_LIMIT_MARKERS):
        print("⏳ Provider báo rate limit, chờ 20s rồi thử lại 1 lần...")
        time.sleep(20)
        response = provider.generate(prompt, system_prompt=system_prompt)
    return response


def load_test_cases():
    """Đọc bộ test cases từ config/test_cases.json của Role 1"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")

    # Fallback kiểm tra nếu file ở thư mục hiện tại
    if not os.path.exists(config_path):
        config_path = "test_cases.json"

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_baseline_chatbot(user_query: str, provider):
    """
    Dựng Chatbot gốc (Baseline) không có công cụ.
    """
    print(f"\n💬 [CHATBOT BASELINE] Câu hỏi: {user_query}")

    # Gọi LLM Provider thực hiện sinh câu trả lời (1 lần gọi duy nhất, không tool)
    response = _safe_generate(provider, user_query, CHATBOT_BASELINE_PROMPT)
    print(f"🤖 Chatbot trả lời:\n{response}")
    return response


def _parse_tool_args(raw_args: str) -> list:
    """Tách chuỗi tham số trong Action[...] thành list Python, tự nhận diện số nguyên."""
    args = []
    for part in raw_args.split(","):
        cleaned = part.strip().strip("'").strip('"').strip()
        if not cleaned:
            continue
        if re.fullmatch(r"-?\d+", cleaned):
            args.append(int(cleaned))
        else:
            args.append(cleaned)
    return args


def _execute_tool(tool_name: str, raw_args: str) -> str:
    """Thực thi tool thật từ AVAILABLE_TOOLS. Luôn trả về string, không bao giờ crash."""
    if tool_name not in AVAILABLE_TOOLS:
        valid = ", ".join(AVAILABLE_TOOLS.keys())
        return f"LỖI: Tool '{tool_name}' không tồn tại. Các tool hợp lệ: [{valid}]."

    args = _parse_tool_args(raw_args)
    try:
        return AVAILABLE_TOOLS[tool_name](*args)
    except TypeError as e:
        return f"LỖI: Tham số truyền cho tool '{tool_name}' không hợp lệ ({e})."
    except Exception as e:
        return f"LỖI: Tool '{tool_name}' gặp sự cố khi thực thi ({e})."


def run_react_agent(user_query: str, provider):
    """
    Vòng lặp ReAct Agent thật: gọi LLM sinh Thought -> Action, thực thi Tool thật qua
    AVAILABLE_TOOLS, nối Observation vào ngữ cảnh cho bước suy luận tiếp theo.
    Có Guardrails: giới hạn MAX_ITERATIONS, chặn lặp lại y hệt 1 Action, chặn LLM tự bịa
    Observation trong cùng một lượt sinh.
    """
    print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")

    scratchpad = f"Câu hỏi của người dùng: {user_query}\n"
    last_action_signature = None
    last_observation = None
    step = 0
    completed = False
    final_answer = None

    while step < MAX_ITERATIONS:
        step += 1
        print(f"\n--- 🔄 Vòng lặp ReAct (Step {step}/{MAX_ITERATIONS}) ---")

        raw_output = _safe_generate(provider, scratchpad, REACT_SYSTEM_PROMPT)

        # Guardrail: cắt bỏ nếu LLM tự sinh thêm "Observation:"/bước tiếp theo trong
        # cùng một lượt trả lời, tránh việc nó tự bịa kết quả tool.
        llm_output = raw_output.split("Observation:")[0].strip()
        print(llm_output)
        scratchpad += llm_output + "\n"

        final_match = FINAL_ANSWER_RE.search(llm_output)
        if final_match:
            final_answer = final_match.group(1).strip()
            completed = True
            break

        action_match = ACTION_RE.search(llm_output)
        if not action_match:
            correction = (
                "Observation: LỖI: Định dạng phản hồi không hợp lệ. Vui lòng trả lời "
                "đúng theo mẫu 'Thought: ...' rồi 'Action: tool[tham_số]', hoặc "
                "'Thought: ...' rồi 'Final Answer: ...'."
            )
            print(f"👁️ {correction}")
            scratchpad += correction + "\n"
            continue

        tool_name, raw_args = action_match.group(1), action_match.group(2)
        action_signature = f"{tool_name}[{raw_args}]"

        if action_signature == last_action_signature:
            correction = (
                "Observation: LỖI: Bạn vừa lặp lại chính xác Action này. Hãy thử tham "
                "số khác hoặc trả lời Final Answer với thông tin đang có."
            )
            print(f"👁️ {correction}")
            scratchpad += correction + "\n"
            continue
        last_action_signature = action_signature

        obs = _execute_tool(tool_name, raw_args)
        print(f"👁️ Observation: {obs}")
        scratchpad += f"Observation: {obs}\n"
        last_observation = obs

    if not completed:
        is_last_step_success = bool(last_observation) and not last_observation.startswith(
            ("LỖI:", "KHÔNG TÌM THẤY:")
        )
        if is_last_step_success:
            # Agent đã thực thi đúng tool và có kết quả tốt, chỉ là hết lượt trước khi
            # kịp phát biểu Final Answer -> dùng thẳng Observation cuối, không bịa ra
            # một câu "xin lỗi" mâu thuẫn với kết quả đã đạt được.
            final_answer = (
                "Đã đạt giới hạn số bước xử lý trước khi kịp tổng hợp câu trả lời cuối, "
                f"nhưng đây là kết quả mới nhất tôi thu thập được:\n{last_observation}"
            )
        else:
            final_answer = (
                f"Xin lỗi, tôi chưa thể hoàn tất yêu cầu này trong {MAX_ITERATIONS} bước xử lý. "
                "Bạn vui lòng cung cấp thêm thông tin hoặc thử lại với yêu cầu rõ ràng hơn."
            )
        print(
            f"🛡️ GUARDRAIL TRIGGERED: Đã đạt giới hạn tối đa {MAX_ITERATIONS} bước. "
            f"Ngắt lặp an toàn!\n🏁 Final Answer (fallback): {final_answer}"
        )

    return final_answer


if __name__ == "__main__":
    print("==================================================")
    print("🏫 ĐẠI HỌC VINUNI - BÀI LAB 3: CHATBOT VS REACT AGENT")
    print("==================================================")

    # Khởi tạo Multi-Provider LLM Adapter (Đọc từ biến môi trường LLM_PROVIDER)
    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Offline Mock Mode")
    print(f"🔌 LLM Provider đang hoạt động: {provider.__class__.__name__} (Model: {model_name})")

    tests = load_test_cases()
    print(f"✅ Đã tải thành công {len(tests)} Test Cases từ config/test_cases.json")

    for test in tests:
        print("\n" + "=" * 70)
        print(f"📋 TEST CASE #{test['id']} — {test['category']}")
        print("=" * 70)

        print("\n--- CHẠY TRÊN CHATBOT BASELINE ---")
        run_baseline_chatbot(test["question"], provider)

        print("\n--- CHẠY TRÊN REACT AGENT ---")
        run_react_agent(test["question"], provider)
