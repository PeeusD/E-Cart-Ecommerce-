from app.models import Cart
# Globally rendering into all templates
def all_cart(request):
    total_item=0
    if request.user.is_authenticated:
        total_item = Cart.objects.filter(user=request.user).count()
        # total_item =len(Cart.objects.filter(user=request.user)) #Alt.
    return {'total_item': total_item}
    

