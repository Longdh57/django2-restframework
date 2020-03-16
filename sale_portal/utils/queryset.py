from django.db.models import Q

from sale_portal.shop.models import Shop
from sale_portal.team.models import Team
from sale_portal.user.models import User
from sale_portal.staff.models import Staff
from sale_portal.staff import StaffTeamRoleType
from sale_portal.staff_care import StaffCareType
from sale_portal.staff_care.models import StaffCare
from sale_portal.administrative_unit.models import QrProvince
from sale_portal.user import ROLE_SALE_MANAGER, ROLE_SALE_ADMIN


def get_provinces_viewable_queryset(user):
    if not user.is_superuser:
        group = user.get_group()
        if group is None or group.status is False:
            return QrProvince.objects.none()
        if group.name == ROLE_SALE_MANAGER or group.name == ROLE_SALE_ADMIN:
            # Neu la SM (or SA) cua tripi, teko thi load all province
            if user.is_manager_outside_vnpay:
                return QrProvince.objects.all()
            # Neu la SM (or SA) cua Vnpay thi load provinces theo area
            provinces = QrProvince.objects.none()
            for area in user.area_set.all():
                provinces |= area.get_provinces()
            return provinces

        else:
            return QrProvince.objects.none()

    return QrProvince.objects.all()


def get_staffs_viewable_queryset(user):
    if not user.is_superuser:
        group = user.get_group()
        if group is None or group.status is False:
            return Staff.objects.none()
        if group.name == ROLE_SALE_MANAGER or group.name == ROLE_SALE_ADMIN:
            # Neu la SM (or SA) cua tripi, teko thi load ds team => ds sale
            if user.is_manager_outside_vnpay:
                teams = user.team_set.all()
                return Staff.objects.filter(team__in=teams)
            # Neu la SM (or SA) cua Vnpay thi load ds area => ds team => ds sale
            teams = Team.objects.filter(area__in=user.area_set.all())
            return Staff.objects.filter(team__in=teams)
        else:
            staff = Staff.objects.filter(email=user.email).first()
            if staff and staff.team:
                if staff.role == StaffTeamRoleType.TEAM_MANAGEMENT:
                    return Staff.objects.filter(team_id=staff.team.id)
                else:
                    return Staff.objects.filter(email=user.email)
            else:
                return Staff.objects.none()
    return Staff.objects.all()


def get_teams_viewable_queryset(user):
    if not user.is_superuser:
        group = user.get_group()
        if group is None or group.status is False:
            return Team.objects.none()
        if group.name == ROLE_SALE_MANAGER or group.name == ROLE_SALE_ADMIN:
            # Neu la SM (or SA) cua tripi, teko thi load luon ds team
            if user.is_manager_outside_vnpay:
                return user.team_set.all()
            # Neu la SM (or SA) cua Vnpay thi load ds area => ds team
            return Team.objects.filter(area__in=user.area_set.all())
        else:
            staff = Staff.objects.filter(email=user.email).first()
            if staff and staff.team:
                if staff.role == StaffTeamRoleType.TEAM_MANAGEMENT:
                    return Team.objects.filter(pk=staff.team.id)
                else:
                    return Team.objects.none()
            else:
                return Team.objects.none()

    return Team.objects.all()


def get_shops_viewable_queryset(user):
    if not user.is_superuser:
        group = user.get_group()
        if group is None or group.status is False:
            return Shop.objects.none()
        if group.name == ROLE_SALE_MANAGER or group.name == ROLE_SALE_ADMIN:
            # Neu la SM (or SA) cua tripi, teko thi load ds team => ds sale => ds shop
            if user.is_manager_outside_vnpay:
                staffs = get_staffs_viewable_queryset(user)
                shops = StaffCare.objects.filter(staff__in=staffs, type=StaffCareType.STAFF_SHOP).values('shop')
                return Shop.objects.filter(pk__in=shops)
            # Neu la SM (or SA) cua Vnpay thi load Shop theo provinces lay ra tu area
            provinces = QrProvince.objects.none()
            for area in user.area_set.all():
                provinces |= area.get_provinces()
            return Shop.objects.filter(province__in=provinces)
        else:
            staff = Staff.objects.filter(email=user.email).first()
            if staff and staff.team:
                if staff.role == StaffTeamRoleType.TEAM_MANAGEMENT:
                    staffs = Staff.objects.filter(team_id=staff.team.id)
                    shops = StaffCare.objects.filter(staff__in=staffs, type=StaffCareType.STAFF_SHOP).values('shop')
                else:
                    shops = StaffCare.objects.filter(staff=staff, type=StaffCareType.STAFF_SHOP).values('shop')
                return Shop.objects.filter(pk__in=shops)
            else:
                return Shop.objects.none()

    return Shop.objects.all()


def get_users_viewable_queryset(user):
    if not user.is_superuser:
        staffs_viewable_email = [s.email for s in get_staffs_viewable_queryset(user)]
        user_viewable = User.objects.filter(Q(email__in=staffs_viewable_email) | Q(pk=user.id)).all()
        return user_viewable
    return User.objects.all()
