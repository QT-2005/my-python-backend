"""
Email service - gửi email qua SMTP bất đồng bộ (aiosmtplib).
Dùng cho forgot-password và các notification khác sau này.
"""
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_email(
    to: str,
    subject: str,
    html_body: str,
    plain_body: str | None = None,
) -> bool:
    """
    Gửi email bất đồng bộ qua SMTP.
    Trả về True nếu thành công, False nếu thất bại (không raise exception
    để tránh lộ thông tin server cho client).
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to

    if plain_body:
        msg.attach(MIMEText(plain_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True,          # STARTTLS (port 587)
        )
        logger.info("Email sent to %s — subject: %s", to, subject)
        return True
    except Exception as exc:
        logger.error("Failed to send email to %s: %s", to, exc)
        return False


async def send_reset_password_email(to: str, token: str, reset_base_url: str) -> bool:
    """
    Gửi email chứa link đặt lại mật khẩu.

    Args:
        to: địa chỉ email người nhận
        token: reset token đã tạo
        reset_base_url: URL frontend, ví dụ "https://app.lexirise.com/reset-password"
    """
    reset_link = f"{reset_base_url}?token={token}"

    subject = "Đặt lại mật khẩu LexiRise"

    plain_body = (
        f"Xin chào,\n\n"
        f"Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản của bạn.\n"
        f"Truy cập link sau để đặt lại mật khẩu (có hiệu lực trong 1 giờ):\n\n"
        f"{reset_link}\n\n"
        f"Nếu bạn không yêu cầu, hãy bỏ qua email này.\n\n"
        f"Trân trọng,\nĐội ngũ LexiRise"
    )

    html_body = f"""<!DOCTYPE html>
<html lang="vi">
<head><meta charset="UTF-8"></head>
<body style="font-family:Arial,sans-serif;background:#f5f5f5;margin:0;padding:0">
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td align="center" style="padding:40px 0">
        <table width="560" cellpadding="0" cellspacing="0"
               style="background:#fff;border-radius:8px;padding:40px;box-shadow:0 2px 8px rgba(0,0,0,.08)">
          <tr>
            <td>
              <h2 style="color:#1a1a1a;margin:0 0 16px">Đặt lại mật khẩu</h2>
              <p style="color:#555;line-height:1.6">
                Xin chào,<br><br>
                Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản <strong>{to}</strong>.
                Nhấn vào nút bên dưới để tiếp tục (link có hiệu lực trong <strong>1 giờ</strong>).
              </p>
              <div style="text-align:center;margin:32px 0">
                <a href="{reset_link}"
                   style="background:#4f46e5;color:#fff;text-decoration:none;
                          padding:14px 32px;border-radius:6px;font-size:16px;font-weight:600">
                  Đặt lại mật khẩu
                </a>
              </div>
              <p style="color:#888;font-size:13px;line-height:1.6">
                Hoặc copy link sau vào trình duyệt:<br>
                <a href="{reset_link}" style="color:#4f46e5;word-break:break-all">{reset_link}</a>
              </p>
              <hr style="border:none;border-top:1px solid #eee;margin:24px 0">
              <p style="color:#aaa;font-size:12px">
                Nếu bạn không yêu cầu đặt lại mật khẩu, hãy bỏ qua email này. 
                Tài khoản của bạn vẫn an toàn.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    return await send_email(to, subject, html_body, plain_body)
