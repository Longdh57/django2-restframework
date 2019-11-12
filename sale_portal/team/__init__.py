class TeamLogType:
    CREATED = 0
    DELETED = 1
    UPDATED = 2

    CHOICES = [
        (CREATED, 'Created new Team'),
        (DELETED, 'Deleted Team'),
        (UPDATED, 'Updated Team')
    ]