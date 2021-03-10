from rest_framework import serializers, validators
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .utils import generate_wallet_id
from wallet.models import Wallet, WalletTransaction


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'is_active',)


class WalletSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Wallet
        fields = ('id', 'wallet_id', 'balance', 'user',)


class CreateTransactionSerializer(serializers.Serializer):
    to_wallet_id = serializers.CharField(max_length=16)
    amount = serializers.IntegerField()


class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = '__all__'


class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, write_only=True)
    password1 = serializers.CharField(max_length=200, write_only=True)
    password2 = serializers.CharField(max_length=200, write_only=True)
    token = serializers.CharField(max_length=40, read_only=True)
    wallet = WalletSerializer(read_only=True)

    def validate(self, attrs):
        password1 = attrs.get("password1", None)
        password2 = attrs.get("password2", None)
        username = attrs.get("username")
        if password1 != password2:
            raise validators.ValidationError({"message": "passwords not matched"})
        if User.objects.filter(username=username).count() > 0:
            raise validators.ValidationError({"message": "user already exist"})

        user = User(username=username)
        user.set_password(password1)
        user.save()
        token = Token.objects.create(user=user)
        attrs.update({'token': token.key})
        while True:
            generate_wallet__id = generate_wallet_id()
            if Wallet.objects.filter(wallet_id=generate_wallet__id).count() == 0:
                wallet_instance = Wallet.objects.create(wallet_id=generate_wallet__id, user=user)
                attrs.update({"wallet": WalletSerializer(wallet_instance).data})
                return attrs
