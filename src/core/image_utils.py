from PIL import Image
import io, base64
from src.config import MAX_IMAGE_SIZE

def compress_image_to_base64(image_path):
    """
    打开图像文件，将其压缩（最长边不超过 MAX_IMAGE_SIZE 像素），
    转换为 WebP 格式并编码为 base64 字符串，返回用于 API 请求的 data URI。
    """
    with Image.open(image_path) as img:
        # 获取原始尺寸
        width, height = img.size
        # 如尺寸超出限制，按比例缩放图像
        if max(width, height) > MAX_IMAGE_SIZE:
            if width >= height:
                new_width = MAX_IMAGE_SIZE
                new_height = int(MAX_IMAGE_SIZE * height / width)
            else:
                new_height = MAX_IMAGE_SIZE
                new_width = int(MAX_IMAGE_SIZE * width / height)
            img = img.resize((new_width, new_height), Image.LANCZOS)
        # 将图像转换为 WebP 格式并写入字节流:contentReference[oaicite:11]{index=11}:contentReference[oaicite:12]{index=12}
        byte_stream = io.BytesIO()
        img.save(byte_stream, format='WEBP')
        img_bytes = byte_stream.getvalue()
        # 编码为 base64 字符串
        base64_str = base64.b64encode(img_bytes).decode('utf-8')
        # 构造 data URI 字符串（使用 image/webp 格式）并返回:contentReference[oaicite:13]{index=13}
        data_uri = f"data:image/webp;base64,{base64_str}"
        return data_uri
