# TestTaskVK
Тестовое задание на должность Python Developer (Flask) для DIGITAL FUTURE SYSTEMS
Описание в формате Open API: https://app.swaggerhub.com/apis/realalexasha/TestTaskVK/1.0.0
## Настройка и запуск
1. После копирования файлов последовательно запустите в командной строке команды **pipenv install** и **pipenv shell**.
2. Создайте файл найстроек **.env** из шаблона **example.env**. Заполните настройки:
  - **для VK:**
    - CLIENT_ID - ID Вашего приложения в VK.
    - CLIENT_SECRET - защищённый ключ Вашего приложения в VK.
    - REDIRECT_URI - доверенный redirect URI Вашего приложения в VK.
  - **для PostgreSQL:**
    - DB_USER - имя пользователя БД.
    - DB_PASSWORD - пароль пользователя БД.
    - DB_HOST - хост.
    - DB_PORT - порт (по умолчанию 5432)
    - DB_NAME -  имя БД.
 3. Запустите команду **python app.py**.

## Описание
Для авторизации в VK используется метод **Authorization Code Flow**.
При запуске методов, которые требуют авторизации (**search_user_and_friends_groups** и **search_and_write_user_groups**), если токен ещё не получен, то Вы автоматически будете перенаправлены на страницу с предложением авторизоваться в VK.
После авторизации Вам будет доступна ссылка для повторной отправки предыдущего запроса, либо Вы можете отправить любой другой произвольный запрос.
Если Вы планируете отправлять запросы через такие программы тестирования APK как Postman или SouaUI, то для получения токена можете открыть в браузере старницу http://localhost:5000/authorization и подтвердить авторизацию.
После этого приложение получит токен и Вы сможете отправлять запросы.

### Методы
- **search_user_and_friends_groups**
получает группы пользователя и его друзей с возможностью пагинации.
  - параметры:
    - user_id (число, обязательный): ID пользователя VK. Если не заполнен или заполнен не числовыми данными, то сервис вернёт ошибку. Если пользователя с существующим ID не существует, то коллекция **groups** результата будет пустой.
    - query (строка, необязательный): строка поиска, если не задан, то сервис вернёт все группы пользователя и его друзей без фильтрации.
    - per_page (число, необязательный): количество групп на странице, работает только вместе со свойством **page**. Если заданы не числовые данные, то сервис вернёт ошибку. Если **page** или **per_page** не заполнены или заполнены некорректно (равны 0), то будут возвращены все результаты поиска без учета пагинации.
    - page (число, необязательный): номер страницы при разбиении результата на порции по **per_page** элементов, работает только вместе со свойством **per_page**. Если заданы не числовые данные, то сервис вернёт ошибку. Если **page** или **per_page** не заполнены или заполнены некорректно (равны 0), то будут возвращены все результаты поиска без учета пагинации.
  - результат:
    - groups: колеекция групп, каждый элемент которой содержит свойства **id** и **name**.
    - total_results: общее количество групп, соответствующих запросу без учёта пагинации.
    - per_page: значение параметра per_page, если он был использован в запросе.
    - page: значение параметра page, если он был использован в запросе.
   - пример: 
      http://localhost:5000/search_user_and_friends_groups?query=кулинария&user_id=777&page=3per_page=5 вернёт интервал с 11 по 15 групп пользователя id=777 и его друзей, содержащие в названии слово "кулинария".
- **search_and_write_user_groups**
получает группы пользователя и записывает данные в БД.
  - параметры:
    - user_id (число, обязательный): ID пользователя VK. Если не заполнен или заполнен не числовыми данными, то сервис вернёт ошибку. Если пользователя с существующим ID не существует, то коллекция **groups** результата будет пустой.
    - query (строка, необязательный): строка поиска, если не задан, то сервис вернёт все группы пользователя без фильтрации.
    - per_page (число, необязательный): количество групп на странице, работает только вместе со свойством **page**. Если заданы не числовые данные, то сервис вернёт ошибку. Если **page** или **per_page** не заполнены или заполнены некорректно (равны 0), то будут возвращены все результаты поиска без учета пагинации.
    - page (число, необязательный): номер страницы при разбиении результата на порции по **per_page** элементов, работает только вместе со свойством **per_page**. Если заданы не числовые данные, то сервис вернёт ошибку. Если **page** или **per_page** не заполнены или заполнены некорректно (равны 0), то будут возвращены все результаты поиска без учета пагинации.
  Если параметры per_page и page были заполнены частично или некорректно и не использовались в запросе, то они всё равно будут записаны в БД.
  -результат:
    - groups: колеекция групп, каждый элемент которой содержит свойства **id** и **name**.
    - total_results: общее количество групп, соответствующих запросу без учёта пагинации.
    - per_page: значение параметра per_page, если он был использован в запросе.
    - page: значение параметра page, если он был использован в запросе.
   пример: 
      http://localhost:5000/search_and_write_user_groups?query=кулинария&user_id=777&page=3per_page=5 вернёт интервал с 11 по 15 групп пользователя id=777, содержащие в названии слово "кулинария".
- **get_groups_from_db**:
получает все полученные методом **search_and_write_user_groups** группы в хронологической последовательности.
  - параметры:
    - per_page (число, необязательный): количество групп на странице, работает только вместе со свойством **page**. Если заданы не числовые данные, то сервис вернёт ошибку. Если **page** или **per_page** не заполнены или заполнены некорректно (равны 0), то будут возвращены все результаты поиска без учета пагинации.
    - page (число, необязательный): номер страницы при разбиении результата на порции по **per_page** элементов, работает только вместе со ствойством **per_page**. Если заданы не числовые данные, то сервис вернёт ошибку. Если **page** или **per_page** не заполнены или заполнены некорректно (равны 0), то будут возвращены все результаты поиска без учета пагинации.
   - результат:
    - groups: колеекция групп, каждый элемент которой содержит свойства **group** (id группы) и **name** и **created** (дата и время получения данных о группе метдом **search_and_write_user_groups**).
    - total_results: общее количество групп, соответствующих запросу без учёта пагинации.
    - per_page: значение параметра per_page, если он был использован в запросе.
    - page: значение параметра page, если он был использован в запросе.
  - пример: 
      http://localhost:5000/get_groups_from_db?query=кулинария&&page=3per_page=5 вернёт интервал с 11 по 15 групп, полученных ранее методом **search_and_write_user_groups**.
### База данных
Для хранения информации приложение создаёт 4 таблицы:
  - Request: хранит информацию о дате и времени выполнения запросов.
  - Parameter: хранит информацию о параметрах запросов.
  - Group: справочник групп, хранит идентификаторы и наименование.
  - ReceivedGroup: хранит информацию о полученных группах - ссылки на таблицы Request и Group.

### Недостатки и ограничения
Основным недостатком приложения является синхронная работа, а именно последовательная отправка запросов к API VK. На реальном проекте следовало бы обеспечить их конкурентное выполение с помощью asyncio.
Также не учитывается ограничение метода API VK friends.get в 5000 записей.
Возможно, метод **search_user_and_friends_groups** было бы целесообразнее сделать при помощью **exectue**, но я не стал пробовать, так как был ограничен по времени и основой целью этого задания была демонстрация работы с flask и postgree.
