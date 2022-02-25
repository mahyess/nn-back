from django.db.models import Count, F, Q, When, Case, Value, IntegerField, ExpressionWrapper
from namastenepal.points.pointSystem import multiplier
from namastenepal.community.models import Community


# + Case(
#     When(priority='lo', then=Value(multiplier('lo'))),
#     # When(total__gt=10, then=Value('C')),
#     # When(total__gt=20, then=Value('D')),
#     default=Value(1),
#     output_field=IntegerField(),
# )


def hot_sort(queryset):
    _qs = queryset.annotate(points=F('community__priority')).annotate(
        hot=((Count('likes') +
              Count('comments')/2) *
             Case(
                 When(points=Community.LOW, then=Value(
                     multiplier(Community.LOW))),
                 When(points=Community.MEDIUM, then=Value(
                     multiplier(Community.MEDIUM))),
                 When(points=Community.HIGH, then=Value(
                     multiplier(Community.HIGH))),
                 When(points=Community.VERY_HIGH, then=Value(
                     multiplier(Community.VERY_HIGH))),
                 When(points=Community.CRITICAL, then=Value(
                     multiplier(Community.CRITICAL))),

                 default=Value(1),
                 output_field=IntegerField())
             )
    ).order_by("-hot")
    return _qs


def trend_sort(queryset):
    return queryset.annotate(
        hot=(Count('likes')+Count('comments')/2)
    ).order_by("-hot")
