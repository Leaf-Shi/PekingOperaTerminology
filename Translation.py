import openai
import re

# 设置 OpenAI API 密钥
openai.api_key = 'APIKEY'

def translate_term_with_ranking(term, explanation):
    explanation = explanation[:1000]  # 截取前1000字符，视情况可调整
    prompt = f"""
    这是关于戏曲术语“{term}”及其解释：
    {explanation}
    请根据提供的术语解释，直接提供关于戏曲术语“{term}”的五个不重复的术语潜在的英语翻译。并将这五个潜在的翻译根据可理解性进行排名,将最可理解的术语放在最前面，例如英语术语1是最为可理解的术语翻译
    严格遵循输出格式：{term},英文术语1,英文术语2,英文术语3,英文术语4,英文术语5
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "你是中国传统戏曲领域的专家。"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7
    )
    translations = response['choices'][0]['message']['content'].strip()
    print(f"Translation for {term}: {translations}")  # 调试输出
    return translations

# 逐条读取和处理术语
with open('output_terms.txt', 'r', encoding='utf-8') as infile, open('translations.txt', 'w', encoding='utf-8') as outfile:
    current_term = None
    current_explanation = []
    for line in infile:
        line = line.strip()
        if not line:
            continue
        # 匹配术语开头（以术语名称加冒号为标志）
        if ':' in line and re.match(r'^[^\s:]+:', line):
            if current_term:
                explanation = ' '.join(current_explanation).strip()
                try:
                    translations = translate_term_with_ranking(current_term, explanation)
                    outfile.write(f"{translations}\n")
                except Exception as e:
                    print(f"Error translating term {current_term}: {e}")
                # 清空current_explanation以便处理下一个术语
                current_explanation.clear()
            # 更新当前术语
            parts = line.split(':', 1)
            current_term = parts[0].strip()
            current_explanation = [parts[1].strip()]
        else:
            # 非术语开头的行，继续作为解释的一部分累积
            current_explanation.append(line)
    # 处理最后一个术语和解释
    if current_term:
        explanation = ' '.join(current_explanation).strip()
        try:
            translations = translate_term_with_ranking(current_term, explanation)
            outfile.write(f"{translations}\n")
        except Exception as e:
            print(f"Error translating term {current_term}: {e}")

print("翻译完成并已保存到文件。")
