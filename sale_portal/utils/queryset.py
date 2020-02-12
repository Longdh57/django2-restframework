from sale_portal.administrative_unit.models import QrProvince
from sale_portal.shop.models import Shop
from sale_portal.staff import StaffTeamRoleType
from sale_portal.staff.models import Staff
from sale_portal.staff_care import StaffCareType
from sale_portal.staff_care.models import StaffCare
from sale_portal.team.models import Team
from sale_portal.user import ROLE_SALE_MANAGER, ROLE_SALE_ADMIN


def get_provinces_viewable_queryset(user):
    if not user.is_superuser:
        group = user.get_group()
        if group is None or group.status is False:
            return QrProvince.objects.none()
        if group.name == ROLE_SALE_MANAGER or group.name == ROLE_SALE_ADMIN:
            provinces = QrProvince.objects.none()
            for area in user.area_set.all():
                provinces |= area.get_provinces()

            return provinces

        else:
            return QrProvince.objects.none()

    return QrProvince.objects.all()


def get_shops_viewable_queryset(user):
    if not user.is_superuser:
        group = user.get_group()
        if group is None or group.status is False:
            return Shop.objects.none()
        if group.name == ROLE_SALE_MANAGER or group.name == ROLE_SALE_ADMIN:
            provinces = QrProvince.objects.none()
            for area in user.area_set.all():
                provinces |= area.get_provinces()

            return Shop.objects.filter(province__in=provinces)
        else:
            staff = Staff.objects.filter(email=user.email).first()
            if staff and staff.team and staff.role:
                if staff.role.code == StaffTeamRoleType.CHOICES[StaffTeamRoleType.TEAM_MANAGEMENT][1]:
                    staffs = Staff.objects.filter(team_id=staff.team.id)
                    return StaffCare.objects.filter(staff__in=staffs, type=StaffCareType.STAFF_SHOP).values('shop')
                else:
                    return StaffCare.objects.filter(staff=staff, type=StaffCareType.STAFF_SHOP).values('shop')
            else:
                return Shop.objects.none()

    return Shop.objects.all()


def get_staffs_viewable_queryset(user):
    if not user.is_superuser:
        group = user.get_group()
        if group is None or group.status is False:
            return Staff.objects.none()
        if group.name == ROLE_SALE_MANAGER or group.name == ROLE_SALE_ADMIN:
            teams = Team.objects.filter(area__in=user.area_set.all())
            return Staff.objects.filter(team__in=teams)
        else:
            staff = Staff.objects.filter(email=user.email).first()
            if staff and staff.team and staff.role:
                if staff.role.code == StaffTeamRoleType.CHOICES[StaffTeamRoleType.TEAM_MANAGEMENT][1]:
                    return Staff.objects.filter(team_id=staff.team.id)
                else:
                    return Staff.objects.filter(email=user.email)
            else:
                return Staff.objects.none()

    return Staff.objects.all()