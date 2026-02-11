from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
import os
import io


from models.models import Phone_data, Channel_Data

from service_parsing.parsing import phone_register_send, login_with_cookies, parse_channel_data_optimized

from auth.auth_deps import security


parsing_router = APIRouter()


@parsing_router.post('/phone_auth', dependencies=[Depends(security.access_token_required)], tags=['Парсинг'])
def phone_register(phone_num: Phone_data, background_tasks: BackgroundTasks):
    background_tasks.add_task(phone_register_send, phone_num.phone,)
    return {'message': f'Подтверждение отправлено в тг с номером {phone_num.phone}'}


@parsing_router.post('/sign_in', dependencies=[Depends(security.access_token_required)], tags=['Парсинг'])
def sign_in_with_cookie(phone_num: Phone_data):
    driver = login_with_cookies()
    if not driver:
        return {'message': 'Ошибка входа. Нужна авторизация.'}

    return {'message': f'Успешный вход через куки! {phone_num.phone}'}


@parsing_router.post('/univers_parsing', dependencies=[Depends(security.access_token_required)], tags=['Парсинг'])
def choose_channel(channel_data: Channel_Data):
    driver = login_with_cookies()

    if not driver:
        return {'message': 'Ошибка входа.'}

    try:
        # Используем оптимизированную функцию для парсинга
        result = parse_channel_data_optimized(
            driver, channel_data.channel_name, save_excel=True)

        # Если есть Excel файл, отправляем его и удаляем
        if 'excel_file' in result and result['excel_file']:
            excel_file_path = result['excel_file']

            # Проверяем, что файл существует
            if os.path.exists(excel_file_path):
                # Читаем файл в память
                with open(excel_file_path, 'rb') as f:
                    file_content = f.read()

                # Удаляем файл с диска
                os.remove(excel_file_path)

                # Очищаем название файла от кириллицы для HTTP заголовка
                import re
                import urllib.parse
                safe_filename = re.sub(r'[^\w\s\-_\.]', '', excel_file_path)
                safe_filename = safe_filename.replace(' ', '_')

                # URL-кодируем имя файла для безопасной передачи
                encoded_filename = urllib.parse.quote(
                    safe_filename.encode('utf-8'))

                # Возвращаем файл как поток
                return StreamingResponse(
                    io.BytesIO(file_content),
                    media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    headers={
                        'Content-Disposition': f'attachment; filename*=UTF-8\'\'{encoded_filename}'
                    }
                )
            else:
                return {'error': 'Excel файл не найден'}
        else:
            return result

    except Exception as e:
        return {'error': f'Ошибка: {e}'}
    finally:
        driver.quit()
        
@parsing_router.delete('/delete_cookies', dependencies=[Depends(security.access_token_required)], tags=['Парсинг'])
def delete_cookies():
    try:
        COOKIES_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cookies_user.pkl")
        if not os.path.exists(COOKIES_FILE):
            return {"message": "Файл cookies не найден", "deleted": False}
        os.remove(COOKIES_FILE)
        return {"message": "Cookies удалены", "deleted": True}
    except OSError as e:
        return {"message": f"Ошибка при удалении: {e}", "deleted": False}