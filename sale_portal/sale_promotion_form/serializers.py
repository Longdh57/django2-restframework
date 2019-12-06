from rest_framework import serializers
from .models import SalePromotion


class SalePromotionSerializer(serializers.ModelSerializer):
    terminal = serializers.SerializerMethodField()
    merchant = serializers.SerializerMethodField()
    shop = serializers.SerializerMethodField()
    staff = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    def get_terminal(self, sale_promotion):
        return sale_promotion.get_terminal()

    def get_merchant(self, sale_promotion):
        return sale_promotion.get_merchant()

    def get_shop(self, sale_promotion):
        return sale_promotion.get_shop()

    def get_staff(self, sale_promotion):
        return sale_promotion.get_staff()

    def get_title(self, sale_promotion):
        return sale_promotion.get_title()

    def get_status(self, sale_promotion):
        return sale_promotion.get_status()

    class Meta:
        model = SalePromotion
        fields = (
            'id', 'terminal', 'merchant', 'shop', 'staff', 'title', 'contact_person', 'contact_phone_number',
            'contact_email', 'tentcard_ctkm', 'wobbler_ctkm', 'status', 'image', 'sub_image',
            'created_date', 'updated_date'
        )
