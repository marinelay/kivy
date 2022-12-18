'''
Graphics tests
==============

Testing the simple vertex instructions
'''

import sys
import pytest
from threading import Thread
from kivy.tests.common import GraphicUnitTest, requires_graphics


class BoxShadowTest(GraphicUnitTest):

    def test_create(self):
        from kivy.graphics.boxshadow import BoxShadow
        from kivy.uix.widget import Widget
        from kivy.graphics import Color

        r = self.render

        # with initial arguments
        wid = Widget()
        with wid.canvas:
            Color(1, 0, 0, 1)
            bs = BoxShadow(
                pos=(50, 50),
                size=(150, 150),
                offset=(0, 10),
                spread_radius=10,
                border_radius=(10, 10, 10, 10),
                blur_radius=80,
            )
        r(wid)

        # changing properties later
        wid = Widget()
        with wid.canvas:
            Color(0, 0, 1, 1)
            bs = BoxShadow()
        bs.pos = [50, 50]
        bs.size = [150, 150]
        bs.offset = [0, 10]
        bs.spread_radius = 10
        bs.border_radius = [10, 10, 10, 10]
        bs.blur_radius = 80
        r(wid)

    def test_adjusted_size(self):
        from kivy.graphics.boxshadow import BoxShadow

        raw_size = 150, 150

        bs = BoxShadow()
        bs.pos = 50, 50
        bs.size = raw_size
        bs.blur_radius = 80
        bs.spread_radius = 10

        # The size of the rectangle containing the FBO texture (shadow) needs
        # to be adjusted according to the size of the shadow, otherwise there
        # will be an unwanted cropping behavior.
        adjusted_size = (
            max(
                0,
                raw_size[0] + bs.blur_radius * 3 + bs.spread_radius * 2,
            ),
            max(
                0,
                raw_size[1] + bs.blur_radius * 3 + bs.spread_radius * 2,
            ),
        )

        assert bs.size == adjusted_size

    def test_adjusted_pos(self):
        from kivy.graphics.boxshadow import BoxShadow

        raw_pos = 50, 50
        raw_size = 150, 150
        offset = 10, -100

        bs = BoxShadow()
        bs.pos = raw_pos
        bs.size = raw_size
        bs.offset = offset
        bs.blur_radius = 80
        bs.spread_radius = 10

        # If the size of the rectangle containing the FBO texture (shadow)
        # changes, its position will need to be adjusted.
        adjusted_pos = (
            raw_pos[0]
            - bs.blur_radius * 1.5
            - bs.spread_radius
            + bs.offset[0],
            raw_pos[0]
            - bs.blur_radius * 1.5
            - bs.spread_radius
            + bs.offset[1],
        )

        assert bs.pos == adjusted_pos


class VertexInstructionTest(GraphicUnitTest):

    def test_circle(self):
        from kivy.uix.widget import Widget
        from kivy.graphics import Ellipse, Color
        r = self.render

        # basic circle
        wid = Widget()
        with wid.canvas:
            Color(1, 1, 1)
            Ellipse(pos=(100, 100), size=(100, 100))
        r(wid)

        # reduced circle
        wid = Widget()
        with wid.canvas:
            Color(1, 1, 1)
            Ellipse(pos=(100, 100), size=(100, 100), segments=10)
        r(wid)

        # moving circle
        wid = Widget()
        with wid.canvas:
            Color(1, 1, 1)
            self.e = Ellipse(pos=(100, 100), size=(100, 100))
        self.e.pos = (10, 10)
        r(wid)

    def test_ellipse(self):
        from kivy.uix.widget import Widget
        from kivy.graphics import Ellipse, Color
        r = self.render

        # ellipse
        wid = Widget()
        with wid.canvas:
            Color(1, 1, 1)
            self.e = Ellipse(pos=(100, 100), size=(200, 100))
        r(wid)

    def test_point(self):
        from kivy.uix.widget import Widget
        from kivy.graphics import Point, Color
        r = self.render

        # 1 point
        wid = Widget()
        with wid.canvas:
            Color(1, 1, 1)
            Point(points=(10, 10))
        r(wid)

        # 25 points
        wid = Widget()
        with wid.canvas:
            Color(1, 1, 1)
            Point(points=[x * 5 for x in range(50)])
        r(wid)

    def test_point_add(self):
        from kivy.uix.widget import Widget
        from kivy.graphics import Point, Color
        r = self.render

        wid = Widget()
        with wid.canvas:
            Color(1, 1, 1)
            p = Point(pointsize=10)

        p.add_point(10, 10)
        p.add_point(90, 10)
        p.add_point(10, 90)
        p.add_point(50, 50)
        p.add_point(10, 50)
        p.add_point(50, 10)

        r(wid)


class FBOInstructionTestCase(GraphicUnitTest):

    def test_fbo_pixels(self):
        from kivy.graphics import Fbo, ClearColor, ClearBuffers, Ellipse

        fbo = Fbo(size=(512, 512))
        with fbo:
            ClearColor(0, 0, 0, 1)
            ClearBuffers()
            Ellipse(pos=(100, 100), size=(100, 100))
        fbo.draw()
        data = fbo.pixels
        fbo.texture.save('results.png')


class TransformationsTestCase(GraphicUnitTest):

    def test_identity_creation(self):
        from kivy.graphics import LoadIdentity
        mat = LoadIdentity()
        self.assertTrue(mat.stack)


class CallbackInstructionTest(GraphicUnitTest):

    def test_from_kv(self):
        from textwrap import dedent
        from kivy.lang import Builder

        root = Builder.load_string(dedent("""\
        Widget:
            canvas:
                Callback:
                    callback: lambda __: setattr(self, 'callback_test', 'TEST')
        """))
        r = self.render
        r(root)
        self.assertTrue(root.callback_test == 'TEST')


@pytest.fixture
def widget_verify_thread(request):
    from kivy.uix.widget import Widget
    from kivy.config import Config

    original = Config.get('graphics', 'verify_gl_main_thread')
    Config.set('graphics', 'verify_gl_main_thread', request.param)

    widget = Widget()
    yield widget, request.param

    Config.set('graphics', 'verify_gl_main_thread', original)


@requires_graphics
@pytest.mark.parametrize('widget_verify_thread', ['0', '1'], indirect=True)
def test_graphics_main_thread(widget_verify_thread):
    from kivy.graphics import Color

    widget, verify_thread = widget_verify_thread
    with widget.canvas:
        color = Color()
    color.rgb = .1, .2, .3


@requires_graphics
@pytest.mark.parametrize('widget_verify_thread', ['0', '1'], indirect=True)
def test_create_graphics_second_thread(widget_verify_thread):
    from kivy.graphics import Color
    widget, verify_thread = widget_verify_thread
    exception = None

    def callback():
        nonlocal exception
        try:
            with widget.canvas:
                if verify_thread == '1':
                    with pytest.raises(TypeError):
                        Color()
                else:
                    Color()
        except BaseException as e:
            exception = e, sys.exc_info()[2]
            raise

    thread = Thread(target=callback)
    thread.start()
    thread.join()
    if exception is not None:
        raise exception[0].with_traceback(exception[1])


@requires_graphics
@pytest.mark.parametrize('widget_verify_thread', ['0', '1'], indirect=True)
def test_change_graphics_second_thread(widget_verify_thread):
    from kivy.graphics import Color
    widget, verify_thread = widget_verify_thread
    with widget.canvas:
        color = Color()

    exception = None

    def callback():
        nonlocal exception
        try:
            if verify_thread == '1':
                with pytest.raises(TypeError):
                    color.rgb = .1, .2, .3
            else:
                color.rgb = .1, .2, .3
        except BaseException as e:
            exception = e, sys.exc_info()[2]
            raise

    thread = Thread(target=callback)
    thread.start()
    thread.join()
    if exception is not None:
        raise exception[0].with_traceback(exception[1])
