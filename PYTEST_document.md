## Guide to use pytest to test Sale Portal Backend V2

### Setup
Setting path to connect DB in .env  
- TEST_DB_NAME = sp_pytest
- TEST_DB_USER = sp_user
- TEST_DB_PASSWORD = secret123
- TEST_DB_HOST = localhost
- TEST_DB_PORT = 5432

### Folder Setting
Put file pytest.ini in root folder  
Put file settings for pytest in **sale_portal/test_settings.py**  
In each django app, delete file **tests.py**, create new folder by follow this structure    
```tests```  
&nbsp;&nbsp;&nbsp;```|- __init__.py```  
&nbsp;&nbsp;&nbsp;```|- conftest.py```  
&nbsp;&nbsp;&nbsp;```|- tests.py```

### Testing with an exists DB
Add ```@pytest.mark.django_db``` before start a **class**  
```
import pytest
from mixer.backend.django import mixer

from sale_portal.team.models import Team

pytestmark = pytest.mark.django_db


@pytest.mark.django_db
class TestClass:
    pytestmark = pytest.mark.django_db

    def test_create_team(self):
        team = mixer.blend(Team, name='Team Ha Noi', code='HN1')
        assert team.type == 0
```

### Run pytest
Test all project - run command in terminal
```
pytest
```
Test by select a test file:
```
pytest path_to_test_file    # Example: pytest sale_portal/team/tests/tests.py
```