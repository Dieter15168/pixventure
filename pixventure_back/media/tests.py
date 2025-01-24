# test_blur_logic.py

from django.test import TestCase
from unittest.mock import patch
from django.contrib.auth.models import User
from posts.models import Post
from media.models import MediaItem
from taxonomy.models import Category
from media.utils import get_media_file_for_display

class BlurLogicTest(TestCase):
    """
    Tests the blur/paywall logic for both Photos and Videos.
    Ensures the function returns the *full URL* (e.g. '/media/preview.jpg') 
    or an empty string if no file is set.
    """

    def setUp(self):
        # Create paying and non-paying users
        self.user_paying = User.objects.create_user(username='paying_user')
        self.user_non_paying = User.objects.create_user(username='non_paying_user')
        
        # Create a post category
        self.category = Category.objects.create(name='Test category', slug='test-category-slug')

        # Create a post (not blurred by default)
        self.post = Post.objects.create(name='Test Post', is_blurred=False, main_category=self.category)

        # PHOTO item with all file fields
        # We'll assume Django's FileField populates .url with '/media/<filename>'
        self.photo_item = MediaItem.objects.create(
            item_type=MediaItem.PHOTO,
            is_blurred=False,
            watermarked_file='watermarked.jpg',          # => '/media/watermarked.jpg'
            preview_file='preview.jpg',                  # => '/media/preview.jpg'
            thumbnail_file='thumb.jpg',                  # => '/media/thumb.jpg'
            blurred_preview_file='preview_blurred.jpg',  # => '/media/preview_blurred.jpg'
            blurred_thumbnail_file='thumb_blurred.jpg',  # => '/media/thumb_blurred.jpg'
        )

        # VIDEO item with no blurred files
        self.video_item = MediaItem.objects.create(
            item_type=MediaItem.VIDEO,
            is_blurred=False,
            watermarked_file='watermarked_video.mp4',  # => '/media/watermarked_video.mp4'
            preview_file='preview_video.mp4',          # => '/media/preview_video.mp4'
            thumbnail_file='video_thumb.jpg',          # => '/media/video_thumb.jpg'
            blurred_preview_file='',                   # no blurred version
            blurred_thumbnail_file='',                 # no blurred version
        )

    # Helper to unify calling the function
    def _get_url(self, media_item, user, post=None, thumbnail=False):
        return get_media_file_for_display(media_item, user, post=post, thumbnail=thumbnail)

    ### PHOTO TESTS ###

    @patch('media.utils.check_if_user_is_paying', return_value=True)
    def test_photo_nonblurred_paying_post_nonblurred_full(self, mock_check):
        """
        Photo item => paying user => not blurred => full => watermarked_file
        Expect '/media/watermarked.jpg'
        """
        self.post.is_blurred = False
        self.post.save()
        self.photo_item.is_blurred = False
        self.photo_item.save()

        url = self._get_url(self.photo_item, self.user_paying, post=self.post, thumbnail=False)
        self.assertEqual(url, '/media/watermarked.jpg')

    @patch('media.utils.check_if_user_is_paying', return_value=True)
    def test_photo_nonblurred_paying_post_nonblurred_thumb(self, mock_check):
        """
        Photo item => paying user => not blurred => thumbnail => thumbnail_file
        Expect '/media/thumb.jpg'
        """
        self.post.is_blurred = False
        self.post.save()
        self.photo_item.is_blurred = False
        self.photo_item.save()

        url = self._get_url(self.photo_item, self.user_paying, post=self.post, thumbnail=True)
        self.assertEqual(url, '/media/thumb.jpg')

    @patch('media.utils.check_if_user_is_paying', return_value=False)
    def test_photo_blurred_nonpaying_post_blurred_full(self, mock_check):
        """
        Photo item => non-paying => item/post blurred => full => blurred_preview_file
        Expect '/media/preview_blurred.jpg'
        """
        self.post.is_blurred = True
        self.post.save()
        self.photo_item.is_blurred = True
        self.photo_item.save()

        url = self._get_url(self.photo_item, self.user_non_paying, post=self.post, thumbnail=False)
        self.assertEqual(url, '/media/preview_blurred.jpg')

    @patch('media.utils.check_if_user_is_paying', return_value=False)
    def test_photo_blurred_nonpaying_post_blurred_thumb(self, mock_check):
        """
        Photo item => non-paying => item/post blurred => thumbnail => blurred_thumbnail_file
        Expect '/media/thumb_blurred.jpg'
        """
        self.post.is_blurred = True
        self.post.save()
        self.photo_item.is_blurred = True
        self.photo_item.save()

        url = self._get_url(self.photo_item, self.user_non_paying, post=self.post, thumbnail=True)
        self.assertEqual(url, '/media/thumb_blurred.jpg')

    @patch('media.utils.check_if_user_is_paying', return_value=False)
    def test_photo_nonblurred_nonpaying_post_nonblurred_full(self, mock_check):
        """
        Photo => non-paying => post/item not blurred => full => preview_file
        Expect '/media/preview.jpg'
        """
        self.post.is_blurred = False
        self.post.save()
        self.photo_item.is_blurred = False
        self.photo_item.save()

        url = self._get_url(self.photo_item, self.user_non_paying, post=self.post, thumbnail=False)
        self.assertEqual(url, '/media/preview.jpg')

    @patch('media.utils.check_if_user_is_paying', return_value=False)
    def test_photo_nonblurred_nonpaying_post_nonblurred_thumb(self, mock_check):
        """
        Photo => non-paying => post/item not blurred => thumbnail => thumbnail_file
        Expect '/media/thumb.jpg'
        """
        self.post.is_blurred = False
        self.post.save()
        self.photo_item.is_blurred = False
        self.photo_item.save()

        url = self._get_url(self.photo_item, self.user_non_paying, post=self.post, thumbnail=True)
        self.assertEqual(url, '/media/thumb.jpg')
        
    @patch('media.utils.check_if_user_is_paying', return_value=False)
    def test_photo_nonblurred_nonpaying_post_blurred_thumb(self, mock_check):
        """
        Photo => non-paying => post blurred, item not => thumbnail => blurred_thumbnail_file
        Expect '/media/thumb_blurred.jpg'
        """
        self.post.is_blurred = True
        self.post.save()
        self.photo_item.is_blurred = False
        self.photo_item.save()

        url = self._get_url(self.photo_item, self.user_non_paying, post=self.post, thumbnail=True)
        self.assertEqual(url, '/media/thumb_blurred.jpg')
        
    @patch('media.utils.check_if_user_is_paying', return_value=False)
    def test_photo_nonblurred_nonpaying_post_blurred_full(self, mock_check):
        """
        Photo => non-paying => post blurred, item not blurred => full => preview_blurred
        Expect '/media/preview_blurred.jpg'
        """
        self.post.is_blurred = True
        self.post.save()
        self.photo_item.is_blurred = False
        self.photo_item.save()

        url = self._get_url(self.photo_item, self.user_non_paying, post=self.post, thumbnail=False)
        self.assertEqual(url, '/media/preview_blurred.jpg')
        
    @patch('media.utils.check_if_user_is_paying', return_value=False)
    def test_photo_blurred_nonpaying_post_nonblurred_thumb(self, mock_check):
        """
        Photo => non-paying => post non-blurred, item blurred => thumbnail => blurred_thumbnail_file
        Expect '/media/thumb_blurred.jpg'
        """
        self.post.is_blurred = False
        self.post.save()
        self.photo_item.is_blurred = True
        self.photo_item.save()

        url = self._get_url(self.photo_item, self.user_non_paying, post=self.post, thumbnail=True)
        self.assertEqual(url, '/media/thumb_blurred.jpg')
        
    @patch('media.utils.check_if_user_is_paying', return_value=False)
    def test_photo_blurred_nonpaying_post_nonblurred_full(self, mock_check):
        """
        Photo => non-paying => post non-blurred, item blurred => full => preview_blurred
        Expect '/media/preview_blurred.jpg'
        """
        self.post.is_blurred = False
        self.post.save()
        self.photo_item.is_blurred = True
        self.photo_item.save()

        url = self._get_url(self.photo_item, self.user_non_paying, post=self.post, thumbnail=False)
        self.assertEqual(url, '/media/preview_blurred.jpg')

    @patch('media.utils.check_if_user_is_paying', return_value=True)
    def test_photo_nonblurred_paying_post_blurred_thumb(self, mock_check):
        """
        Photo => paying => post blurred, item not => thumbnail => thumb
        Expect '/media/thumb.jpg'
        """
        self.post.is_blurred = True
        self.post.save()
        self.photo_item.is_blurred = False
        self.photo_item.save()

        url = self._get_url(self.photo_item, self.user_non_paying, post=self.post, thumbnail=True)
        self.assertEqual(url, '/media/thumb.jpg')
        
    @patch('media.utils.check_if_user_is_paying', return_value=True)
    def test_photo_nonblurred_paying_post_blurred_full(self, mock_check):
        """
        Photo => paying => post blurred, item not blurred => full => watermarked
        Expect '/media/watermarked.jpg'
        """
        self.post.is_blurred = True
        self.post.save()
        self.photo_item.is_blurred = False
        self.photo_item.save()

        url = self._get_url(self.photo_item, self.user_non_paying, post=self.post, thumbnail=False)
        self.assertEqual(url, '/media/watermarked.jpg')
        
    @patch('media.utils.check_if_user_is_paying', return_value=True)
    def test_photo_blurred_paying_post_nonblurred_thumb(self, mock_check):
        """
        Photo => paying => post non-blurred, item blurred => thumbnail => thumb.jpg
        Expect '/media/thumb.jpg'
        """
        self.post.is_blurred = False
        self.post.save()
        self.photo_item.is_blurred = True
        self.photo_item.save()

        url = self._get_url(self.photo_item, self.user_non_paying, post=self.post, thumbnail=True)
        self.assertEqual(url, '/media/thumb.jpg')
        
    @patch('media.utils.check_if_user_is_paying', return_value=True)
    def test_photo_blurred_paying_post_nonblurred_full(self, mock_check):
        """
        Photo => paying => post non-blurred, item blurred => full => watermarked
        Expect '/media/watermarked.jpg'
        """
        self.post.is_blurred = False
        self.post.save()
        self.photo_item.is_blurred = True
        self.photo_item.save()

        url = self._get_url(self.photo_item, self.user_non_paying, post=self.post, thumbnail=False)
        self.assertEqual(url, '/media/watermarked.jpg')


    ### VIDEO TESTS (no blurred files) ###

    @patch('media.utils.check_if_user_is_paying', return_value=True)
    def test_video_nonblurred_paying_post_nonblurred_full(self, mock_check):
        """
        Video => paying => not blurred => full => watermarked_video.mp4
        """
        self.post.is_blurred = False
        self.post.save()
        self.video_item.is_blurred = False
        self.video_item.save()

        url = self._get_url(self.video_item, self.user_paying, post=self.post, thumbnail=False)
        self.assertEqual(url, '/media/watermarked_video.mp4')

    @patch('media.utils.check_if_user_is_paying', return_value=True)
    def test_video_nonblurred_paying_post_nonblurred_thumb(self, mock_check):
        """
        Video => paying => not blurred => thumbnail => video_thumb.jpg
        """
        self.post.is_blurred = False
        self.post.save()
        self.video_item.is_blurred = False
        self.video_item.save()

        url = self._get_url(self.video_item, self.user_paying, post=self.post, thumbnail=True)
        self.assertEqual(url, '/media/video_thumb.jpg')

    @patch('media.utils.check_if_user_is_paying', return_value=True)
    def test_video_blurred_paying_post_nonblurred_full(self, mock_check):
        """
        Video => paying => item is blurred => still we ignore blur for paying => watermarked_video.mp4
        """
        self.post.is_blurred = False
        self.post.save()
        self.video_item.is_blurred = True
        self.video_item.save()

        url = self._get_url(self.video_item, self.user_paying, post=self.post, thumbnail=False)
        self.assertEqual(url, '/media/watermarked_video.mp4')
        
    @patch('media.utils.check_if_user_is_paying', return_value=True)
    def test_video_nonblurred_paying_post_blurred_full(self, mock_check):
        """
        Video => paying => post is blurred => still we ignore blur for paying => watermarked_video.mp4
        """
        self.post.is_blurred = True
        self.post.save()
        self.video_item.is_blurred = False
        self.video_item.save()

        url = self._get_url(self.video_item, self.user_paying, post=self.post, thumbnail=False)
        self.assertEqual(url, '/media/watermarked_video.mp4')

    @patch('media.utils.check_if_user_is_paying', return_value=False)
    def test_video_blurred_nonpaying_post_blurred_full(self, mock_check):
        """
        Video => non-paying => both post & item blurred => no blurred video file => fallback to preview_video.mp4
        """
        self.post.is_blurred = True
        self.post.save()
        self.video_item.is_blurred = True
        self.video_item.save()

        url = self._get_url(self.video_item, self.user_non_paying, post=self.post, thumbnail=False)
        self.assertEqual(url, '/media/preview_video.mp4')
        
    @patch('media.utils.check_if_user_is_paying', return_value=False)
    def test_video_blurred_nonpaying_post_nonblurred_full(self, mock_check):
        """
        Video => non-paying => video blurred => no blurred video file => fallback to preview_video.mp4
        """
        self.post.is_blurred = False
        self.post.save()
        self.video_item.is_blurred = True
        self.video_item.save()

        url = self._get_url(self.video_item, self.user_non_paying, post=self.post, thumbnail=False)
        self.assertEqual(url, '/media/preview_video.mp4')
        
    @patch('media.utils.check_if_user_is_paying', return_value=False)
    def test_video_nonblurred_nonpaying_post_blurred_full(self, mock_check):
        """
        Video => non-paying => post blurred => no blurred video file => fallback to preview_video.mp4
        """
        self.post.is_blurred = True
        self.post.save()
        self.video_item.is_blurred = False
        self.video_item.save()

        url = self._get_url(self.video_item, self.user_non_paying, post=self.post, thumbnail=False)
        self.assertEqual(url, '/media/preview_video.mp4')
