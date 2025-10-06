
from rest_framework_simplejwt.tokens import RefreshToken

def generate_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    
    refresh['user_id'] = str(user.id)
    refresh['email'] = user.email
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }