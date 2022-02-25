from graphene_django import DjangoObjectType
import graphene
from namastenepal.core.models import User
from namastenepal.community.models import CommunityPost, Community, Comments


class UserSchema(DjangoObjectType):

    class Meta:
        model = User
        exclude = ['password']


class CommunitySchema(DjangoObjectType):

    class Meta:
        model = Community


class PostSchema(DjangoObjectType):

    class Meta:
        model = CommunityPost


class CommentSchema(DjangoObjectType):

    class Meta:
        model = Comments


class Query(graphene.ObjectType):
    users = graphene.List(UserSchema)
    communities = graphene.List(CommunitySchema)
    posts = graphene.List(PostSchema)
    comments = graphene.List(CommentSchema)

    def resolve_users(self, info):
        return User.objects.all()

    def resolve_communities(self, info):
        return Community.objects.all()

    def resolve_posts(self, info):
        return CommunityPost.objects.all()

    def resolve_comments(self, info):
        return Comments.objects.all()


schema = graphene.Schema(query=Query)
