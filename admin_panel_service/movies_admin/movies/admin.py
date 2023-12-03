from django.contrib import admin

from .models import Person, Genre, Filmwork, GenreFilmwork, PersonFilmwork


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'created',
        'modified',
    )

    search_fields = ('full_name', 'id', )


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'description',
        'created',
        'modified',
    )

    search_fields = ('name', 'description', 'id', )


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (
        GenreFilmworkInline,
        PersonFilmworkInline,
    )

    list_display = (
        'title',
        'type',
        'file_path',
        'creation_date',
        'rating',
        'created',
        'modified',
    )

    list_filter = ('type', )
    search_fields = ('title', 'description', 'id', )
