class ProportionKpiTeamType:
    SIZE_0 = 0
    SIZE_1_2 = 1
    SIZE_3_4 = 2
    SIZE_5_6 = 3
    SIZE_7_8 = 4
    SIZE_9_10 = 5
    SIZE_MORE_THAN_10 = 6

    CHOICES = [
        (SIZE_0, 'Team có 0 nhân viên vs 1 Team Lead'),
        (SIZE_1_2, 'Team có 1-2 nhân viên vs 1 Team Lead'),
        (SIZE_3_4, 'Team có 3-4 nhân viên vs 1 Team Lead'),
        (SIZE_5_6, 'Team có 5-6 nhân viên vs 1 Team Lead'),
        (SIZE_7_8, 'Team có 7-8 nhân viên vs 1 Team Lead'),
        (SIZE_9_10, 'Team có 9-10 nhân viên vs 1 Team Lead'),
        (SIZE_MORE_THAN_10, 'Team có hơn 10 nhân viên vs 1 Team Lead')
    ]
