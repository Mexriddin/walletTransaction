from django.shortcuts import render
from rest_framework import views, response, validators, authentication, permissions
from rest_framework.decorators import APIView
from .models import *
from .serializers import *
# Create your views here.


class WalletView(views.APIView):
    def  get(self, request, wallet_id):
        try:
            queryset = Wallet.objects.get(wallet_id=wallet_id)
            serializer = WalletSerializer(instance=queryset)
            return response.Response(serializer.data)
        except Wallet.DoesNotExist:
            raise validators.ValidationError({'message': 'user not found'})


class TransactionView(views.APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CreateTransactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        from_wallet = Wallet.objects.get(user=request.user)
        to_wallet = Wallet.objects.get(wallet_id=serializer.data.get('to_wallet_id'))
        if from_wallet.wallet_id == to_wallet.wallet_id:
            raise validators.ValidationError({'error': 'don\'t transaction yourself'})
        from_wallet.balance -= serializer.data.get('amount')
        to_wallet.balance += serializer.data.get('amount')
        try:
            from_wallet.save()
            to_wallet.save()
        except Exception as e:
            raise validators.ValidationError({'message': 'min balance 0'})
        wt_transaction = WalletTransaction.objects.create(
            from_wallet=from_wallet,
            to_wallet=to_wallet,
            amount=serializer.data.get('amount')
        )
        transaction_serializers = WalletTransactionSerializer(wt_transaction)

        return response.Response(transaction_serializers.data)


class RegisterView(views.APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response.Response(serializer.data)
