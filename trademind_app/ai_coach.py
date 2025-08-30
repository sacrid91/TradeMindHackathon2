# trademind_app/ai_coach.py
import os
import requests
import json
from django.conf import settings

# --- CONFIG ---
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_ENDPOINT = "https://api.deepseek.com/v1/chat/completions"

HF_API_KEY = os.getenv('HF_API_KEY')
# HF_MODEL = 
HF_MODEL = "meta-llama/Llama-3.1-8B-Instruct"
HF_ENDPOINT = f"https://huggingface.co/models/{HF_MODEL}"

def get_ai_insight(trade_data):
    """
    Main entry point. Tries Deepseek first, falls back to Hugging Face.
    Returns a dict with:
        - insight
        - risk_pattern
        - discipline_score (1-10)
        - coaching_tip
    """
    
    # Try Deepseek (Commented since it needs payment but it fully works)
    #result = _call_deepseek(trade_data)
    #if result:
    #    return result

    # Fallback to Hugging Face
    result = _call_huggingface(trade_data)
    if result:
        return result

    # Final fallback: mock insight
    return _mock_insight_on_failure(trade_data)

#Works but you have to pay
#def _call_deepseek(trade_data):
#    if not DEEPSEEK_API_KEY:
#        print("[AI Coach] DEEPSEEK_API_KEY not set")
#        return None
#
#    prompt = _build_prompt(trade_data)
#
#    headers = {
#        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
#        "Content-Type": "application/json"
#    }
#
#    payload = {
#        "model": "deepseek-chat",
#        "messages": [
#            {"role": "system", "content": "You are TradeMind AI, a behavioral finance coach for traders. Respond in strict JSON."},
#            {"role": "user", "content": prompt}
#        ],
#        "temperature": 0.6,
#        "max_tokens": 300
#    }
#
#    try:
#        print("[AI Coach] Calling Deepseek API...")
#        response = requests.post(DEEPSEEK_ENDPOINT, headers=headers, json=payload, timeout=10)
#        print(f"[AI Coach] Response status: {response.status_code}")
#        print(f"[AI Coach] Response body: {response.text}")
#        if response.status_code == 200:
#            content = response.json()['choices'][0]['message']['content']
#            return _parse_json_response(content)
#    except Exception as e:
#        print(f"[AI Coach] Deepseek error: {e}")
#    return None

def _call_huggingface(trade_data):
    if not HF_API_KEY:
        print("[AI Coach] HF_API_KEY not set")
        return None

    prompt = _build_prompt(trade_data)

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 300,
            "temperature": 0.6,
            "return_full_text": False
        }
    }

    try:
        print(f"[AI Coach] Calling Hugging Face: {HF_ENDPOINT}")
        response = requests.post(HF_ENDPOINT, headers=headers, json=payload, timeout=10)
        print(f"[AI Coach] Response status: {response.status_code}")
        print(f"[AI Coach] Response body: {response.text}")
        
        if response.status_code == 200:
            content = response.json()[0]['generated_text']
            return _parse_json_response(content)
        elif response.status_code == 503:
            print("[AI Coach] Model is loading, try again in 30-60 seconds.")
        else:
            print(f"[AI Coach connection not reached]: {response.status_code}")
        
    except Exception as e:
        print(f"[AI Coach] Hugging Face error: {e}")
    return None

def _build_prompt(trade_data):
    return f"""
    You are TradeMind AI, a behavioral finance psychologist for traders.
    Analyze this trade and return ONLY valid JSON:

    {{
      "insight": "1 sentence on emotional/behavioral leak",
      "risk_pattern": "1 phrase: e.g., 'Revenge trading', 'FOMO entry'",
      "discipline_score": 1-10,
      "coaching_tip": "1 actionable tip, supportive tone"
    }}

    Trade Details:
    - Entry: {trade_data.get('entry')}
    - Pair: {trade_data.get('pair')}
    - Profit/Loss: {trade_data.get('profit')} / {trade_data.get('loss')}
    - Pre-Trade Emotion: {trade_data.get('pre_trade_emotion')}
    - Post-Trade Emotion: {trade_data.get('post_trade_emotion')}
    - Rules Followed: {trade_data.get('rules_followed_count')}/{trade_data.get('rules_total')}
    - Journal Reason: "{trade_data.get('reason')}"

    Rules:
    - Be clinical, concise, and trader-focused.
    - Use terms: discipline, emotional leakage, risk, edge.
    - No markdown, no extra text.
    - Return ONLY JSON.
    """

def _parse_json_response(raw_content):
    try:
        start = raw_content.find('{')
        end = raw_content.rfind('}') + 1
        if start == -1 or end == 0:
            raise ValueError("No JSON found")
        json_str = raw_content[start:end]
        data = json.loads(json_str)
        required = ['insight', 'risk_pattern', 'discipline_score', 'coaching_tip']
        for key in required:
            if key not in data:
                raise ValueError(f"Missing key: {key}")
        data['discipline_score'] = max(1, min(10, data['discipline_score']))
        return data
    except Exception as e:
        print(f"[AI Coach] Parse error: {e}, Raw: {raw_content}")
        return None

def _mock_insight_on_failure(trade_data):
    # Generate insight based on actual trade data
    pre_emotion = trade_data.get('pre_trade_emotion', 'neutral')
    post_emotion = trade_data.get('post_trade_emotion', 'neutral')
    profit = trade_data.get('profit')
    loss = trade_data.get('loss')
    rules_followed = trade_data.get('rules_followed_count', 0)
    rules_total = max(1,trade_data.get('rules_total', 1)) #Prevent division by zero
    
    # Avoid division by zero
    if rules_total == 0:
        rules_total = 1  # Prevent ZeroDivisionError
        rules_followed = 0  # Ensure ratio is 0

    # Dynamic insight
    if profit:
        insight = f"You maintained discipline with {rules_followed}/{rules_total} rules followed, leading to a profitable trade."
        risk_pattern = "None"
        discipline_score = 7 + (rules_followed / rules_total) * 3  # 7-10
        coaching_tip = "Keep using your checklist to avoid FOMO entries."
    else:
        insight = f"Emotional shift from {pre_emotion} to {post_emotion} suggests impulsive entry."
        risk_pattern = "Revenge trading"
        discipline_score = max(1, 4 - (rules_followed / rules_total) * 3)  # 1-4
        coaching_tip = "Pause for 10 minutes after a loss. Recheck your rules before re-entering."

    return {
        "insight": insight,
        "risk_pattern": risk_pattern,
        "discipline_score": int(discipline_score),
        "coaching_tip": coaching_tip
    }