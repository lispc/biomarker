import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


def create_openai_client() -> OpenAI:
    """创建 OpenAI 客户端"""
    api_key = os.getenv("MOONSHOT_API_KEY")
    if not api_key:
        raise ValueError("MOONSHOT_API_KEY not found in .env file")
    return OpenAI(
        api_key=api_key,
        base_url="https://api.moonshot.cn/v1",
    )


def query_biomarker(index: int, name_en: str, name_cn: str, category: str, output_dir: str = "assets") -> str:
    """
    查询单个生物标志物，生成说明文档并保存为 markdown 文件。
    
    Args:
        index: 行号（从1开始计数），用于生成文件名前缀
        name_en: 生物标志物英文名
        name_cn: 生物标志物中文名
        category: 分类名（CSV第一列）
        output_dir: 输出目录，默认为 "assets"
    
    Returns:
        生成的文件路径
    """
    import os
    
    client = create_openai_client()
    
    # 构建查询文本，同时使用英文名和中文名
    text = f"介绍一下 '{name_en}'（{name_cn}）这个体检指标的涵义，以及常见的异常，异常对应的可能原因，异常对应的建议后续处理（如调整生活方式，进一步详细检查等）。使用 markdown 输出"
    
    # 构建文件名：003|英文名|中文名.md
    # 清理文件名中的非法字符
    safe_name_en = name_en.replace("/", "-").replace("\\", "-").replace("|", "-")
    safe_name_cn = name_cn.replace("/", "-").replace("\\", "-").replace("|", "-")
    filename = f"{index:03d}|{safe_name_en}|{safe_name_cn}.md"
    
    # 构建路径：assets/$(分类名)/$(文件名)
    # 清理分类名中的非法字符
    safe_category = category.replace("/", "-").replace("\\", "-").strip()
    category_dir = os.path.join(output_dir, safe_category)
    os.makedirs(category_dir, exist_ok=True)
    filepath = os.path.join(category_dir, filename)
    
    stream = client.chat.completions.create(
        model="kimi-k2.5",
        messages=[
            {"role": "system", "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。"},
            {"role": "user", "content": text}
        ],
        temperature=1,
        max_tokens=32000,
        stream=True,
    )
    
    with open(filepath, "w") as w:
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                w.write(delta.content)
                print(delta.content, end="")
    
    return filepath


if __name__ == "__main__":
    # 保持向后兼容，可以直接运行
    name = "尿白蛋白/肌酐比值"
    query_biomarker(index=1, name_en=name, name_cn=name, category="Kidney Health", output_dir="assets")
