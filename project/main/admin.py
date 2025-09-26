from django.contrib import admin
from .models import Course, Video
from django.utils.html import format_html
from django import forms

class VideoInline(admin.StackedInline):
    model = Video
    extra = 1
    fields = ['title', 'file', 'duration']
    show_change_link = True

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'description']
    search_fields = ['title', 'description']
    list_per_page = 20
    ordering = ['title']
    inlines = [VideoInline]

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = '__all__'

    def clean_file(self):
        file = self.cleaned_data.get('file', False)
        if file:
            if file.size > 500 * 1024 * 1024:  # 500MB лимит
                raise forms.ValidationError("Видео слишком большое (макс 500MB)")
        return file

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    form = VideoForm
    list_display = ['title', 'course', 'duration', 'video_preview']
    list_filter = ['course']
    search_fields = ['title']

    def video_preview(self, obj):
        if obj.file:
            return format_html(
                '<video width="200" controls>'
                '<source src="{}" type="video/mp4">'
                'Ваш браузер не поддерживает видео.'
                '</video>',
                obj.file.url
            )
        return "-"
    video_preview.short_description = "Предпросмотр"
