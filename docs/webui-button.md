# Кнопка в штатном WebUI

На исходном устройстве кнопка **zoid LTE Diagnostics** расположена рядом с Refresh на странице информации об устройстве/системе. Она открывает новую вкладку с `http://192.168.8.1:8080/status.html`.

Файл: `/app/webroot/WebApp/common/html/deviceinformation.html.gz`.

Пользовательский блок сохранён в [`integration/deviceinformation-button.html`](../integration/deviceinformation-button.html). Он использует штатную функцию `create_button` и jQuery. Штатный `deviceinformation.js.gz` при сборе также сохранён локально как справочный материал; дополнительной функции обработчика в нём для этой кнопки нет — обработчик находится непосредственно в HTML.

## Подготовка на компьютере

Скопируйте текущий `deviceinformation.html.gz` с роутера и сохраните резервную копию. Инструмент работает с локальным файлом и создаёт отдельный результат:

```sh
python tools/patch-webui.py deviceinformation.html.gz --output deviceinformation.with-button.html.gz
```

Он ищет ровно одну секцию `create_button(common_refresh,"refresh");` и вставляет архивный блок после её закрывающего `</script>`. При существующей кнопке, неизвестной структуре, совпадении путей или уже существующем output прекращает работу. Исходный файл не перезаписывается.

Распакуйте результат для просмотра, убедитесь в единственности кнопки и сохранности остальных элементов. Передайте подготовленный файл на роутер в `/tmp/deviceinformation.with-button.html.gz`.

## Развёртывание на роутере

После сохранения резервной копии:

```sh
busybox gzip -t /tmp/deviceinformation.with-button.html.gz
```

Только при успешной проверке установите файл с сохранением прав и владельца существующего файла:

```sh
cp /app/webroot/WebApp/common/html/deviceinformation.html.gz /app/webroot/WebApp/common/html/deviceinformation.html.gz.new
cat /tmp/deviceinformation.with-button.html.gz > /app/webroot/WebApp/common/html/deviceinformation.html.gz.new
busybox gzip -t /app/webroot/WebApp/common/html/deviceinformation.html.gz.new
```

Проверьте код выхода последней команды. При `0`:

```sh
mv /app/webroot/WebApp/common/html/deviceinformation.html.gz.new /app/webroot/WebApp/common/html/deviceinformation.html.gz
```

Обновите страницу с очисткой кэша и нажмите кнопку. Наличие кнопки не запускает HTTP-сервер — для него нужен watchdog.

## Удаление или перенос

Для удаления только этого блока подготовьте локальный результат:

```sh
python tools/patch-webui.py deviceinformation.html.gz --remove --output deviceinformation.without-button.html.gz
```

Затем проверьте и установите его тем же способом. Если WebUI отличается, адаптируйте точку вставки вручную; не подменяйте всю страницу файлом от другой версии. При изменении LAN IP нужно согласовать URL в пользовательском блоке и шаблоны поиска инструмента.

При архивировании инструмент проверен локально на копии установленной страницы: удаление, повторное добавление, отказ при дубликате и сохранность содержимого вне добавленного блока. На роутер подготовленный инструментом результат не устанавливался.
