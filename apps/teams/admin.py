from django.contrib import admin

from .models import Team, TeamMember


class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 0
    fields = ["name", "position", "email", "phone_number", "order"]
    ordering = ["order"]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["name"]
    inlines = [TeamMemberInline]


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ["name", "position", "team", "order"]
    list_filter = ["team"]
    search_fields = ["name", "position", "email"]
    ordering = ["team", "order"]
