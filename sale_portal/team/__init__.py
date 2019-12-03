class TeamType:
    TEAM_SALE = 0
    TEAM_CHAIN = 1
    TEAM_SCC = 2

    CHOICES = [
        (TEAM_SALE, 'Team Sale'),
        (TEAM_CHAIN, 'Team Chuỗi'),
        (TEAM_SCC, 'Team Trực Tiếp')
    ]


class TeamLogType:
    CREATED = 0
    DELETED = 1
    UPDATED = 2

    CHOICES = [
        (CREATED, 'Created new Team'),
        (DELETED, 'Deleted Team'),
        (UPDATED, 'Updated Team')
    ]
