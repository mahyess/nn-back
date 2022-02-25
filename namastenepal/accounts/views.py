import re

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.db.models import Q
from django.dispatch import receiver
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from twilio.rest import Client

from django_rest_passwordreset.signals import reset_password_token_created
from namastenepal.core.models import User, Gender
from namastenepal.points.models import Point
from namastenepal.usermodule.models import Friend, FriendRequest
from namastenepal.usermodule.models import Profile
from .serializers import UserSerializer, UserMiniSerializer
from .tokens import account_activation_token

# Initialize Twilio client
client = Client(username=settings.TWILIO_ACCOUNT_SID,
                password=settings.TWILIO_AUTH_TOKEN)


@api_view(['GET'])
def set_fcm_token(request):
    if request.user.is_authenticated:
        # checkUserPoints(request.user)
        if "fcm_token" in request.GET:
            fcm_token = request.GET.get('fcm_token')
            profile = Profile.objects.get(user=request.user)
            profile.fcm_token = fcm_token
            profile.save()
            return Response({"fcm_token": fcm_token}, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def is_auth(request):
    # t = time.time()
    if request.user.is_authenticated:
        # checkUserPoints(request.user)
        if "fcm_token" in request.GET:
            fcm_token = request.GET.get('fcm_token')
            profile = Profile.objects.get(user=request.user)
            profile.fcm_token = fcm_token
            profile.save()

        now = timezone.now()

        cache.set('user_{}_seen'.format(request.user.username), now)
        serializer = UserSerializer(request.user)
        # print("Woaahh!! My work is finished..")
        # print("I took " + str(time.time() - t))
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({"error": "not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)


# threaded
@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """
    # send an e-mail to the user
    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_password_token': reset_password_token.key
    }

    # render email text
    email_html_message = get_template(
        'email/user_reset_password.html').render(context)
    email_plaintext_message = get_template(
        'email/email_alt.txt').render(context)

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for {title}".format(title="NamasteNepal"),
        # message:
        email_plaintext_message,
        # from:
        settings.DEFAULT_EMAIL,
        # to:
        [reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()


class CreateUser(APIView):
    authentication_classes = ()
    permission_classes = ()

    @staticmethod
    def post(request, *args, **kwargs):
        _data = request.data.copy()
        try:
            with transaction.atomic():
                username = _data.get("username").lower()
                if not username or username == "":
                    return Response(data={"username": "Invalid username."},
                                    status=status.HTTP_400_BAD_REQUEST)
                pattern = '^(?=.{4,18}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$'
                validator = re.findall(pattern, username)
                if not validator:
                    return Response(data={
                        "username": "Username must be 4-18 char long and \
                                    must not contain any special chars or white spaces except _ "},
                        status=status.HTTP_400_BAD_REQUEST)
                if User.objects.filter(username=username).exists():
                    return Response(data={"username": "User already exists."},
                                    status=status.HTTP_400_BAD_REQUEST)

                # Email or phone validate
                v_method = "email"
                email_or_phone = _data.get("email_or_phone")
                email_or_phone = email_or_phone.replace(" ", "")
                if re.search("[@.]", email_or_phone) is None:
                    v_method = "phone_number"
                    email_or_phone = email_or_phone.replace("+", "")
                    if len(str(email_or_phone)) <= 10:
                        return Response(data={"email_or_phone": "You forgot your country code."},
                                        status=status.HTTP_400_BAD_REQUEST)

                    phone_regex = re.compile(r'^(?:\+?44)?[07]\d{9,13}$')
                    if phone_regex.search('0' + email_or_phone) is None:
                        return Response(data={"email_or_phone": "Invalid email/phone."},
                                        status=status.HTTP_400_BAD_REQUEST)
                    else:
                        email_or_phone = "+" + email_or_phone

                if v_method == "email":
                    if User.objects.filter(email=email_or_phone).exists():
                        return Response(data={"email_or_phone": "Email already taken."},
                                        status=status.HTTP_400_BAD_REQUEST)
                else:
                    if User.objects.filter(phone_number=email_or_phone).exists():
                        return Response(data={"email_or_phone": "User with phone number exists."},
                                        status=status.HTTP_400_BAD_REQUEST)

                password = _data.get("password")
                if not password or password == "":
                    return Response(data={"password": "Invalid password"},
                                    status=status.HTTP_400_BAD_REQUEST)
                if len(password) < 8:
                    message = "Make sure your password is at lest 8 letters"
                    return Response(data={"password": message},
                                    status=status.HTTP_400_BAD_REQUEST)
                elif re.search('[0-9]', password) is None:
                    message = "Make sure your password has a number in it"
                    return Response(data={"password": message},
                                    status=status.HTTP_400_BAD_REQUEST)
                # elif re.search('[A-Z]',password) is None:
                #     message = "Make sure your password has a capital letter in it"
                #     return Response(data={"password": message},
                #             status=status.HTTP_400_BAD_REQUEST)

                gender = _data.get("gender")
                if not gender or gender == "":
                    return Response(data={"gender": "gender is required to register a user."},
                                    status=status.HTTP_400_BAD_REQUEST)
                try:
                    _gender = Gender.objects.get(title=gender)
                except Gender.DoesNotExist:
                    if gender.lower() == 'male' or gender.lower() == 'female':
                        _gender = Gender.objects.create(title=gender)
                    else:
                        return Response(data={"gender": "Invalid gender."},
                                        status=status.HTTP_400_BAD_REQUEST)

                first_name = _data.get("first_name")
                last_name = _data.get("last_name")

                if not first_name or first_name == "" and not last_name or last_name == "":
                    return Response(data={"names": "First_name and Last_name are required to register a user."},
                                    status=status.HTTP_400_BAD_REQUEST)

                country = _data.get('country')
                if not country or country == "":
                    return Response(data={"country": "country is required to register a user."},
                                    status=status.HTTP_400_BAD_REQUEST)
                birth_date = _data.get('birth_date')
                if not birth_date or birth_date == "":
                    return Response(data={"birth_date": "birth date is required to register a user."},
                                    status=status.HTTP_400_BAD_REQUEST)

                city = _data.get('city')
                hometown = _data.get('hometown', "")

                if not city or city == "":
                    return Response(data={"city": "city is required to register a user."},
                                    status=status.HTTP_400_BAD_REQUEST)

                user, created = User.objects.get_or_create(
                    username=username, gender=_gender)
                try:
                    current_site = get_current_site(request)
                except Exception as e:  # DjangoSite.DoesNotExist:
                    current_site = type('', (), {})()
                    current_site.domain = "www.namastenepal.com"

                if created:
                    user.set_password(password)
                    user.first_name = first_name
                    user.last_name = last_name
                    if v_method == "email":
                        user.email = email_or_phone
                    else:
                        user.phone_number = email_or_phone

                    user.gender = _gender
                    user.is_active = False

                    user.profile.birthdate = birth_date
                    user.profile.country = country[:2]
                    user.profile.city = city
                    user.profile.hometown = hometown
                    user.profile.save()

                    # send email
                    if v_method == "email":
                        verification_status = send_email(
                            request,
                            current_site,
                            email_or_phone,
                            user,
                            account_activation_token
                        )
                    else:
                        try:
                            verification_status = send_phone_verification(
                                email_or_phone)
                        except Exception as e:
                            print(e)
                            print("helo")
                            User.objects.get(username=username).delete()
                            return Response(
                                data={"email_or_phone": "Please enter your number and country code as instructed."},
                                status=status.HTTP_400_BAD_REQUEST)

                    if not verification_status:
                        User.objects.get(username=username).delete()
                        return Response(data={"email_or_phone": "Verification code was not sent."},
                                        status=status.HTTP_400_BAD_REQUEST)
                    else:
                        user.save()
                        return Response(data={"success": "Verification code sent to user.", "username": str(username),
                                              "email_or_phone": str(email_or_phone), "verification_method": v_method},
                                        status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response(data={"error": "There was some serious error, please check all your data."},
                            status=status.HTTP_400_BAD_REQUEST)


def send_phone_verification(phone_number):
    verification_sid = start_phone_verification(phone_number, channel="sms")

    return not not verification_sid


def start_phone_verification(to, channel):
    if channel not in ('sms', 'voice'):
        channel = 'sms'

    service = settings.VERIFICATION_SID

    verification = client.verify \
        .services(service) \
        .verifications \
        .create(to=to, channel=channel)

    return verification.sid


def send_email(request, current_site, email, user, activation_token):
    try:
        context = {
            'request': request,
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': activation_token.make_token(user),
        }

        email_html_message = get_template(
            'acc_active_email.html').render(context)
        email_plaintext_message = get_template(
            'email/email_alt.txt').render(context)

        msg = EmailMultiAlternatives(
            # title:
            "Activate your {title} Account".format(title="NamasteNepal"),
            # message:
            email_plaintext_message,
            # from:
            settings.DEFAULT_EMAIL,
            # to:
            [email]
        )
        msg.attach_alternative(email_html_message, "text/html")
        msg.send()

        return True
    except Exception as e:
        print(e)
        return False


class RequestPhoneVerify(APIView):
    @staticmethod
    def get(request, phone_number):
        try:
            _phone_number = phone_number.replace(" ", "")
            if "+" not in _phone_number:
                _phone_number = "+" + str(_phone_number)

            send_status = send_phone_verification(_phone_number)
            if send_status:
                return Response({"success": "verification code sent"}, status=status.HTTP_200_OK)
        except Exception as e:
            print('Error', e)
            return Response({"error": "verification code not sent"}, status=status.HTTP_400_BAD_REQUEST)


class PhoneVerify(APIView):
    @staticmethod
    def post(request):
        try:
            code = request.data.get('verification_code')
            phone_number = request.data.get('phone_number')
            phone_number = phone_number.replace(" ", "")
            if "+" not in phone_number:
                phone_number = "+" + str(phone_number)

            user = User.objects.get(uid=request.user.uid)
            service = settings.VERIFICATION_SID
            verification_check = client.verify \
                .services(service) \
                .verification_checks \
                .create(to=phone_number, code=code)
            if verification_check.status == "approved":
                user.phone_number = phone_number
                user.save()
                return Response({"success": "verification succeed", "status": "approved"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "verification failed", "status": "failed"},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({"error": "verification failed", "status": "failed"}, status=status.HTTP_400_BAD_REQUEST)


class PhoneActivationVerify(APIView):
    authentication_classes = ()
    permission_classes = ()

    @staticmethod
    def post(request):
        try:
            code = request.data.get('verification_code')
            phone_number = request.data.get('phone_number')
            if "+" not in phone_number:
                phone_number = "+" + str(phone_number)

            user = User.objects.get(phone_number=phone_number)
            service = settings.VERIFICATION_SID
            verification_check = client.verify \
                .services(service) \
                .verification_checks \
                .create(to=user.phone_number, code=code)
            if verification_check.status == "approved":
                user.is_active = True
                user.save()
                return Response({"success": "verification succeed", "status": "approved"}, status=status.HTTP_200_OK)
            else:
                user.delete()
                return Response({"error": "verification failed please signup again", "status": "failed"},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({"error": "verification failed", "status": "failed"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def change_password(request):
    try:
        with transaction.atomic():
            current_password = request.data.get('current_password')
            if not current_password or current_password == "":
                return Response(data={"password": "Invalid current password"},
                                status=status.HTTP_400_BAD_REQUEST)

            requested_user: User = request.user
            user = User.objects.get(uid=requested_user.uid)
            if not user.check_password(current_password):
                return Response(data={"password": "Invalid current password"},
                                status=status.HTTP_400_BAD_REQUEST)
            password = request.data.get('new_password')
            if not password or password == "":
                return Response(data={"password": "Invalid password"},
                                status=status.HTTP_400_BAD_REQUEST)
            if password == current_password:
                return Response(data={"password": "Please use different password"},
                                status=status.HTTP_400_BAD_REQUEST)

            if len(password) < 8:
                message = "Make sure your password is at lest 8 letters"
                return Response(data={"password": message},
                                status=status.HTTP_400_BAD_REQUEST)
            elif re.search('[0-9]', password) is None:
                message = "Make sure your password has a number in it"
                return Response(data={"password": message},
                                status=status.HTTP_400_BAD_REQUEST)
            elif re.search('[A-Z]', password) is None:
                message = "Make sure your password has a capital letter in it"
                return Response(data={"password": message},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                pass

            password2 = request.data.get('confirm_password')
            if not password == password2:
                return Response(data={"password": "Password didnt matched."},
                                status=status.HTTP_400_BAD_REQUEST)
            user.set_password(password)
            user.save()
            return Response(data={"password": "password changed."},
                            status=status.HTTP_201_CREATED)
    except Exception as e:
        print(e)
        return Response(data={"password": "There was an error."},
                        status=status.HTTP_400_BAD_REQUEST)


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'activated.html')
    else:
        return HttpResponse('Activation link is invalid!')


@api_view(['POST'])
def deactivate_account(request):
    try:
        with transaction.atomic():
            password = request.data.get('password')
            if not password or password == "":
                return Response(data={"password": "password is required"},
                                status=status.HTTP_400_BAD_REQUEST)

            user = authenticate(
                username=request.user.username, password=password)
            if user:
                user.is_active = False
                user.save()
                return Response(data={"password": "account deactivated."},
                                status=status.HTTP_200_OK)
            else:
                return Response(data={"password": "account deactivation failed."},
                                status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        print(e)
        return Response(data={"password": "there was an error."},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def current_user(request):
    """
    Determine the current user by their token, and return their data
    """

    serializer = UserSerializer(request.user)
    return Response(serializer.data)


def check_user_points(user):
    user_point = Point.objects.get(user=user)
    if user_point.total_points <= -100:
        user.is_active = False
        user.save()


class UserList(APIView):

    # permission_classes = (permissions.AllowAny,)

    @staticmethod
    def get(request):
        friends = Friend.objects.filter(
            from_user=request.user).values_list('to_user__id', flat=True)
        friend_requests = FriendRequest.objects.filter(Q(from_user=request.user) | Q(
            to_user=request.user)).values_list('to_user__id', flat=True)

        to_exclude = [*friends, request.user.id, *friend_requests]

        users = User.objects.filter(
            is_superuser=False).exclude(id__in=to_exclude)

        serializer = UserMiniSerializer(users, many=True)
        return Response(serializer.data)
